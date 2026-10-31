#!/usr/bin/env python
"""P2 の再測（枠外 10 種 × seed 1〜5）をまとめる。

1 種 1 seed の測定は、seed の揺れと演技の差を区別できない。ここでは同じ種を
5 seed で振り、「狙った向きへ動いた seed がいくつか」を数える。

  PYTHONPATH=. <venv> .../summarize_seeds.py projects/longform/acting/seeds.tsv
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict

import numpy as np

# 種ごとの狙い（P2 の設計）。向きは「小さいほど狙い通り」を down で書く。
TARGETS = {
    "tere": [("energy_median_db", "down")],
    "hiniku": [("f0_end_st_s", "down"), ("rate_mora_s", "down")],
    "akirame": [("energy_median_db", "down"), ("rate_mora_s", "down")],
    "kyosei": [("energy_median_db", "up")],
    "sasayaki": [("energy_median_db", "down")],
    "donari": [("energy_median_db", "up")],
    "nakijwarai": [("f0_range_st", "up")],
    "dokuhaku": [("energy_median_db", "down"), ("rate_mora_s", "down")],
    "hayakuchi": [("duration", "down")],
    "ma": [("duration", "up")],
}
ORDER = ["baseline"] + list(TARGETS)


def kind_of(path: str) -> str:
    name = path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    return name.rsplit("-s", 1)[0]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("tsv")
    ap.add_argument("--voice-dir", default=None,
                    help="WAV の置き場（音色を測る。既定は tsv と同じ作品の voice/）")
    args = ap.parse_args()

    with open(args.tsv, encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    data: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        data[kind_of(r["path"])].append(r)

    if "baseline" not in data:
        raise SystemExit("baseline が無い")
    base = data["baseline"]

    def col(rs, m):
        return np.array([float(r[m]) for r in rs])

    print(f"{args.tsv} — 1 種 {len(base)} seed・{len(data)} 種")
    print(f"{'種':10s} {'指標':16s} {'狙い':4s} {'基準線':>10s} {'種':>10s} "
          f"{'幅(基準)':>10s} {'幅(種)':>10s} {'向き'}")

    for kind in ORDER:
        if kind not in data:
            continue
        rs = data[kind]
        for metric, direction in TARGETS.get(kind, [("duration", "up")]):
            b = col(base, metric)
            k = col(rs, metric)
            bm, km = float(np.median(b)), float(np.median(k))
            ok = int((k < bm).sum()) if direction == "down" else int((k > bm).sum())
            print(f"{kind:10s} {metric:16s} {direction:4s} {bm:10.2f} {km:10.2f} "
                  f"{b.max() - b.min():10.2f} {k.max() - k.min():10.2f} "
                  f"{ok}/{len(k)}")

    print("\n参考：有声率（囁きは息が有声の外へ落ちる）")
    for kind in ("baseline", "sasayaki", "donari", "dokuhaku"):
        if kind in data:
            v = col(data[kind], "voiced_fraction")
            print(f"  {kind:10s} {np.median(v):.3f}（{v.min():.3f}–{v.max():.3f}）")

    # 音色（張りは peak 正規化で消えるが、息は帯域と平坦度に残る）
    if args.voice_dir:
        from semantic_audio_loom.skills import probe

        tim: dict[str, list[dict]] = defaultdict(list)
        for kind in data:
            for r in data[kind]:
                name = r["path"].rsplit("/", 1)[-1]
                path = f"{args.voice_dir.rstrip('/')}/{name}"
                try:
                    m = probe.measure(path)
                except FileNotFoundError:
                    continue
                m["_kind"] = kind
                tim[kind].append(m)
        if tim:
            print("\n音色（帯域の比と平坦度。5 seed の中央値）")
            print(f"{'種':10s} {'低':>7s} {'中':>7s} {'高':>7s} {'重心 Hz':>8s} {'平坦度':>8s}")
            for kind in ORDER:
                if kind not in tim:
                    continue
                ts = tim[kind]
                lo = np.median([t["bands_db"]["low"] for t in ts])
                mi = np.median([t["bands_db"]["mid"] for t in ts])
                hi = np.median([t["bands_db"]["high"] for t in ts])
                ce = np.median([t["centroid_hz"] for t in ts])
                fl = np.median([t["flatness"] for t in ts])
                print(f"{kind:10s} {lo:7.1f} {mi:7.1f} {hi:7.1f} {ce:8.0f} {fl:8.4f}")

    print("\n判定（向きが 5/5 の指標だけを「動いた」と呼ぶ）")
    for kind, targets in TARGETS.items():
        if kind not in data:
            continue
        moved, still = [], []
        for metric, direction in targets:
            b = col(base, metric)
            k = col(data[kind], metric)
            bm = float(np.median(b))
            ok = int((k < bm).sum()) if direction == "down" else int((k > bm).sum())
            (moved if ok == 5 else still).append(f"{metric}:{ok}/5")
        print(f"  {kind:10s} 動いた {', '.join(moved) or '—'} / 残り {', '.join(still) or '—'}")


if __name__ == "__main__":
    main()
