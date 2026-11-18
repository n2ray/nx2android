"""Cross-chunk GPU copies retain ordering, offsets and all-or-nothing preflight."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('cc'), 'host C compiler required')
class CrossCopy(unittest.TestCase):
    def test_chunk_boundaries(self):
        source = (ROOT / 'nxnative/dm/android/gfx_vk_core.c').read_text()
        source = source[source.index('void vk_gpu_wrote(uint64_t a, uint64_t n);\ntypedef struct'):
                        source.index('void mtl_sub_fill(uint64_t dst')]
        code = r'''
#define VK_NO_PROTOTYPES
#include <vulkan/vulkan_core.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
typedef struct { uint64_t lo, hi, base, end, boff; VkBuffer buf; } vkpool_t;
static uint8_t memory[6][128];
static vkpool_t pools[6];
static int copies, barriers, ends, writes, red;
static uint64_t wrote_addr, wrote_len;
static vkpool_t *vk_pool_of(uint64_t a, uint64_t n) {
    for (int i=0; i<6; i++) if (a>=pools[i].lo && a<pools[i].hi && n<=pools[i].hi-a) return &pools[i];
    return NULL;
}
static void vk_end_pass_land(void) { ends++; }
static VkCommandBuffer vk_cmd(void) { return (VkCommandBuffer)(uintptr_t)1; }
static void vk_img_barrier_all(VkCommandBuffer b) { (void)b; barriers++; }
static void vkCmdCopyBuffer(VkCommandBuffer c, VkBuffer s, VkBuffer d, uint32_t n, const VkBufferCopy *r) {
    (void)c; assert(n==1); copies++; memcpy((uint8_t *)(uintptr_t)d+r->dstOffset,(uint8_t *)(uintptr_t)s+r->srcOffset,r->size);
}
void vk_gpu_wrote(uint64_t a, uint64_t n) { writes++; wrote_addr=a; wrote_len=n; }
#define VKRED_ONCE(id, ...) do { (void)(id); red++; } while (0)
#define VKLOG(...) ((void)0)
'''
        code += source
        code += r'''
int main(void) {
    const uint64_t bounds[6][4]={{0x1000,0x1040,0x1000,0x10c0},{0x1040,0x1080,0x1000,0x10c0},{0x1080,0x10c0,0x1000,0x10c0},
        {0x2000,0x2030,0x2000,0x20b0},{0x2030,0x2070,0x2000,0x20b0},{0x2070,0x20b0,0x2000,0x20b0}};
    for(int i=0;i<6;i++) { pools[i]=(vkpool_t){bounds[i][0],bounds[i][1],bounds[i][2],bounds[i][3],8,(VkBuffer)(uintptr_t)memory[i]};
        for(uint64_t a=pools[i].lo;a<pools[i].hi;a++) memory[i][8+a-pools[i].lo]=(uint8_t)(a-0x1000); }
    mtl_sub_copy(0x1030,0x2018,80);
    assert(copies==3 && barriers==2 && ends==1 && writes==1 && wrote_addr==0x2018 && wrote_len==80);
    for(int i=0;i<80;i++) { vkpool_t *p=vk_pool_of(0x2018+i,1); assert(((uint8_t *)(uintptr_t)p->buf)[p->boff+0x2018+i-p->lo]==(uint8_t)(0x30+i)); }
    int c=copies; mtl_sub_copy(0x1030,0x20a0,80); assert(copies==c && red==1 && writes==1);
    mtl_sub_copy(UINT64_MAX-2,0x2020,8); assert(copies==c && writes==1);
    mtl_sub_copy(0x1030,0x1040,40); assert(copies==c && writes==1);
    pools[4].lo=0x2031; mtl_sub_copy(0x1030,0x2018,80); assert(copies==c && writes==1); pools[4].lo=0x2030;
    mtl_sub_copy(0x1000,0x2000,16); assert(copies==c+1 && writes==2);
    return 0;
}
'''
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / 'test.c'
            binary = Path(td) / 'test'
            src.write_text(code)
            subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-I',
                            str(ROOT / 'nxnative/dm/third_party/vulkan-headers/include'),
                            str(src), '-o', str(binary)], check=True)
            subprocess.run([str(binary)], check=True)


if __name__ == '__main__':
    unittest.main()
