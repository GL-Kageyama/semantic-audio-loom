#!/usr/bin/env python
"""感情の効きは、seed の揺れを超えるか（真白・同じ 1 行「明日、また来るね。」）。

5 感情（neutral / joy / anger / sadness / fear）× seed 1〜3 = 15 本。
強度・声量・速さ・型はそろえてあるので、動きの出どころは感情と seed だけ。

  PYTHONPATH=. <venv> .../measure_emotion_seed.py

出すもの:
- 15 本の指標（act_probe）
- 感情ごとの平均と、seed 3 本の幅（同じ感情の中でどこまで動くか）
- 一元配置の分散分析（要因＝感情、誤差＝seed）——F と p=0.05 の境目
- 感情の重心どうしの音色距離と、同じ感情の seed どうしの距離（同じ物差しで比べる）
"""
from __future__ import annotations

import itertools
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "projects", "longform"))   # measure_*.py はここ

import numpy as np

from semantic_audio_loom.skills.act_probe import measure as probe
from measure_envelope import distance, envelope
from measure_timbre import fingerprint

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE = os.path.join(os.path.dirname(HERE), "assets", "emotion-seed", "voice")

EMOTIONS = ["neutral", "joy", "anger", "sadness", "fear"]
SEEDS = [1, 2, 3]
# 台詞 2 行。名前の頭（空 = 1 行目 / "l2-" = 2 行目）。
LINES = [("1 行目「明日、また来るね。」", ""),
         ("2 行目「そんなこと、ないよ。」", "l2-")]
METRICS = [
    ("f0_median_hz", "f0 中央値 Hz"),
    ("f0_range_st", "抑揚 st"),
    ("rate_mora_s", "速さ mora/s"),
    ("pause_ratio", "間"),
    ("energy_median_db", "energy dB"),
    ("voiced_fraction", "有声率"),
]

# F(4, 10) の 5% 点。これより大きければ「感情の差は seed の揺れより大きい」と言える。
F_CRIT_05 = 3.478


def f_path(emotion: str, seed: int, prefix: str = "") -> str:
    return os.path.join(VOICE, f"{prefix}{emotion}-s{seed}.wav")


def anova(groups: list[np.ndarray]) -> tuple[float, float, float]:
    """一元配置。返り値は (F, SS_between, SS_within)。"""
    k = len(groups)
    n = sum(len(g) for g in groups)
    grand = float(np.mean(np.concatenate(groups)))
    ss_b = sum(len(g) * (float(np.mean(g)) - grand) ** 2 for g in groups)
    ss_w = sum(float(np.sum((g - np.mean(g)) ** 2)) for g in groups)
    f = (ss_b / (k - 1)) / (ss_w / (n - k)) if ss_w > 0 else float("inf")
    return f, ss_b, ss_w


def anova_blocked(mat: np.ndarray) -> dict:
    """反復のない二因子（行＝感情・列＝seed）。seed をブロックとして除いてから感情を見る。

    seed は拡散のノイズを決めるだけなので、seed の効きは「同じ台詞でも seed で
    これだけ動く」という揺れの見積もりになる。返り値は SS と F と寄与率（η²）。
    """
    r, c = mat.shape
    grand = float(mat.mean())
    row = mat.mean(axis=1)      # 感情ごと
    col = mat.mean(axis=0)      # seed ごと
    ss_emo = float(c * np.sum((row - grand) ** 2))
    ss_seed = float(r * np.sum((col - grand) ** 2))
    resid = mat - row[:, None] - col[None, :] + grand
    ss_err = float(np.sum(resid ** 2))
    ss_tot = ss_emo + ss_seed + ss_err
    df_err = (r - 1) * (c - 1)
    ms_err = ss_err / df_err
    return {
        "F_emo": (ss_emo / (r - 1)) / ms_err if ms_err else float("inf"),
        "F_seed": (ss_seed / (c - 1)) / ms_err if ms_err else float("inf"),
        "eta_emo": ss_emo / ss_tot if ss_tot else 0.0,
        "eta_seed": ss_seed / ss_tot if ss_tot else 0.0,
        "eta_err": ss_err / ss_tot if ss_tot else 0.0,
    }


def run(title: str, prefix: str) -> None:
    print(f"\n==== {title} ====")
    missing = [f_path(e, s, prefix) for e in EMOTIONS for s in SEEDS
               if not os.path.exists(f_path(e, s, prefix))]
    if missing:
        sys.exit("先に build_voice.py --dir projects/longform/emotion-seed を走らせる:\n  "
                 + "\n  ".join(missing))

    rows: dict[tuple[str, int], dict] = {}
    for e in EMOTIONS:
        for s in SEEDS:
            rows[(e, s)] = probe(f_path(e, s, prefix))

    print(f"{'':14s} {'f0':>7s} {'抑揚':>6s} {'速さ':>6s} {'間':>6s} {'energy':>7s} {'有声':>6s}")
    for (e, s), m in rows.items():
        print(f"{e + ' s' + str(s):14s} {m['f0_median_hz']:7.1f} {m['f0_range_st']:6.1f} "
              f"{m['rate_mora_s']:6.1f} {m['pause_ratio']:6.3f} "
              f"{m['energy_median_db']:7.1f} {m['voiced_fraction']:6.3f}")

    # --- 感情ごとの平均と、seed の幅 -----------------------------------------
    print(f"\n{'感情':10s} {'f0 平均':>8s} {'seed 幅':>8s} {'抑揚 平均':>9s} {'幅':>6s} "
          f"{'速さ 平均':>9s} {'幅':>6s}")
    means: dict[str, dict[str, float]] = {}
    spans: dict[str, dict[str, float]] = {}
    for e in EMOTIONS:
        vals = {k: np.array([rows[(e, s)][k] for s in SEEDS], dtype=float)
                for k, _ in METRICS}
        means[e] = {k: float(v.mean()) for k, v in vals.items()}
        spans[e] = {k: float(v.max() - v.min()) for k, v in vals.items()}
        print(f"{e:10s} {means[e]['f0_median_hz']:8.1f} {spans[e]['f0_median_hz']:8.1f} "
              f"{means[e]['f0_range_st']:9.1f} {spans[e]['f0_range_st']:6.1f} "
              f"{means[e]['rate_mora_s']:9.1f} {spans[e]['rate_mora_s']:6.1f}")

    mean_span = {k: float(np.mean([spans[e][k] for e in EMOTIONS])) for k, _ in METRICS}
    emo_span = {k: float(max(means[e][k] for e in EMOTIONS)
                         - min(means[e][k] for e in EMOTIONS)) for k, _ in METRICS}

    # --- 分散分析 -----------------------------------------------------------
    print(f"\n{'指標':12s} {'感情の幅':>9s} {'seed の幅':>9s} {'比':>6s} {'F(4,10)':>8s} {'判定':>6s}")
    for k, label in METRICS:
        groups = [np.array([rows[(e, s)][k] for s in SEEDS], dtype=float)
                  for e in EMOTIONS]
        f, _, _ = anova(groups)
        ratio = emo_span[k] / mean_span[k] if mean_span[k] > 0 else float("inf")
        verdict = "超える" if f > F_CRIT_05 else "超えない"
        print(f"{label:12s} {emo_span[k]:9.2f} {mean_span[k]:9.2f} {ratio:6.1f} "
              f"{f:8.2f} {verdict:>6s}")

    # --- seed をブロックにした二因子（反復なし）----------------------------
    # 一元配置は seed の揺れを誤差に混ぜるので、感情が見えなくなる。seed を
    # ブロックとして先に除くと、感情の効きそのものを検定できる。
    print(f"\nseed をブロックにした二因子（F の境目：感情 F(4,8)=3.84／seed F(2,8)=4.46）")
    print(f"{'指標':12s} {'F 感情':>8s} {'F seed':>8s} {'η² 感情':>9s} {'η² seed':>9s} {'η² 残り':>9s}")
    for k, label in METRICS:
        mat = np.array([[rows[(e, s)][k] for s in SEEDS] for e in EMOTIONS], dtype=float)
        r = anova_blocked(mat)
        print(f"{label:12s} {r['F_emo']:8.2f} {r['F_seed']:8.2f} "
              f"{r['eta_emo']:9.2f} {r['eta_seed']:9.2f} {r['eta_err']:9.2f}")

    # 感情の並びが seed をまたいで同じか（低い順）
    print("\nf0 の低い順（seed ごと）")
    for s in SEEDS:
        order = sorted(EMOTIONS, key=lambda e: rows[(e, s)]["f0_median_hz"])
        vals = " < ".join(f"{e} {rows[(e, s)]['f0_median_hz']:.0f}" for e in order)
        print(f"  s{s}: {vals}")

    # seed を 1 つに固定したときの感情の幅（作品の中はこれ。全キュー seed 1）
    prof = {s: np.array([rows[(e, s)]["f0_median_hz"] for e in EMOTIONS], dtype=float)
            for s in SEEDS}
    print("  seed を固定したときの感情の幅: "
          + " / ".join(f"s{s} {prof[s].max() - prof[s].min():.1f} Hz" for s in SEEDS))
    print("  seed どうしの並びの一致（順位相関 ρ）: "
          + " / ".join(f"s{a}–s{b} {np.corrcoef(np.argsort(np.argsort(prof[a])),
                                                np.argsort(np.argsort(prof[b])))[0, 1]:.2f}"
                       for a, b in itertools.combinations(SEEDS, 2)))

    # --- 音色：感情の重心どうし vs seed どうし -------------------------------
    env = {(e, s): envelope(f_path(e, s, prefix)) for e in EMOTIONS for s in SEEDS}
    fp = {(e, s): fingerprint(f_path(e, s, prefix)) for e in EMOTIONS for s in SEEDS}

    def mfcc(a, b) -> float:
        return float(np.linalg.norm(fp[a] - fp[b]))

    within = {}
    for e in EMOTIONS:
        vals = [mfcc((e, a), (e, b)) for a, b in itertools.combinations(SEEDS, 2)]
        within[e] = float(np.mean(vals))
    def centroid(e):
        return np.mean([fp[(e, s)] for s in SEEDS], axis=0)
    cent = {e: centroid(e) for e in EMOTIONS}
    between = {}
    for a, b in itertools.combinations(EMOTIONS, 2):
        between[(a, b)] = float(np.linalg.norm(cent[a] - cent[b]))

    all_within = list(within.values())
    all_between = list(between.values())
    print(f"\n音色（MFCC・有声フレーム）")
    print(f"  同じ感情で seed を替える: 平均 {np.mean(all_within):5.2f} "
          f"（{min(all_within):.2f}〜{max(all_within):.2f}）")
    print(f"  感情の重心どうし（seed 3 本の平均）: 中央 {np.median(all_between):5.2f} "
          f"（{min(all_between):.2f}〜{max(all_between):.2f}）")
    lo = min(between, key=between.get)
    hi = max(between, key=between.get)
    print(f"  いちばん近い対 {lo[0]}↔{lo[1]} {between[lo]:.2f} / "
          f"いちばん遠い対 {hi[0]}↔{hi[1]} {between[hi]:.2f}")

    # 同じ seed の中だけで見た感情の距離（種をそろえた比較）
    same_seed = {}
    for s in SEEDS:
        vals = [mfcc((a, s), (b, s)) for a, b in itertools.combinations(EMOTIONS, 2)]
        same_seed[s] = float(np.mean(vals))
    print(f"  同じ seed の中で感情を替える: 平均 "
          + " / ".join(f"s{s} {v:.2f}" for s, v in same_seed.items()))

    # 包絡は「声質」のもう 1 本の計器
    env_within = []
    for e in EMOTIONS:
        env_within += [distance(env[(e, a)], env[(e, b)])
                       for a, b in itertools.combinations(SEEDS, 2)]
    env_between = [distance(env[(a, s)], env[(b, s)])
                   for s in SEEDS for a, b in itertools.combinations(EMOTIONS, 2)]
    print(f"  包絡 dB — 同じ感情で seed どうし 平均 {np.mean(env_within):.2f} / "
          f"同じ seed の中で感情を替える 平均 {np.mean(env_between):.2f}")


def three_way(arr: np.ndarray) -> dict:
    """台詞 × 感情 × seed の加算モデル（反復なし）。arr の形は (行, 感情, seed)。

    誤差の自由度は (2-1)(5-1)(3-1) = 8。交互作用は誤差に飲ませる。
    """
    l, e, s = arr.shape
    grand = float(arr.mean())
    ml, me, ms = arr.mean(axis=(1, 2)), arr.mean(axis=(0, 2)), arr.mean(axis=(0, 1))
    ss_l = float(e * s * np.sum((ml - grand) ** 2))
    ss_e = float(l * s * np.sum((me - grand) ** 2))
    ss_s = float(l * e * np.sum((ms - grand) ** 2))
    ss_tot = float(np.sum((arr - grand) ** 2))
    ss_err = ss_tot - ss_l - ss_e - ss_s
    df_err = (l - 1) * (e - 1) * (s - 1)
    ms_err = ss_err / df_err
    return {
        "F_line": (ss_l / (l - 1)) / ms_err,
        "F_emo": (ss_e / (e - 1)) / ms_err,
        "F_seed": (ss_s / (s - 1)) / ms_err,
        "eta": (ss_l / ss_tot, ss_e / ss_tot, ss_s / ss_tot, ss_err / ss_tot),
    }


def main() -> None:
    for title, prefix in LINES:
        run(title, prefix)

    print("\n==== 台詞 2 行をまとめた三因子（F の境目：台詞 F(1,8)=5.32・"
          "感情 F(4,8)=3.84・seed F(2,8)=4.46）====")
    print(f"{'指標':12s} {'F 台詞':>8s} {'F 感情':>8s} {'F seed':>8s} "
          f"{'η² 台詞':>8s} {'η² 感情':>8s} {'η² seed':>8s} {'η² 残り':>8s}")
    for k, label in METRICS:
        arr = np.array([[[probe(f_path(e, s, p))[k] for s in SEEDS]
                         for e in EMOTIONS] for _, p in LINES], dtype=float)
        r = three_way(arr)
        el, ee, es, er = r["eta"]
        print(f"{label:12s} {r['F_line']:8.2f} {r['F_emo']:8.2f} {r['F_seed']:8.2f} "
              f"{el:8.2f} {ee:8.2f} {es:8.2f} {er:8.2f}")


if __name__ == "__main__":
    main()
