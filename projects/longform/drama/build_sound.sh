#!/bin/zsh
# 演劇の音（声の外）。呼び出し音・切断音・夜の部屋の環境音。
set -u
cd /Users/user/AI創作工房/semantic-audio-loom || exit 1
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
TSV=projects/longform/timings.tsv

run() {
  local stage=$1 asset=$2 model=$3 settings=$4
  shift 4
  local st=$(date +%s) rc
  PYTHONPATH=. "$PY" "$@" > "/tmp/drama-sound.log" 2>&1
  rc=$?
  local t=$(( $(date +%s) - st ))
  echo -e "2026-10-31\t${stage}\t${asset}\t${model}\t${settings}\t${t}\t-\tM2Pro-16GB\trc=${rc}" >> "$TSV"
  echo "$asset rc=$rc ${t}s"
  if [ $rc -ne 0 ]; then echo "--- log ---"; tail -5 /tmp/drama-sound.log; fi
}

run P4 drama/sfx/ring stable_audio-open-1.0 "duration=4,seed=4" \
  bin/asset.py --type sfx --provider stable_audio --resolve rule --duration 4 --seed 4 \
  --prompt "A smartphone ringing on a desk at night, a soft synthetic ringtone repeating twice, close perspective, muffled room, no music, no voice" \
  --project longform --scene drama/sfx --name ring

run P4 drama/sfx/hangup stable_audio-open-1.0 "duration=1.5,seed=5" \
  bin/asset.py --type sfx --provider stable_audio --resolve rule --duration 1.5 --seed 5 \
  --prompt "A phone call ending, a short dull click and the line going dead, close perspective, quiet, no music, no voice" \
  --project longform --scene drama/sfx --name hangup

run P4 drama/bgm/underlay stable_audio-open-1.0 "duration=30,seed=6" \
  bin/asset.py --type ambience --provider stable_audio --resolve rule --duration 30 --seed 6 \
  --prompt "Very quiet bedroom at night, faint electrical hum from a charger, distant traffic through a closed window, no voices, no music, steady low ambience" \
  --project longform --scene drama/bgm --name underlay
