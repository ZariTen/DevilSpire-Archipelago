#!/usr/bin/env bash
# Offline testing without the client: writes a sample ap_in.txt + ap_config.ini into the game's save dir.
# Usage: patch/make_test_ap_in.sh [save dir] [--reset]
#   --reset  also deletes the game-private state (ap_granted.txt, ap_souls_granted.txt) and ap_out.txt
# Item ids = base_id + 500 + code (worlds-src/devilspire/items.py). Existing files are kept as *.bak (once).
set -euo pipefail
default="$HOME/.local/share/Steam/steamapps/compatdata/2579370111/pfx/drive_c/users/steamuser/AppData/Roaming/Devil_Spire"
dir="$default"; reset=0
for a in "$@"; do case "$a" in --reset) reset=1;; *) dir="$a";; esac; done
mkdir -p "$dir"
BASE=38470000
for f in ap_in.txt ap_config.ini; do [ -f "$dir/$f" ] && [ ! -f "$dir/$f.bak" ] && cp "$dir/$f" "$dir/$f.bak" || true; done
cat > "$dir/ap_config.ini" <<CFG
[ap]
death_link=0
floor_check_step=1
base_id=$BASE
poll_frames=30
slot_id=offline-test:Tester
CFG
# idx|code|name   (sender = "Tester")
items=(
 "100|Orb of Strength" "102|Orb of Vitality" "103|Orb of Agility" "104|Stat Point"
 "110|Yellow Orb (Gold)" "111|Gold Hoard" "112|Blue Orb (Stone)" "113|Pouch of Souls"
 "120|Red Potion Pack" "121|Blue Potion Pack" "122|White Potion"
 "130|Spell Page (Basic)" "141|Weapon (Lv 50)" "144|Armor Piece (Lv 50)" "147|Accessory (Lv 50)"
 "149|Shield (Lv 25)" "151|Mystic Ring" "113|Pouch of Souls" "110|Yellow Orb (Gold)" "200|Ambush Trap"
)
tmp="$dir/ap_in.txt.tmp"; : > "$tmp"; i=0
for e in "${items[@]}"; do
  code="${e%%|*}"; name="${e#*|}"
  echo "I|$i|$((BASE + 500 + code))|$name|Tester" >> "$tmp"; i=$((i+1))
done
mv "$tmp" "$dir/ap_in.txt"
if [ "$reset" = 1 ]; then rm -f "$dir/ap_granted.txt" "$dir/ap_souls_granted.txt" "$dir/ap_out.txt"; echo "reset game-private AP state"; fi
echo "wrote $dir/ap_in.txt ($i items) and ap_config.ini"
