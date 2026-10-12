# Research notes (Archipelago x Devil Spire)

Date: 2026-10-11. Legend: [V] verified from a fetched source this session, [U] unverified / from memory, must check.

## Local facts (read-only inspection of the install)
- [V] Install has data.win (~43.8 MB), Devil Spire.exe (~4.5 MB), audiogroup1..22.dat, D3DX9_43.dll, steam_api.dll, options.ini, loose .ogg music, splash.png.
- [V] options.ini has a [Windows] section (CreateTexturesOnDemand, AlternateSyncMethod, VertexBufferMethod, SleepMargin) -> typical GM runner file.
- [V] The exe contains strings "c:\hudson\GMBase\GMGreen\GameMaker\Runner\VC_Runner..." and "gamemaker_pro" -> consistent with the GM Studio 1.x runner (exact version [U], read it from data.win GEN8 chunk).
- [U] Not found on the machine at inspection time: dotnet, UndertaleModCli, python3 (in the shell PATH I used; may exist in a nix-shell/flake).
- Steam compatdata dir: /mnt/NVME/SteamLibrary/steamapps/compatdata/<appid> (Devil Spire appid [U]).

## Archipelago world API
- World API: https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/world%20api.md  [V]
  - World class, WebWorld, options dataclass (PerGameCommonOptions), settings (host.yaml), Locations/Items (IDs 1..2^53-1, recommend <2^31), item classifications (progression, useful, filler, trap, skip_balancing, deprioritized...), Regions/Entrances/access rules (set_rule/add_rule, CollectionState.has), events (id None; goal must still be sent via StatusUpdate by the client), generation hooks order (generate_early, create_regions, create_items, set_rules, connect_entrances, generate_basic, pre_fill, fill_hook, post_fill, generate_output, fill_slot_data), start inventory (push_precollected / start_inventory_from_pool), LogicMixin, tests via test.bases.WorldTestBase + assertAccessDependency, docs under worlds/<game>/docs (game info + tutorial md), requirements.txt.
- Adding games: https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/adding%20games.md [U content not read this session]
- Options API: https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/options%20api.md [U]
- Settings API: https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/settings%20api.md [U]
- Tests doc: https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/tests.md [U]
- Style guide: https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/style.md [U]

## APWorld format
- https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/apworld%20specification.md [V]
  - .apworld = zip, all-lowercase name, contains folder of same name (e.g. devilspire/__init__.py). Placed in the worlds/ folder of an AP install (or custom_worlds in newer installers [U]).
  - archipelago.json: required "game"; optional minimum_ap_version, maximum_ap_version, world_version ("major.minor.build"), authors. Packaged files get version/compatible_version added automatically.
  - Build: Launcher "Build APWorlds" component (source install only); CLI `Launcher.py "Build APWorlds" -- "Game Name"` -> build/apworlds. .apignore (gitignore syntax) excludes files.
  - Use relative imports inside the world, absolute for AP core; every subfolder needs __init__.py.

## Network protocol / clients
- Protocol: https://github.com/ArchipelagoMW/Archipelago/blob/main/docs/network%20protocol.md [U content not fetched; known pieces from memory: websocket JSON; RoomInfo, Connect, Connected (slot_data), ReceivedItems, LocationChecks, LocationScouts, StatusUpdate (CLIENT_GOAL=30), Get/Set/SetNotify (data storage), Bounce (DeathLink uses tags ["DeathLink"] + Bounce), Sync, Say, PrintJSON, DataPackage]. VERIFY against the doc before coding.
- CommonClient.py (python, CommonContext, server_loop, GUI via kvui) [U]; example world client structure confirmed via Undertale excerpts below.
- Undertale (GameMaker, file-based) world: https://git.hollymcfarland.com/monorail/Archipelago/raw/commit/0b5c7fe8a9c6f052bd870e407eb47d284737f56f/worlds/undertale/__init__.py [V excerpt] and client https://github.com/Satisha10/Archipelago_wotw/blob/main/UndertaleClient.py [V excerpt]: Python CommonContext subclass; reads/writes files in the game's save folder; uses slot_data, Get/SetNotify data storage, DeathLink hook; game_watcher async task; registered via Launcher component running client in a Process.
  Real upstream: https://github.com/ArchipelagoMW/Archipelago/tree/main/worlds/undertale [U path assumed]

## GameMaker precedent
- Deltarune AP mod (UndertaleModTool + UMP framework + C#/GML/Python): https://github.com/Tenebrosful/DeltaruneAP-mod/ [V readme] - patches data.win via UTMT script (Build.cxs); README credits an "In-Game AP Client".
- GameMaker (2.2.1+) integration sample: https://github.com/PrintOmnivore20/archipelago-gamemaker-integration-sample [V] - in-game websocket client written in GML; README says it will NOT work on versions older than 2.2.1 and some parts need 2023.8+. => Not usable as-is for GMS1.
- Others mentioned by user (Pizza Tower, Cult of the Lamb, Risk of Rain, Hollow Knight): not researched here [U]. Hollow Knight is Unity, not relevant.

## GameMaker 1 limitations
- external_define/external_call load DLLs (args real or string only; returns real/string): https://manual.gamemaker.io/lts/en/GameMaker_Language/GML_Reference/OS_And_Compiler/external_call.htm [V - LTS manual, exact GMS1 behaviour U]
- GM8.1 has no buffers/pointers; DLL workaround patterns: https://yal.cc/gm81-extensions/ [V] (GMS1 does have buffers; GM8.1 doesn't - don't confuse).
- network_create_socket / network_connect (TCP/UDP) exist in GMS1 [U, manual shown is LTS]; websocket socket type (network_socket_ws) is newer [U: sample README implies >=2.2.1]. Raw TCP to a local bridge is the plausible GMS1 route.
- Maarten Baert HTTP DLL notes for Studio: https://www.maartenbaert.be/game-maker-dlls/http-dll-2/ [V]
- File I/O (file_text_*, ini_*, file_exists) is core GML in GMS1 [U but near-certain]; GMS1 sandboxes files to working dir / %LOCALAPPDATA%/<game> (check which for this game) [U].

## UndertaleModTool / tooling
- UTMT repo: https://github.com/UnderminersTeam/UndertaleModTool [V]. Supports GML code editing (not YYC), decompiler/compiler, scripts, library UndertaleModLib, CLI UndertaleModCli (described as primitive); GUI requires Windows to compile.
- Release 0.9.1.2: official CLI builds for Windows, Ubuntu, macOS https://github.com/UnderminersTeam/UndertaleModTool/releases/tag/0.9.1.2 [V]
- Nixpkgs package `undertalemodcli` (buildDotnetModule, dotnet 10, x86_64-linux): https://github.com/NixOS/nixpkgs/blob/nixpkgs-unstable/pkgs/by-name/un/undertalemodcli/package.nix [V]; MyNixOS shows 0.9.2.0 https://mynixos.com/nixpkgs/package/undertalemodcli [V]; update PR https://github.com/NixOS/nixpkgs/pull/555802 [V]. NUR alt: utmt-cli https://github.com/nix-community/nur-combined/blob/main/repos/claymorwan/pkgs/utmt-cli/default.nix [V].
- [U] Whether UTMT 0.9.x fully supports GMS1-era data.win (bytecode 14/15, older chunk layouts) - UTMT historically supports GM:S 1 / bytecode 14-16 [U]; test by loading and re-saving data.win with no changes and diffing.
- [U] Alternative: GMS1 games can sometimes be unpacked with other tools (e.g. "gm8decompiler" is for GM8 only, not GMS1) - don't rely.
- [U] UMP ("Undertale Mod Project"/Nhaar framework) mentioned in Deltarune README; check for generic use.

## Proton/NixOS considerations [U unless noted]
- Game runs as Windows exe under Proton; client (Python) runs natively on Linux or inside the same prefix. Files written by the game land in the prefix: compatdata/<appid>/pfx/drive_c/users/steamuser/AppData/Local/<game name or exe>/ or in the game dir (working dir). Find by running the game and `find -newer`.
- A native Linux bridge reaching a TCP socket opened by the game works across Wine on localhost (Wine shares host network stack) [U but standard].
- NixOS: use a flake/devshell with python3 + websockets deps for AP (or run AP from source with its own venv; nix-ld may be needed for prebuilt binaries), plus undertalemodcli from nixpkgs.
