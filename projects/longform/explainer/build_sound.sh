#!/bin/zsh
# 解説動画の音（声の外）。章の印のチャイムと、下地のピアノ。
# 生成は 1 本ずつ・時間を timings.tsv に残す。失敗は 1 回だけ再試行。
set -u
cd /Users/user/AI創作工房/semantic-audio-loom || exit 1
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
TSV=projects/longform/timings.tsv

run() {  # run <stage> <asset> <model> <settings> <args...>
  local stage=$1 asset=$2 model=$3 settings=$4
  shift 4
  local st=$(date +%s) rc
  PYTHONPATH=. "$PY" "$@" > "/tmp/explainer-sound.log" 2>&1
  rc=$?
  local t=$(( $(date +%s) - st ))
  echo -e "2026-10-31\t${stage}\t${asset}\t${model}\t${settings}\t${t}\t-\tM2Pro-16GB\trc=${rc}" >> "$TSV"
  echo "$asset rc=$rc ${t}s"
  if [ $rc -ne 0 ]; then
    echo "--- log ---"; tail -5 /tmp/explainer-sound.log
  fi
}

run P3 explainer/sfx/chime stable_audio-open-1.0 "duration=3,seed=1" \
  bin/asset.py --type sfx --provider stable_audio --resolve rule --duration 3 --seed 1 \
  --prompt "A single soft glass bell chime, warm and gentle, a clear ringing onset with a natural decay, close and intimate, no music, no voice" \
  --project longform --scene explainer/sfx --name chime

run P3 explainer/sfx/door-soft stable_audio-open-1.0 "duration=1.6,seed=2" \
  bin/asset.py --type sfx --provider stable_audio --resolve rule --duration 1.6 --seed 2 \
  --prompt "A wooden interior door closing gently, a soft click of the latch and a quiet thud, close perspective, no music, no voice" \
  --project longform --scene explainer/sfx --name door-soft

run P3 explainer/sfx/door-slam stable_audio-open-1.0 "duration=2.2,seed=3" \
  bin/asset.py --type sfx --provider stable_audio --resolve rule --duration 2.2 --seed 3 \
  --prompt "A wooden door slammed shut hard, a sharp impact and rattling latch, close perspective, sudden, no music, no voice" \
  --project longform --scene explainer/sfx --name door-slam

run P3 explainer/bgm/underlay musicgen-small "duration=30,seed=1" \
  bin/asset.py --type bgm --provider musicgen --resolve rule --duration 30 --seed 1 \
  --prompt "A quiet understated felt piano piece, sparse slow notes, calm and curious, warm room tone, no drums, no vocals" \
  --project longform --scene explainer/bgm --name underlay
