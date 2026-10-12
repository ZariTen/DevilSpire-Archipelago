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
    from . import file_protocol as fp
    from .constants import GAME_NAME
except ImportError:  # run standalone (client/DevilSpireClient.py puts this dir on sys.path)
    import file_protocol as fp  # type: ignore
    from constants import GAME_NAME  # type: ignore

import Utils
from CommonClient import ClientCommandProcessor, CommonContext, get_base_parser, gui_enabled, handle_url_arg, \
    logger, server_loop
from NetUtils import ClientStatus

POLL_SECONDS = 0.5


class DevilSpireCommandProcessor(ClientCommandProcessor):
    def _cmd_savedir(self, path: str = "") -> bool:
        """Show or set the Devil Spire save directory (where ap_out.txt / ap_in.txt live)."""
        if path:
            p = Path(path).expanduser()
            if not p.is_dir():
                logger.error(f"Not a directory: {p}")
                return False
            self.ctx.set_save_dir(p)
        logger.info(f"Save dir: {self.ctx.save_dir}")
        return True

    def _cmd_apstatus(self) -> bool:
        """Show what the client currently knows (found locations, items written to ap_in.txt)."""
        c = self.ctx
        logger.info(f"save dir: {c.save_dir}; found locations: {len(c.found_locations)}; "
                    f"sent: {len(c.sent_locations)}; items in ap_in.txt: {len(c.in_writer.items) if c.in_writer else 0}; "
                    f"goal: {c.finished_game}")
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
        if self.slot_data:
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
            self.on_connected_setup()
        elif cmd == "ReceivedItems":
            self.refresh_items()
        elif cmd == "RoomUpdate":
            self.refresh_items()

    def on_connected_setup(self) -> None:
        """Called after Connected (and when the save dir changes): write config, sync identity, rewrite ap_in."""
        if self.save_dir is None or self.tailer is None or self.in_writer is None:
            return
        identity = {"seed": self.server_seed_name, "team": self.team, "slot": self.slot,
                    "name": self.auth, "base_id": self.slot_data.get("base_id")}
        old = fp.load_state(self.save_dir)
        if old.get("identity") != identity:
            # different multiworld/slot than the files were written for: forget stale checks, clear ap_out.txt
            if old.get("identity"):
                logger.info("New seed/slot detected for this save dir: clearing ap_out.txt and local state.")
            self.found_locations.clear()
            self.goal_seen = False
            self.tailer.truncate_file()
            self.in_writer.deaths.clear()
            fp.store_state(self.save_dir, {"identity": identity})
        try:
            if fp.write_config(self.save_dir, self.slot_data):
                logger.info("Wrote ap_config.ini (restart the game if it is already running; it is read at start).")
        except (OSError, KeyError) as e:
            logger.error(f"Could not write ap_config.ini: {e!r}")
        # catch-up: everything already in ap_out.txt (boss/floor checks persist across runs). DeathLink lines are
        # historic at this point and must NOT be re-sent.
        for ev in self.tailer.poll_events():
            self.handle_event(ev, replay=True)
        self.session_ready = True
        self.refresh_items(force=True)
        asyncio.create_task(self.flush_locations())

    def on_deathlink(self, data: dict) -> None:
        super().on_deathlink(data)
        if self.in_writer is not None and self.death_link:
            self.in_writer.add_death(data.get("cause") or f"DeathLink from {data.get('source', '?')}")
            self.write_in()

    # -- ap_in.txt --------------------------------------------------------------------------------------------
    def refresh_items(self, force: bool = False) -> None:
        if self.in_writer is None or self.slot is None:
            return
        items = []
        for it in self.items_received:
            try:
                name = self.item_names.lookup_in_game(it.item, self.game)
            except Exception:
                name = f"Item {it.item}"
            sender = self.player_names.get(it.player, f"Player {it.player}")
            items.append((it.item, name, sender))
        self.in_writer.items = items
        self.write_in(force)

    def write_in(self, force: bool = False) -> None:
        if self.in_writer is None:
            return
        try:
            self.in_writer.flush(force)
        except OSError as e:
            logger.error(f"Could not write ap_in.txt: {e!r}")

    # -- ap_out.txt -------------------------------------------------------------------------------------------
    def connected_to_slot(self) -> bool:
        return bool(self.slot is not None and self.server and self.server.socket and not self.server.socket.closed)

    def handle_event(self, ev: fp.OutEvent, replay: bool = False) -> None:
        if ev.kind == "L" and ev.location_id is not None:
            self.found_locations.add(ev.location_id)
        elif ev.kind == "G":
            self.goal_seen = True
        elif ev.kind == "D":
            if not replay and self.death_link and self.connected_to_slot():
                asyncio.create_task(self.send_death(f"{self.auth} {ev.text}".strip()))
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
