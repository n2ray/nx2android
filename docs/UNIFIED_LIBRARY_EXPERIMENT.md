# Unified library experiment

This branch starts with read-only discovery of already prepared nx2android data packs:

```
python -m porter.library /path/to/game-library
```

Each direct child with `nx2a-data.json`, `mods/`, `RomFS/` and `shaders.dmsv` is listed by title ID and version. This is a structural check, not proof that the contents are complete, compatible, safe, or launchable. Nothing is imported, modified, executed, or uploaded.

The experimental Android library activity lists prepared packs from the app's external `games/<id>/` folder. `mkapk.py --library-launcher` enables the activity when the supplied DEX includes the library and external-display activities; the APK must include `assets/library-runtime-id.txt` with its compiled profile's uppercase title ID. An optional `cover.png` appears on the card. Selecting the compatible game writes an app-private `library-selection.txt`, then starts the game activity.

The runtime rejects IDs other than its compiled profile, reads that pack and isolates its internal save in `saves/<id>/`. When the selection is absent, the existing single-game paths remain in use. On a Xiaomi 15 Ultra the separate experimental APK listed and launched the prepared OCTOPATH TRAVELER 1.0.3 pack into its Chinese story scene. The experimental build used the separately maintained Octopath rendering fixes and profile: they are not all in this branch.

The host still compiles one game profile into `libdmhost.so`, so other game cards cannot start until runtime/profile work is complete. Packs must currently be prepared and copied into place externally. Compatibility of arbitrary `env.txt` settings, per-game temporary data and save import/export need end-to-end verification before this can be used. Mobile extraction, rewriting and shader translation are separate future work.

## Phone-side preparation experiments

The target is direct import of the player's own XCI / NSP and keys, without desktop preparation. On a Xiaomi 15 Ultra, a separately downloaded Galar Native v0.39 Android extractor identified an OCTOPATH TRAVELER 1.0.3 XCI and produced the ExeFS and a RomFS manifest on the phone. The reference APK's SHA-256 matched its GitHub release digest. The extractor and OpenSSL libraries were used only as temporary research tools; they are not bundled in this branch.

Using that release's Android Python and Capstone with the previously tested Octopath rewriter, an unbounded spin-instruction cache exhausted memory. A 32,768-entry LRU retained the complete scan and the phone rewrote main, subsdk0 and sdk. The SHA-256 of each rewritten binary matched the existing installation. One observed sample with the bounded cache was approximately 344 MB RSS; this is not a peak-memory measurement. The experiment used isolated outputs and no save data.

The `extract_aot` and `xlate_aot` projects compile this checkout's own extractor and shader translator for Android on a Linux build host. The experimental CI builds only tools from source: it must never receive game files or keys. These projects are based on Galar Native (MIT), commit `884e6d9fd338f81d4c88c54d596a3814a2e7d4e0`. The reference translator identifies a different source version, so its binary must not be treated as interchangeable with this checkout's shader chain.

There is no Android file-picker, end-to-end XCI/NSP import, on-device shader conversion or safe install transaction in the app yet. Do not replace the installed Octopath game or its saves with these research outputs.
