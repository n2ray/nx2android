"""Exercise the actual occlusion snapshot lifetime independently of Vulkan."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class OcclusionSnapshots(unittest.TestCase):
    def test_completed_queries_batch_and_fallback(self):
        cc = shutil.which('cc') or shutil.which('clang')
        if not cc:
            self.skipTest('C compiler not available')
        source = (Path(__file__).resolve().parents[1] / 'nxnative/dm/android/gfx_vk_core.c').read_text()
        start = source.index('static void occ_complete(')
        end = source.index('\nenum { GW_SUB', start)
        code = r'''#include <stdint.h>
#include <stdlib.h>
#include <assert.h>
#define OCC_MAX 1024
#define VK_QUERY_RESULT_64_BIT 1
#define VK_SUCCESS 0
typedef struct { uint64_t value; int refs; } occ_segment;
typedef struct { occ_segment *occ[OCC_MAX]; unsigned nocc; } vksub_t;
static void occ_release(occ_segment *s) { s->refs--; }
static struct { int dev; } V; static int g_oq, calls, fail_batch;
static int vkGetQueryPoolResults(int d, int p, uint32_t first, uint32_t n, size_t size, void *data, size_t stride, int flags) {
    (void)d; (void)p; (void)size; (void)stride; (void)flags; calls++;
    if (fail_batch && n > 1) return 1;
    for (uint32_t i = 0; i < n; i++) ((uint64_t *)data)[i] = first + i;
    return 0;
}
''' + source[start:end] + r'''
int main(void) {
    occ_segment a = {42, 1}, b = {42, 1}; vksub_t s = {.occ = {&a, &b}, .nocc = 2};
    occ_complete(&s, 1, 1); assert(calls == 1 && a.value == OCC_MAX && b.value == OCC_MAX + 1 && !a.refs && !b.refs);
    a.refs = b.refs = 1; calls = 0; fail_batch = 1; occ_complete(&s, 2, 1);
    assert(calls == 3 && a.value == OCC_MAX * 2 && b.value == OCC_MAX * 2 + 1);
    a.value = b.value = 42; a.refs = b.refs = 1; calls = 0; occ_complete(&s, 0, 0);
    assert(!calls && a.value == 42 && b.value == 42 && !a.refs && !b.refs);
    return 0;
}
'''
        with tempfile.TemporaryDirectory() as tmp:
            src, exe = Path(tmp) / 'test.c', Path(tmp) / 'test'
            src.write_text(code)
            subprocess.run([cc, '-std=c11', '-Wall', '-Wextra', '-Werror', str(src), '-o', str(exe)], check=True)
            subprocess.run([str(exe)], check=True)

    def test_snapshots_survive_reset_and_later_results(self):
        cc = shutil.which('cc') or shutil.which('clang')
        if not cc:
            self.skipTest('C compiler not available')
        source = (Path(__file__).resolve().parents[1] / 'nxnative/dm/android/gfx_vk_core.c').read_text()
        start = source.index('enum { OCC_MAX =')
        end = source.index('#define SCRATCH_BLOCK', start)
        code = '#include <stdint.h>\n#include <stdlib.h>\n#include <stdatomic.h>\n#include <assert.h>\ntypedef void *VkQueryPool;\n' + source[start:end] + r'''
static occ_segment *append(uint64_t value) {
    occ_segment *s = malloc(sizeof *s); assert(s); atomic_init(&s->refs, 2); s->value = value;
    g_occ_list = realloc(g_occ_list, (g_occ_n + 1) * sizeof *g_occ_list); assert(g_occ_list);
    g_occ_list[g_occ_n++] = s; return s;
}
int main(void) {
    assert(occ_snapshot_finish(occ_snapshot_make()) != 0); /* before reset: unknown */
    g_occ_counting = 1;
    assert(occ_snapshot_finish(occ_snapshot_make()) == 0);
    occ_segment *a = append(0), *b = append(3);
    occ_snapshot *first = occ_snapshot_make();
    occ_segment *c = append(9); occ_snapshot *second = occ_snapshot_make();
    occ_clear(); a->value = 2; b->value = 4; c->value = 8;
    assert(occ_snapshot_finish(first) == 6);
    assert(occ_snapshot_finish(second) == 14);
    occ_release(a); occ_release(b); occ_release(c);
    a = append(UINT64_MAX); b = append(1); first = occ_snapshot_make(); occ_clear();
    assert(occ_snapshot_finish(first) == UINT64_MAX); occ_release(a); occ_release(b);
    g_occ_unknown = 1; assert(occ_snapshot_finish(occ_snapshot_make()) != 0);
    assert(occ_snapshot_finish(NULL) != 0);
    free(g_occ_list); return 0;
}
'''
        with tempfile.TemporaryDirectory() as tmp:
            src, exe = Path(tmp) / 'test.c', Path(tmp) / 'test'
            src.write_text(code)
            subprocess.run([cc, '-std=c11', '-Wall', '-Wextra', '-Wno-unused-variable', '-Werror', str(src), '-o', str(exe)], check=True)
            subprocess.run([str(exe)], check=True)

    def test_command_boundaries_and_exhaustion(self):
        cc = shutil.which('cc') or shutil.which('clang')
        if not cc:
            self.skipTest('C compiler not available')
        source = (Path(__file__).resolve().parents[1] / 'nxnative/dm/android/gfx_vk_core.c').read_text()
        state = source[source.index('enum { OCC_MAX ='):source.index('#define SCRATCH_BLOCK')]
        functions = source[source.index('void vk_occ_reset(void)'):source.index('static VkMemoryBarrier2 full_barrier')]
        code = '''#include <stdint.h>\n#include <stdlib.h>\n#include <stdatomic.h>\n#include <assert.h>\n'''
        code += '''typedef void *VkQueryPool; typedef int VkCommandBuffer;\n'''+state
        code += r'''
typedef struct { occ_segment *occ[OCC_MAX]; unsigned nocc; } vksub_t;
static vksub_t slot; static int g_cur;
static vksub_t *cur(void) { return &slot; }
static int vk_cmd(void) { return 1; }
static int begins, ends;
#define VK_QUERY_CONTROL_PRECISE_BIT 1
#define VKLOG(...) ((void)0)
static void vkCmdBeginQuery(int c, void *p, uint32_t q, int flags) { (void)c; (void)p; (void)q; assert(flags == 1); begins++; }
static void vkCmdEndQuery(int c, void *p, uint32_t q) { (void)c; (void)p; (void)q; ends++; }
void vk_occ_end(void);
''' + functions + r'''
int main(void) {
    g_occ_enabled = 1; vk_occ_reset(); vk_occ_begin(); vk_occ_begin();
    assert(begins == 1); vk_occ_end(); assert(ends == 1);
    slot.occ[0]->value = 4; occ_snapshot *s = occ_snapshot_make();
    vk_occ_begin(); assert(begins == 2); vk_occ_reset(); assert(ends == 2);
    assert(occ_snapshot_finish(s) == 4);
    occ_release(slot.occ[0]); occ_release(slot.occ[1]);
    slot.nocc = OCC_MAX; vk_occ_begin(); assert(g_occ_unknown);
    assert(occ_snapshot_finish(occ_snapshot_make()) != 0);
    vk_occ_reset(); assert(!g_occ_unknown); free(g_occ_list); return 0;
}
'''
        with tempfile.TemporaryDirectory() as tmp:
            src, exe = Path(tmp) / 'test.c', Path(tmp) / 'test'
            src.write_text(code)
            subprocess.run([cc, '-std=c11', '-Wall', '-Wextra', '-Wno-unused-variable', '-Werror', str(src), '-o', str(exe)], check=True)
            subprocess.run([str(exe)], check=True)


if __name__ == '__main__':
    unittest.main()
