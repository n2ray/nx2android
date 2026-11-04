# Unified library experiment

This branch starts with read-only discovery of already prepared nx2android data packs:

```
python -m porter.library /path/to/game-library
```

Each direct child with `nx2a-data.json`, `mods/`, `RomFS/` and `shaders.dmsv` is listed by title ID and version. This is a structural check, not proof that the contents are complete, compatible, safe, or launchable. Nothing is imported, modified, executed, or uploaded.

The experimental Android library activity lists prepared packs from the app's external `games/<id>/` folder. `mkapk.py --library-launcher` enables the activity when the supplied DEX includes the library and external-display activities; the APK must include `assets/library-runtime-id.txt` with its compiled profile's uppercase title ID. An optional `cover.png` appears on the card. Selecting the compatible game writes an app-private `library-selection.txt`, then starts the game activity.

The runtime rejects IDs other than its compiled profile, reads that pack and isolates its internal save in `saves/<id>/`. When the selection is absent, the existing single-game paths remain in use. On a Xiaomi 15 Ultra the separate experimental APK listed and launched the prepared OCTOPATH TRAVELER 1.0.3 pack into its Chinese story scene. The experimental build used the separately maintained Octopath rendering fixes and profile: they are not all in this branch.

The host still compiles one game profile into `libdmhost.so`, so other game cards cannot start until runtime/profile work is complete. Packs must currently be prepared and copied into place externally. Compatibility of arbitrary `env.txt` settings, per-game temporary data and save import/export need end-to-end verification before this can be used. Mobile extraction, rewriting and shader translation are separate future work.
