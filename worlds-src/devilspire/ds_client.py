"""Devil Spire Archipelago client (CommonClient based). Fan-made, unofficial.

Bridges the AP server <-> the patched game through text files in the game's save dir (see patch/README.md).
Run via the Archipelago Launcher ("Devil Spire Client") or `python DevilSpireClient.py` from client/.
"""
from __future__ import annotations

import asyncio
import logging
import os
import sys
import typing
from pathlib import Path

try:  # inside the apworld package
    from . import auto_patch as ap_patch
    from . import file_protocol as fp
    from . import health
    from .constants import GAME_NAME, PATCH_PROTOCOL
except ImportError:  # run standalone (client/DevilSpireClient.py puts this dir on sys.path)
    import auto_patch as ap_patch  # type: ignore
    import file_protocol as fp  # type: ignore
    import health  # type: ignore
    from constants import GAME_NAME, PATCH_PROTOCOL  # type: ignore

import Utils
from CommonClient import ClientCommandProcessor, CommonContext, get_base_parser, gui_enabled, handle_url_arg, \
    logger, server_loop
from NetUtils import ClientStatus

POLL_SECONDS = 0.5
HEALTH_SECONDS = 10.0


def remembered_game_dir() -> typing.Optional[Path]:
    try:
        d = Utils.persistent_load().get("devilspire", {}).get("game_dir")
        return Path(d) if d and Path(d).is_dir() else None
    except Exception:
        return None


def remember_game_dir(d: Path) -> None:
    try:
        Utils.persistent_store("devilspire", "game_dir", str(d))
    except Exception:
        pass


class DevilSpireCommandProcessor(ClientCommandProcessor):
    def _patch_cmd(self, fn, args) -> bool:
        src = Path(" ".join(args)).expanduser() if args else None
        try:
            st = fn(src, log=logger.info)
        except ap_patch.PatchError as e:
            logger.error(str(e))
            return False
        except OSError as e:
            logger.error(f"File error: {e!r} (close the game; check the folder is writable)")
            return False
        remember_game_dir(st.game_dir)
        self.ctx.next_health = 0.0  # re-check now
        return True

    def _cmd_auto_patch(self, *game_dir: str) -> bool:
        """Patch Devil Spire for Archipelago (optional: game folder)."""
        return self._patch_cmd(ap_patch.auto_patch, game_dir)

    def _cmd_patch(self, *game_dir: str) -> bool:
        """Same as /auto_patch."""
        return self._cmd_auto_patch(*game_dir)

    def _cmd_restore(self, *game_dir: str) -> bool:
        """Undo the patch (optional: game folder)."""
        return self._patch_cmd(ap_patch.restore, game_dir)

    def _cmd_status(self) -> bool:
        """Show patch, save folder and connection state."""
        c = self.ctx
        try:
            logger.info(ap_patch.patch_status(remembered_game_dir()).describe())
        except ap_patch.PatchError as e:
            logger.info(str(e))
        logger.info(f"save dir: {c.save_dir}; checks found: {len(c.found_locations)}; "
                    f"items: {len(c.in_writer.items) if c.in_writer else 0}; "
                    f"server-checked: {len(c.checked_locations)}; goal: {c.finished_game}; slot: {c.slot_id}")
        return True

    def _cmd_savedir(self, path: str = "") -> bool:
        """Show or set the save folder (only needed if not found)."""
        if path:
            p = Path(path).expanduser()
            if not p.is_dir():
                logger.error(f"Not a directory: {p}")
                return False
            self.ctx.set_save_dir(p)
        logger.info(f"Save dir: {self.ctx.save_dir}")
        return True


class DevilSpireContext(CommonContext):
    command_processor = DevilSpireCommandProcessor
    game = GAME_NAME
    items_handling = 0b111  # full list incl. own-world items and start inventory; patch re-grants everything each run

    def __init__(self, server_address: typing.Optional[str], password: typing.Optional[str],
                 save_dir: typing.Optional[str] = None):
        super().__init__(server_address, password)
        self.explicit_save_dir = save_dir
        self.save_dir: typing.Optional[Path] = None
        self.tailer: typing.Optional[fp.OutTailer] = None
        self.in_writer: typing.Optional[fp.InWriter] = None
        self.slot_data: dict = {}
        self.death_link = False
        self.found_locations: set[int] = set()   # every L| id seen in ap_out.txt (kept across reconnects)
        self.sent_locations: set[int] = set()    # ids sent in this connection (dedupe)
        self.goal_seen = False
        self.session_ready = False               # Connected processed, catch-up read done
        self.items_synced = False                # got ReceivedItems since the last Connected (else ap_in is stale)
        self.slot_id: typing.Optional[str] = None
        self.item_order: list = []                        # stable (item, location, player) order of ap_in.txt
        self.game_protocol: typing.Optional[int] = None   # from the newest S|<n> line
        self.health = health.HealthMonitor(logger.warning)
        self.datawin = health.DataWinCheck(self._patch_status)
        self.orig_watch = health.OriginalSaveWatch()
        self.next_health = 0.0
        self._warned_dir = False
        self.set_save_dir(fp.find_save_dir(save_dir))

    # -- setup ------------------------------------------------------------------------------------------------
    def set_save_dir(self, path: typing.Optional[Path]) -> None:
        self.save_dir = path
        if path is None:
            self.tailer = self.in_writer = None
            return
        self.tailer = fp.OutTailer(path / fp.OUT_FILE)
        self.in_writer = fp.InWriter(path / fp.IN_FILE)
        self.session_ready = False
        logger.info(f"Devil Spire save dir: {path}")
        if self.slot_data and self.slot is not None:
            self.on_connected_setup()

    def make_gui(self):
        ui = super().make_gui()
        ui.base_title = "Archipelago Devil Spire Client"
        return ui

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    # -- server packages --------------------------------------------------------------------------------------
    def on_package(self, cmd: str, args: dict):
        if cmd == "Connected":
            self.slot_data = dict(args.get("slot_data") or {})
            self.death_link = bool(self.slot_data.get("death_link"))
            asyncio.create_task(self.update_death_link(self.death_link))
            self.sent_locations.clear()
            self.items_synced = False
            self.on_connected_setup()
        elif cmd == "ReceivedItems":
            self.items_synced = True
            self.refresh_items()
        elif cmd == "RoomUpdate":
            self.refresh_items()

    def on_connected_setup(self) -> None:
        """Called after Connected (and when the save dir changes): sync identity, write config, rescan ap_out.

        Identity = seed name + team + slot (`slot_id`, also written to ap_config.ini and used by the game to tag
        check lines). First connection for a save dir adopts its existing files (offline checks are sent). A
        different seed/slot moves this slot's files to ap_backup/<time>_<old>/ and starts clean."""
        if self.save_dir is None or self.tailer is None or self.in_writer is None:
            return
        self.slot_id = fp.make_slot_id(self.server_seed_name, self.team, self.slot)
        identity = {"slot_id": self.slot_id, "name": self.auth, "base_id": self.slot_data.get("base_id")}
        old = fp.load_state(self.save_dir).get("identity")
        if old and "slot_id" not in old:  # state file of an older client version
            old = dict(old, slot_id=fp.make_slot_id(old.get("seed"), old.get("team"), old.get("slot")))
        if old and old.get("slot_id") != self.slot_id:
            dest = fp.reset_save_dir(self.save_dir, str(old.get("slot_id", "old")))
            logger.warning(f"This save folder belonged to another multiworld/slot ({old.get('slot_id')}). "
                           f"Its Archipelago character and files were moved to {dest}. If Devil Spire is running, "
                           "quit and restart it, then start a New Game.")
            self.found_locations.clear()
            self.goal_seen = False
            self.in_writer.deaths.clear()
            self.in_writer.items = []
            self.in_writer._last = None
        elif not old:
            if fp.repair_souls_file(self.save_dir):
                logger.info("Reset ap_souls_granted.txt (no items were received before the first connection).")
        state = fp.load_state(self.save_dir) if old == identity else {}
        self.item_order = state.get("items", []) if old == identity else []
        if old != identity:
            fp.store_state(self.save_dir, {"identity": identity, "items": self.item_order})
        self.write_config()
        # catch-up: rescan the WHOLE ap_out.txt on every (re)connect, so checks made while the client was closed or
        # disconnected are sent (the server ignores duplicates). DeathLink lines are historic here: not re-sent.
        self.tailer.reset()
        for ev in self.tailer.poll_events():
            self.handle_event(ev, replay=True)
        self.session_ready = True
        if self.items_synced:
            self.refresh_items(force=True)
        asyncio.create_task(self.flush_locations())

    @staticmethod
    def _patch_status(game_dir: Path):
        try:
            return ap_patch.patch_status(game_dir)
        except Exception as e:
            logger.debug(f"patch status failed: {e!r}")
            return None

    def run_health_checks(self) -> None:
        """Blocking (hashes data.win only when it changed); run in a thread."""
        game_dir = remembered_game_dir() or ap_patch.find_game_dir()
        self.health.report("datawin", self.datawin.check(game_dir))
        self.health.report("protocol", health.protocol_warning(self.game_protocol, PATCH_PROTOCOL))
        self.health.report("unpatched", self.orig_watch.check(self.save_dir))
        self.health.report("cloud", health.cloud_warning(self.save_dir))

    def write_config(self) -> None:
        try:
            if fp.write_config(self.save_dir, self.slot_data, slot_id=self.slot_id):
                logger.info("Wrote ap_config.ini (the game picks it up within a second).")
        except (OSError, KeyError) as e:
            logger.error(f"Could not write ap_config.ini (retrying): {e!r}")

    def on_deathlink(self, data: dict) -> None:
        super().on_deathlink(data)
        if self.in_writer is not None and self.death_link:
            self.in_writer.add_death(data.get("cause") or f"DeathLink from {data.get('source', '?')}")
            self.write_in()

    # -- ap_in.txt --------------------------------------------------------------------------------------------
    def refresh_items(self, force: bool = False) -> None:
        # never write a list that is not the server's current full list for THIS slot (e.g. right after Connected)
        if self.in_writer is None or self.slot is None or not self.items_synced or not self.session_ready:
            return
        order = fp.stable_item_order(self.item_order, [(it.item, it.location, it.player) for it in self.items_received])
        if order != self.item_order:
            self.item_order = order
            try:
                st = fp.load_state(self.save_dir)
                st["items"] = order
                fp.store_state(self.save_dir, st)
            except OSError as e:
                logger.error(f"Could not store item order: {e!r}")
        if len(self.item_order) > len(self.items_received):
            logger.debug("server list has fewer items than already delivered; keeping indexes stable")
        items = []
        for item, _loc, player in self.item_order:
            try:
                name = self.item_names.lookup_in_game(item, self.game)
            except Exception:
                name = f"Item {item}"
            sender = self.player_names.get(player, f"Player {player}")
            items.append((item, name, sender))
        self.in_writer.items = items
        self.write_in(force)

    def write_in(self, force: bool = False) -> None:
        if self.in_writer is None:
            return
        try:
            self.in_writer.flush(force)
        except OSError as e:
            logger.error(f"Could not write ap_in.txt (retrying): {e!r}")

    # -- ap_out.txt -------------------------------------------------------------------------------------------
    def connected_to_slot(self) -> bool:
        return bool(self.slot is not None and self.server and self.server.socket and not self.server.socket.closed)

    def handle_event(self, ev: fp.OutEvent, replay: bool = False) -> None:
        if ev.kind in "LG" and ev.slot is not None and ev.slot != self.slot_id:
            return  # emitted while the game belonged to another multiworld/slot: never send it here
        if ev.kind == "L" and ev.location_id is not None:
            self.found_locations.add(ev.location_id)
        elif ev.kind == "G":
            self.goal_seen = True
        elif ev.kind == "D":
            if not replay and self.death_link and self.connected_to_slot():
                asyncio.create_task(self.send_death(f"{self.auth} {ev.text}".strip()))
        elif ev.kind == "S":
            v = ev.text.split("|", 1)[0].strip()
            self.game_protocol = int(v) if v.isdigit() else None
            if not replay:
                self.next_health = 0.0
        elif ev.kind == "E":
            logger.warning(f"[game] {ev.text}")

    async def flush_locations(self) -> None:
        if not self.connected_to_slot():
            return
        todo = {loc for loc in self.found_locations
                if loc not in self.sent_locations and loc not in self.checked_locations}
        unknown = {loc for loc in todo if self.server_locations and loc not in self.server_locations}
        if unknown:
            logger.warning(f"Ignoring location ids the server does not know (base_id mismatch?): {sorted(unknown)}")
            self.sent_locations |= unknown
            todo -= unknown
        if todo:
            self.sent_locations |= todo
            await self.send_msgs([{"cmd": "LocationChecks", "locations": sorted(todo)}])
        if self.goal_seen and not self.finished_game:
            self.finished_game = True
            await self.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
            logger.info("Goal complete (Rhamdon defeated).")

    async def watch_files(self) -> None:
        while not self.exit_event.is_set():
            try:
                if self.save_dir is None:
                    self.set_save_dir(fp.find_save_dir(self.explicit_save_dir))
                    if self.save_dir is None and not self._warned_dir:
                        self._warned_dir = True
                        logger.warning("Devil Spire save dir not found. Use --savedir, $DEVILSPIRE_SAVE_DIR "
                                       "or /savedir <path>.")
                elif self.session_ready and self.connected_to_slot():
                    for ev in self.tailer.poll_events():
                        self.handle_event(ev)
                    await self.flush_locations()
                    self.write_config()   # no-op unless missing/changed (e.g. a failed write on Windows)
                    self.write_in()       # no-op unless the last write failed or content changed
                now = asyncio.get_running_loop().time()
                if now >= self.next_health:
                    self.next_health = now + HEALTH_SECONDS
                    await asyncio.to_thread(self.run_health_checks)
            except Exception:
                logger.exception("file watcher error")
            await asyncio.sleep(POLL_SECONDS)

    def run_gui(self):
        super().run_gui()


async def _main(args) -> None:
    ctx = DevilSpireContext(args.connect, args.password, getattr(args, "savedir", None))
    ctx.auth = args.name
    ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
    watcher = asyncio.create_task(ctx.watch_files(), name="DevilSpireFileWatcher")
    if gui_enabled:
        ctx.run_gui()
    ctx.run_cli()
    await ctx.exit_event.wait()
    watcher.cancel()
    await ctx.shutdown()


def launch(*launch_args: str) -> None:
    parser = get_base_parser(description="Devil Spire Archipelago client (fan-made, unofficial).")
    parser.add_argument("--name", default=None, help="Slot name to connect as.")
    parser.add_argument("--savedir", default=None,
                        help="Devil Spire save dir (default: $DEVILSPIRE_SAVE_DIR, then auto-detect Proton/%%APPDATA%%).")
    parser.add_argument("url", nargs="?", help="archipelago://name:pass@host:port")
    args = parser.parse_args(launch_args)
    args = handle_url_arg(args, parser=parser)
    Utils.init_logging("DevilSpireClient", exception_logger="Client")
    import colorama
    colorama.just_fix_windows_console()
    asyncio.run(_main(args))
    colorama.deinit()


if __name__ == "__main__":
    launch(*sys.argv[1:])
