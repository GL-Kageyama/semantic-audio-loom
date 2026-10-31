#!/bin/zsh
# P2 演技の端 — 喜怒哀楽の枠の外を 10 種。同じ人物・同じ台詞・同じ seed で振る。
#
# 直すのは機構側（prompts / provider の散文 / Spec）だけ。WAV は手で直さない。
# 測るのは bin/act_probe.py。狙った方向へ動いたかを 1 種ずつ数える。
set -u
cd /Users/user/AI創作工房/semantic-audio-loom || exit 1
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
LINE="明日、また来るね。"

while IFS='|' read -r name emotion intensity volume speed delivery breathiness subtext; do
  [ -z "$name" ] && continue
  st=$(date +%s)
  PYTHONPATH=. "$PY" bin/generate.py --character mashiro --line "$LINE" \
    --emotion "$emotion" --intensity "$intensity" --volume "$volume" --speed "$speed" \
    --delivery "$delivery" --breathiness "$breathiness" --subtext "$subtext" \
    --seed 1 --resolve rule --project longform --scene acting-p2 --name "$name" \
    --provider tsukasa > "/tmp/p2-$name.log" 2>&1
  rc=$?
  t=$(( $(date +%s) - st ))
  echo -e "2026-10-31\tP2\tacting-p2/${name}\ttsukasa\temotion=${emotion},intensity=${intensity},volume=${volume},speed=${speed},delivery=${delivery},breathiness=${breathiness},seed=1\t${t}\t-\tM2Pro-16GB\trc=${rc}" >> projects/longform/timings.tsv
  echo "$name rc=$rc ${t}s"
done <<'TABLE'
baseline|neutral|moderate|normal|natural|controlled|none|基準線（演技を付けない）
tere|joy|subtle|quiet|natural|gentle|slight|照れ隠しに目を逸らしながら、素っ気なく
hiniku|calm|subtle|normal|slow|cold|none|褒めているふりをして、見下している
akirame|sadness|subtle|quiet|slow|flat|slight|もう期待していない。諦めて、静かに
kyosei|confidence|strong|loud|natural|aggressive|none|弱さを見せまいと、わざと大きく
sasayaki|neutral|subtle|whisper|slow|intimate|heavy|誰にも聞こえない距離で
donari|anger|strong|shout|fast|aggressive|none|怒りを叩きつける
nakijwarai|joy|subtle|normal|natural|desperate|heavy|泣きながら、無理に笑って
dokuhaku|loneliness|subtle|quiet|slow|intimate|slight|誰もいない部屋で、自分に言う
hayakuchi|anxiety|moderate|normal|very_fast|hesitant|slight|急いで、言葉が重なる
ma|sadness|moderate|quiet|very_slow|restrained|slight|言いかけて飲み込み、長い間を置く
TABLE
