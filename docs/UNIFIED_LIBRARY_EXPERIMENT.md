# Unified library experiment

This branch starts with read-only discovery of already prepared nx2android data packs:

```
python -m porter.library /path/to/game-library
```

Each direct child with `nx2a-data.json`, `mods/`, `RomFS/` and `shaders.dmsv` is listed by title ID and version. This is a structural check, not proof that the contents are complete, compatible, safe, or launchable. Nothing is imported, modified, executed, or uploaded.

The existing Android host still compiles game profiles into `libdmhost.so` and uses a single application data root. A unified Android launcher must first select a compatible runtime/profile and isolate each game's paths and saves. Existing `env.txt` values, including DLC paths, must be resolved against the selected game, and an update must not silently replace user settings or saves. Mobile extraction, rewriting and shader translation are separate future work.
