#ifndef NX2A_LIBRARY_PATHS_H
#define NX2A_LIBRARY_PATHS_H
#include <stdint.h>
#include <stdio.h>
#include <string.h>

/* Reject a mismatched runtime before opening another game's files or saves. */
static int dm_library_paths(const char *id, uint64_t runtime_id, const char *external,
                            const char *internal, char *root, size_t root_size,
                            char *save, size_t save_size) {
    if (!id || strlen(id) != 16 || !external || !internal) return 0;
    uint64_t value = 0;
    for (int i = 0; i < 16; ++i) {
        unsigned char c = (unsigned char)id[i];
        int digit = c >= '0' && c <= '9' ? c - '0' : c >= 'A' && c <= 'F' ? c - 'A' + 10 : -1;
        if (digit < 0) return 0;
        value = (value << 4) | (unsigned)digit;
    }
    if (value != runtime_id) return 0;
    int a = snprintf(root, root_size, "%s/games/%s", external, id);
    int b = snprintf(save, save_size, "%s/saves/%s", internal, id);
    return a >= 0 && b >= 0 && (size_t)a < root_size && (size_t)b < save_size;
}
#endif
