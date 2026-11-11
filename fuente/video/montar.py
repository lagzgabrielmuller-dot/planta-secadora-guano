"""Une los cuadros capturados con la música en un MP4 (H.264 + AAC).

    python montar.py <carpeta_de_cuadros> <fps> <salida.mp4> [--crf 20] [--ancho 1920] [--cada 2]

La música es _musica.mp3 (o la que se pase con --musica). El audio se corta con un fundido al final del video.
Con --cada 2 usa un cuadro de cada dos (de los cuadros a 60 fps sale una versión a 30 fps más liviana).
"""
import argparse
import glob
import os
import subprocess
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))


def ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


def main():
    a = argparse.ArgumentParser()
    a.add_argument("cuadros"); a.add_argument("fps", type=float); a.add_argument("salida")
    a.add_argument("--crf", type=int, default=20); a.add_argument("--ancho", type=int, default=0)
    a.add_argument("--musica", default=os.path.join(AQUI, "_musica.mp3")); a.add_argument("--preset", default="slow")
    a.add_argument("--kbps", type=int, default=0, help="tasa fija de video (para un archivo de tamaño acotado)")
    a.add_argument("--cada", type=int, default=1, help="usar un cuadro de cada n (fps de salida = fps / n)")
    a.add_argument("--pasadas", type=int, default=1, help="2 = dos pasadas con --kbps (mejor calidad al mismo tamaño)")
    a.add_argument("--audio", type=int, default=192, help="tasa del audio AAC en kbit/s")
    a.add_argument("--sin-audio", action="store_true", help="video mudo (versión pública: la música no es libre de derechos)")
    x = a.parse_args()
    # por número de cuadro (no por posición): sirve aunque falten los intermedios de un render a medias
    cuadros = [c for c in sorted(glob.glob(os.path.join(x.cuadros, "f_*.jpg")))
               if (int(os.path.basename(c)[2:8]) - 1) % x.cada == 0]
    n, fps = len(cuadros), x.fps / x.cada
    dur = n / fps
    tmp = tempfile.TemporaryDirectory()
    lista = os.path.join(x.cuadros, "f_%06d.jpg")
    if x.cada > 1:   # enlaces numerados de corrido para que ffmpeg lea la secuencia
        for i, c in enumerate(cuadros):
            os.symlink(os.path.abspath(c), os.path.join(tmp.name, f"f_{i + 1:06d}.jpg"))
        lista = os.path.join(tmp.name, "f_%06d.jpg")
    # los cuadros JPEG están en rango completo (0-255) y el video va en rango de TV (16-235): sin la conversión, el
    # ffmpeg nuevo marca el video como de rango completo y los reproductores que ignoran la marca lo ven más contrastado
    rango = "in_range=full:out_range=limited"
    vf = [f"scale={x.ancho}:-2:flags=lanczos:{rango}" if x.ancho else f"scale={rango}"]
    entrada = [ffmpeg(), "-y", "-v", "error", "-stats", "-framerate", str(fps), "-i", lista]
    video = ["-c:v", "libx264", "-preset", x.preset, "-pix_fmt", "yuv420p", "-color_range", "tv", "-profile:v", "high"]
    video += ["-b:v", f"{x.kbps}k", "-maxrate", f"{int(x.kbps * 1.5)}k", "-bufsize", f"{x.kbps * 2}k"] if x.kbps else ["-crf", str(x.crf)]
    video += ["-vf", ",".join(vf)]
    if x.pasadas == 2 and x.kbps:   # primera pasada: solo analiza el video y guarda las estadísticas
        log = ["-passlogfile", os.path.join(tmp.name, "x264")]
        subprocess.run(entrada + video + log + ["-pass", "1", "-an", "-f", "mp4", os.devnull], check=True)
        video += log + ["-pass", "2"]
    if x.sin_audio:
        cmd = entrada + ["-map", "0:v", "-t", f"{dur:.3f}"] + video + ["-an", "-movflags", "+faststart", x.salida]
    else:
        cmd = entrada + ["-i", x.musica, "-map", "0:v", "-map", "1:a", "-t", f"{dur:.3f}"] + video + [
            "-c:a", "aac", "-b:a", f"{x.audio}k", "-af", f"afade=t=out:st={max(0, dur - 2.5):.2f}:d=2.5",
            "-movflags", "+faststart", x.salida]
    subprocess.run(cmd, check=True)
    tmp.cleanup()
    print(f"{x.salida}: {n} cuadros, {dur:.1f} s, {os.path.getsize(x.salida) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
