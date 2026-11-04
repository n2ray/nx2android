#include <assert.h>
#include <string.h>
#include "../nxnative/dm/android/library_paths.h"

int main(void) {
    char root[256], save[256];
    uint64_t id = UINT64_C(0x010057D006492000);
    assert(dm_library_paths("010057D006492000", id, "/external", "/internal", root, sizeof root, save, sizeof save));
    assert(!strcmp(root, "/external/games/010057D006492000"));
    assert(!strcmp(save, "/internal/saves/010057D006492000"));
    assert(!dm_library_paths("010057D006492001", id, "/external", "/internal", root, sizeof root, save, sizeof save));
    assert(!dm_library_paths("../../../../oops", id, "/external", "/internal", root, sizeof root, save, sizeof save));
    assert(!dm_library_paths("010057d006492000", id, "/external", "/internal", root, sizeof root, save, sizeof save));
    assert(!dm_library_paths("010057D006492000", id, "/external", "/internal", root, 4, save, sizeof save));
    return 0;
}
