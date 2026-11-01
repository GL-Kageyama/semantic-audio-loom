#!/usr/bin/env python
"""長尺の組み立て（解説も演劇も同じ道具）。voice/ のキューを間で並べ、1 本にする。

- キュー頭尾の無音を切る（切らないと、置いた間が 1 秒ほど伸びる）
- 声量を gain_db で戻す。生成ファイルは peak 0.95 に揃うが、**ピークが揃っても大きさは揃わない**ので、
  有声部分の RMS を人ごとの中央値へ寄せる（同じ人の行は同じ大きさ。人どうしの差は残す）
- 効果音は <dir>/sfx.yaml、下地は assets/<work>/bgm/underlay.wav（全体長へ継ぎ足す）
- 章の印は <dir>/chapters.yaml（無ければ鳴らさない）
- 下地を止める区間は <dir>/bed_mute.yaml（「間」を聴かせる場面）

  PYTHONPATH=. <venv> .../assemble.py --dir projects/longform/explainer
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))          # projects/longform
REPO = os.path.dirname(os.path.dirname(HERE))              # リポジトリの根
sys.path.insert(0, REPO)

import wave

import numpy as np
import yaml

VOLUME_GAIN = {"whisper": -10.0, "quiet": -5.0, "normal": 0.0, "loud": 3.0, "shout": 6.0}
LEAD_IN = 1.2
TAIL = 2.5
_TRIM_DB = -50.0
_HEAD_KEEP = 0.02
_TAIL_KEEP = 0.06


def duration(path: str) -> float:
    with wave.open(path, "rb") as w:
        return w.getnframes() / float(w.getframerate())


def voiced_rms_db(path: str) -> float:
    """有声部分の RMS（dBFS）。

    ピークを 0.95 に揃えても、破裂音の強い行は RMS が低く、母音の続く行は高い。
    その差がそのまま「行ごとに声が大きい／小さい」として聞こえる。
    """
    with wave.open(path, "rb") as w:
        sr, ch = w.getframerate(), w.getnchannels()
        raw = w.readframes(w.getnframes())
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    a = a.reshape(-1, ch).mean(axis=1)
    if a.size == 0:
        return -90.0
    env = np.abs(a)
    thr = env.max() * 0.05                      # 息の漏れ・暗騒音を外す
    idx = np.where(env > thr)[0]
    seg = a[idx[0]:idx[-1] + 1] if idx.size else a
    return float(20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9))


def trim(src: str, dst_dir: str, name: str, force: bool = False) -> str:
    """キュー頭尾の無音を切る（閾値は他と同じ −50 dBFS）。"""
    dst = os.path.join(dst_dir, name + ".wav")
    if not force and os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
        return dst
    os.makedirs(dst_dir, exist_ok=True)
    with wave.open(src, "rb") as w:
        sr, ch, n, sw = w.getframerate(), w.getnchannels(), w.getnframes(), w.getsampwidth()
        raw = w.readframes(n)
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    a = a.reshape(-1, ch)
    loud = np.abs(a).max(axis=1) > 10 ** (_TRIM_DB / 20.0)
    if not loud.any():
        return src                      # 鳴っていないキューは切らずに渡す
    first = int(np.argmax(loud)) - int(_HEAD_KEEP * sr)
    last = len(loud) - int(np.argmax(loud[::-1])) + int(_TAIL_KEEP * sr)
    clipped = a[max(0, first): min(len(a), last)]
    with wave.open(dst, "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(sw)
        w.setframerate(sr)
        w.writeframes((np.clip(clipped, -1, 1) * 32767.0).astype(np.int16).tobytes())
    return dst


def tile_bed(src: str, dst: str, total_s: float, fade_s: float = 2.0) -> str:
    """短い bgm / 環境音を全体に敷く（継ぎ目はクロスフェード、頭尾はフェード）。"""
    with wave.open(src, "rb") as w:
        sr, ch, n = w.getframerate(), w.getnchannels(), w.getnframes()
        raw = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
    clip = raw.reshape(-1, ch)
    total = int(round(total_s * sr))
    out = np.zeros((total + int(fade_s * sr), ch), dtype=np.float32)
    fade = int(fade_s * sr)
    pos = 0
    while pos < len(out):
        end = min(pos + len(clip), len(out))
        seg = clip[: end - pos].copy()
        if pos > 0:
            ramp = np.linspace(0.0, 1.0, min(fade, len(seg)), dtype=np.float32)[:, None]
            seg[: len(ramp)] *= ramp
        out[pos:end] += seg
        pos += len(clip) - fade
    out = out[:total]
    out[:fade] *= np.linspace(0.0, 1.0, min(fade, len(out)), dtype=np.float32)[:, None]
    out[-fade:] *= np.linspace(1.0, 0.0, fade, dtype=np.float32)[:, None]
    with wave.open(dst, "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(out, -1, 1) * 32767.0).astype("<i2").tobytes())
    return dst


def mute_bed(path: str, spans: list, fade_s: float = 0.6) -> str:
    """下地を指定の区間だけ消す（「間」を演じる作品は、下地の音も止める）。

    消す区間は cue 名の対で書く（bed_mute.yaml）。境目は短く絞る。
    ここで消さないと、無音を聴かせる場面に部屋の音が残る。
    """
    if not spans:
        return path
    with wave.open(path, "rb") as w:
        sr, ch, n, sw = w.getframerate(), w.getnchannels(), w.getnframes(), w.getsampwidth()
        a = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
    a = a.reshape(-1, ch)
    f = max(1, int(fade_s * sr))
    for start, end in spans:
        i, j = max(0, int(start * sr)), min(len(a), int(end * sr))
        if j <= i:
            continue
        ramp = np.clip(np.minimum(np.arange(j - i), np.arange(j - i)[::-1]) / f, 0.0, 1.0)
        a[i:j] *= (1.0 - ramp)[:, None]
    with wave.open(path, "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(sw)
        w.setframerate(sr)
        w.writeframes((np.clip(a, -1, 1) * 32767.0).astype(np.int16).tobytes())
    return path


def apply_fx(src: str, character: str, cfg: dict, dst_dir: str, force: bool = False) -> tuple[str, float]:
    """声の加工（帯域・ピッチ。作品ごとの配色）。返り値は (パス, 追加利得 dB)。

    同じモデルから出た二人の声は、seed の揺れのほうが人物差より大きい
    （同じ台詞の MFCC 距離：同一人物 11.7〜13.2 / 別人 7.2）。
    人物を耳で分けるには、声そのもの以外の層で差を作る必要がある。
    """
    from scipy.signal import butter, sosfilt

    dst = os.path.join(dst_dir, os.path.splitext(os.path.basename(src))[0] + ".wav")
    if not force and os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
        return dst, float(cfg.get("gain_db", 0.0))
    os.makedirs(dst_dir, exist_ok=True)
    with wave.open(src, "rb") as w:
        sr, ch, n, sw = w.getframerate(), w.getnchannels(), w.getnframes(), w.getsampwidth()
        a = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
    a = a.reshape(-1, ch)
    nyq = sr / 2.0
    bands = []
    if cfg.get("highpass_hz"):
        bands.append(butter(4, cfg["highpass_hz"] / nyq, btype="highpass", output="sos"))
    if cfg.get("lowpass_hz"):
        bands.append(butter(4, min(cfg["lowpass_hz"] / nyq, 0.99), btype="lowpass", output="sos"))
    for sos in bands:
        a = sosfilt(sos, a, axis=0).astype(np.float32)
    # ピッチ（半音）。フォルマントも一緒に上がるので、声道の短い声になる。
    # 小さな機体のスピーカーらしさは、帯域よりこちらが効く。
    if cfg.get("pitch_semitones"):
        import librosa

        if ch != 1:
            raise ValueError("pitch_semitones はモノラルの声だけに対応する")
        a = librosa.effects.pitch_shift(a[:, 0], sr=sr,
                                        n_steps=float(cfg["pitch_semitones"]))[:, None]
    # 頭は揃えない（揃えると声量の差が消える）。帯域を削った分は gain_db で戻す。
    with wave.open(dst, "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(sw)
        w.setframerate(sr)
        w.writeframes((np.clip(a, -1, 1) * 32767.0).astype(np.int16).tobytes())
    return dst, float(cfg.get("gain_db", 0.0))


def shorten(src: str, dst: str, seconds: float, fade: float = 0.35) -> str:
    """長い効果音を切る（章の印は間の中に収める。台詞の上へはみ出させない）。"""
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
        return dst
    with wave.open(src, "rb") as w:
        sr, ch, n, sw = w.getframerate(), w.getnchannels(), w.getnframes(), w.getsampwidth()
        raw = w.readframes(n)
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    a = a.reshape(-1, ch)[: int(seconds * sr)].copy()
    f = min(int(fade * sr), len(a))
    a[-f:] *= np.linspace(1.0, 0.0, f, dtype=np.float32)[:, None]
    with wave.open(dst, "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(sw)
        w.setframerate(sr)
        w.writeframes((np.clip(a, -1, 1) * 32767.0).astype(np.int16).tobytes())
    return dst


def load_list(path: str) -> list:
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="作品の置き場（script.yaml の親）")
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--retrim", action="store_true", help="切った無音を作り直す")
    args = ap.parse_args()

    work = os.path.abspath(args.dir)
    name = os.path.basename(work.rstrip("/"))
    scene_path = os.path.join(work, "script.yaml")
    assets = os.path.join(HERE, "assets", name)
    voice, sfx_dir, bgm_dir = (os.path.join(assets, d) for d in ("voice", "sfx", "bgm"))
    trim_dir = os.path.join(assets, "voice_trim")

    with open(scene_path, encoding="utf-8") as f:
        scene = yaml.safe_load(f)
    default_pause = float(scene.get("default_pause", 0.0))
    chapters = set(load_list(os.path.join(work, "chapters.yaml")))
    fx_cfg = {}
    fx_path = os.path.join(work, "voice_fx.yaml")
    if os.path.exists(fx_path):
        with open(fx_path, encoding="utf-8") as f:
            fx_cfg = yaml.safe_load(f) or {}
    fx_dir = os.path.join(assets, "voice_fx")

    stems: list[dict] = []
    starts: dict[str, float] = {}
    ends: dict[str, float] = {}
    order: list[str] = []
    heads: list[float] = []
    cursor = LEAD_IN
    for cue in scene["cues"]:
        cue_name = cue.get("name") or ""
        path = os.path.join(voice, cue_name + ".wav")
        if not os.path.exists(path):
            sys.exit(f"声が無い: {path}")
        path = trim(path, trim_dir, cue_name, force=args.retrim)
        extra_gain = 0.0
        character = cue.get("character", "")
        if character in fx_cfg:
            path, extra_gain = apply_fx(path, character, fx_cfg[character], fx_dir,
                                        force=args.retrim)
        pause = cue.get("pause_before")
        cursor += default_pause if pause is None else float(pause)
        starts[cue_name] = cursor
        if cue_name in chapters:
            heads.append(cursor)
        stems.append({
            "file": os.path.relpath(path, work),
            "role": "voice",
            "start": round(cursor, 3),
            "gain_db": VOLUME_GAIN.get(cue.get("volume", "normal"), 0.0) + extra_gain,
            "_char": character,
        })
        cursor += duration(path)
        ends[cue_name] = cursor
        order.append(cue_name)

    # 声量のそろえ: 有声 RMS のばらつきを、人ごとの中央値へ寄せる。
    # 人どうしの差（ミライとミラボの地の大きさ）は残す——そろえるのは同じ人の中だけ。
    voice = [s for s in stems if s.get("role") == "voice"]
    for s in voice:
        s["_db"] = voiced_rms_db(os.path.join(work, s["file"]))
    by_char: dict[str, list[float]] = {}
    for s in voice:
        by_char.setdefault(s.get("_char", ""), []).append(s["_db"])
    med = {c: float(np.median(v)) for c, v in by_char.items()}
    for s in voice:
        s["gain_db"] = round(s["gain_db"] + med[s.get("_char", "")] - s["_db"], 2)
        s.pop("_db", None)
        s.pop("_char", None)
    for c, v in by_char.items():
        if len(v) >= 3:
            print(f"声量 {c or '?':<8} {len(v):>3}行 幅 {max(v) - min(v):.1f} dB → 中央値へ補正")

    total = cursor + TAIL

    # 章の頭の印（chapters.yaml がある作品だけ）
    chime = os.path.join(sfx_dir, "chime.wav")
    if heads and os.path.exists(chime):
        # 章の頭の間は 1〜3 秒。3 秒の鐘をそのまま置くと台詞に重なる。
        chime = shorten(chime, os.path.join(sfx_dir, "chime_short.wav"), 1.4)
        for i, start in enumerate(heads):
            stems.append({
                "file": os.path.relpath(chime, work),
                "role": "hit",
                "start": round(max(0.0, start - 1.6), 3),
                "gain_db": -4.0 + (2.0 if i == 0 else 0.0),
            })

    # 台詞に合わせて置く効果音（anchor の cue の頭から offset 秒）
    for hit in load_list(os.path.join(work, "sfx.yaml")):
        path = os.path.join(sfx_dir, hit["file"])
        anchor = starts.get(hit.get("anchor", ""))
        if anchor is None or not os.path.exists(path):
            print(f"skip sfx {hit.get('file')}（anchor={hit.get('anchor')}）")
            continue
        stems.append({
            "file": os.path.relpath(path, work),
            "role": "hit",
            "start": round(max(0.0, anchor + float(hit.get("offset", 0.0))), 3),
            "gain_db": float(hit.get("gain_db", 0.0)),
        })

    bed_src = os.path.join(bgm_dir, "underlay.wav")
    if os.path.exists(bed_src):
        bed = tile_bed(bed_src, os.path.join(bgm_dir, "underlay_tiled.wav"), total)
        holes = []
        for h in load_list(os.path.join(work, "bed_mute.yaml")):
            # gap_after: その cue の終わりから次の cue の頭まで（＝置いた間）
            if h.get("gap_after"):
                cue = h["gap_after"]
                if cue in ends and order.index(cue) + 1 < len(order):
                    holes.append((ends[cue], starts[order[order.index(cue) + 1]]))
                continue
            a, b = starts.get(h.get("from", "")), starts.get(h.get("to", ""))
            if a is not None and b is not None and b > a:
                holes.append((a, b))
        if holes:
            bed = mute_bed(bed, holes)
        stems.append({
            "file": os.path.relpath(bed, work),
            "role": "bed",
            "start": 0.0,
            "gain_db": -30.0,
        })

    spec = {
        "sample_rate": 44100,
        "output": name,
        "stems": stems,
        "duck": {"threshold_db": -30.0, "depth_db": 14.0, "attack_s": 0.03, "release_s": 0.45},
        "master_peak": 0.95,
    }
    mix_yaml = os.path.join(work, "mix.yaml")
    with open(mix_yaml, "w", encoding="utf-8") as f:
        f.write("# assemble.py が script.yaml と voice/ の実尺から書く（手で編集しない）\n")
        yaml.safe_dump(spec, f, allow_unicode=True, sort_keys=False)
    print(f"mix.yaml: {len(stems)} stems / {total:.1f}s")
    if args.no_render:
        return

    out = os.path.join(assets, "renders")
    os.makedirs(out, exist_ok=True)
    cmd = [sys.executable, os.path.join(REPO, "bin", "mix.py"), "--file", mix_yaml,
           "--out-dir", out, "--name", name]
    subprocess.run(cmd, check=True, cwd=REPO, env={**os.environ, "PYTHONPATH": "."})


if __name__ == "__main__":
    main()
