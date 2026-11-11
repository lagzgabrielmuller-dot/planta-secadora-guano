"""Ritmo de la música del video: pulsos (beats), compases y partes de la canción -> datos/ritmo.json.

    python ritmo.py musica.mp3

Envolvente de ataques por flujo espectral; el período del pulso sale de la autocorrelación y la fase del pulso
de la grilla que más energía de ataque junta. Las partes (intro, estrofa, estribillo…) se marcan por la energía
RMS en ventanas de un compás.
"""
import json
import os
import subprocess
import sys

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
SR, HOP, N = 22050, 256, 2048


def ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


def main(ruta):
    pcm = subprocess.run([ffmpeg(), "-v", "error", "-i", ruta, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768
    dur = len(x) / SR
    fr = np.lib.stride_tricks.sliding_window_view(x, N)[::HOP]
    S = np.log1p(10 * np.abs(np.fft.rfft(fr * np.hanning(N).astype(np.float32), axis=1)))
    env = np.concatenate([[0], np.maximum(0, np.diff(S, axis=0)).sum(1)])
    env = (env - np.convolve(env, np.ones(32) / 32, "same")).clip(0)
    fps = SR / HOP
    # período: autocorrelación en 60-180 pulsos por minuto
    ac = np.correlate(env, env, "full")[len(env) - 1:]
    lags = np.arange(len(ac)) / fps
    ok = (lags > 60 / 180) & (lags < 60 / 60)
    per = lags[ok][np.argmax(ac[ok])]
    # refinamiento fino del período y fase
    mejor = (0, per, 0)
    for p in np.linspace(per * 0.995, per * 1.005, 41):
        for fase in np.linspace(0, p, 64, endpoint=False):
            idx = ((np.arange(fase, dur, p)) * fps).astype(int)
            idx = idx[idx < len(env)]
            s = env[idx].sum()
            if s > mejor[0]:
                mejor = (s, p, fase)
    _, per, fase = mejor
    pulsos = np.arange(fase, dur, per)
    # compás de 4: el desfase que más energía junta en el primer tiempo
    k = int(np.argmax([env[(pulsos[i::4] * fps).astype(int).clip(0, len(env) - 1)].sum() for i in range(4)]))
    compases = pulsos[k::4]
    rms = np.array([np.sqrt(np.mean(x[int(a * SR):int(b * SR)] ** 2)) for a, b in zip(compases[:-1], compases[1:])])
    datos = {"duracion": round(dur, 3), "bpm": round(60 / per, 2), "periodo": round(per, 5),
             "pulsos": [round(float(v), 3) for v in pulsos], "compases": [round(float(v), 3) for v in compases],
             "energia_compas": [round(float(v), 4) for v in rms]}
    os.makedirs(os.path.join(AQUI, "datos"), exist_ok=True)
    json.dump(datos, open(os.path.join(AQUI, "datos", "ritmo.json"), "w"))
    print(f"duración {dur:.1f} s · {60 / per:.2f} bpm · {len(pulsos)} pulsos · {len(compases)} compases")
    for i, (t, e) in enumerate(zip(compases, rms)):
        print(f"{i:3d} {t:7.2f}s {'#' * int(e * 140)}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "_musica.mp3"))
