#!/bin/bash
# 同じ Spec・同じ seed を、プロセスを分けて N 回作る。1 回ごとに WAV を takes/ へ控える。
# 使い方: bash projects/longform/determinism/run.sh [N]
set -eu
cd "$(dirname "$0")/../../.."       # リポジトリの根
N=${1:-6}
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
OUT=projects/longform/assets/determinism/voice
TAKES=projects/longform/determinism/takes
mkdir -p "$OUT" "$TAKES"
for i in $(seq 1 "$N"); do
  PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/determinism --force \
    > /dev/null 2>&1
  cp "$OUT/det-s3.wav" "$TAKES/run-$i.wav"
  echo "run $i $(md5 -q "$TAKES/run-$i.wav")"
done
