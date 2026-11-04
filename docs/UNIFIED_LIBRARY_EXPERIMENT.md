# Unified library experiment

This branch starts with read-only discovery of already prepared nx2android data packs:

```
python -m porter.library /path/to/game-library
```

Each direct child with `nx2a-data.json`, `mods/`, `RomFS/` and `shaders.dmsv` is listed by title ID and version. This is a structural check, not proof that the contents are complete, compatible, safe, or launchable. Nothing is imported, modified, executed, or uploaded.

The experimental Android path accepts an app-private `library-selection.txt` containing an uppercase 16-digit title ID. It rejects IDs other than the runtime's compiled profile, reads the pack under the app's external `games/<id>/` folder, and isolates its internal save in `saves/<id>/`. When the selection is absent, the existing single-game paths remain in use. This is a developer-only path experiment, not an Android game picker; no selection file is created by the app yet.

The host still compiles one game profile into `libdmhost.so`, so selecting a second game requires runtime/profile work. Compatibility of arbitrary `env.txt` settings, per-game temporary data and save import/export need end-to-end verification before this can be used. Mobile extraction, rewriting and shader translation are separate future work.
