#!/usr/bin/env python3
import subprocess
import sys
import time
import platform
import os

IS_WINDOWS = platform.system().lower().startswith('win')
IS_ANDROID = 'android' in platform.platform().lower() or 'termux' in os.getenv("PREFIX", "").lower()
USE_COLOR = not IS_WINDOWS

R = '\033[1;31m' if USE_COLOR else ''
G = '\033[1;32m' if USE_COLOR else ''
Y = '\033[1;33m' if USE_COLOR else ''
C = '\033[1;36m' if USE_COLOR else ''
N = '\033[0m' if USE_COLOR else ''

DOWNLOAD_DIR = (
    os.path.expanduser("~/Downloads")
    if IS_WINDOWS else "/sdcard/Download"
    if IS_ANDROID else os.path.expanduser("~/Downloads")
)

RESOLUTION_MAP = {
    "140": "140",
    "360": "bv*[height<=360]+ba/best[height<=360]",
    "480": "bv*[height<=480]+ba/best[height<=480]",
    "720": "bv*[height<=720]+ba/best[height<=720]",
    "1080": "bv*[height<=1080]+ba/best[height<=1080]",
}

def typing(text, delay=0.004):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def banner():
    print(f"{C}Youtube Downloader")
    print(f"• version : 1.2")
    print(f"• author  : Zidan")
    print(f"• github  : https://github.com/zidanXcode{N}")
    print(f"• platform: {platform.system()} - {platform.release()}\n")

def auto_update_ytdlp():
    try:
        typing(f"{C}[•] Mengecek pembaruan yt-dlp...{N}")
        subprocess.run(["yt-dlp", "-U"], check=True)
    except Exception as e:
        print(f"{R}[!] Gagal memperbarui yt-dlp: {e}{N}")

def is_url(text):
    return text.startswith("http://") or text.startswith("https://")

def search_youtube(query):
    print(f"{C}[•] Mencari video: {query}{N}")
    try:
        result = subprocess.run(
            ["yt-dlp", "--no-cache-dir", f"ytsearch1:{query}", "--print", "%(title)s ||| %(webpage_url)s ||| %(duration_string)s ||| %(uploader)s"],
            capture_output=True, text=True, timeout=30, check=True
        )
        line = result.stdout.strip().split(" ||| ")
        if len(line) == 4:
            title, url, duration, uploader = line
            print(f"\n{Y}Judul     :{N} {title}")
            print(f"{Y}Durasi    :{N} {duration}")
            print(f"{Y}Channel   :{N} {uploader}")
            print(f"{Y}Link      :{N} {url}")
            return url
    except Exception as e:
        print(f"{R}[!] Error saat pencarian: {e}{N}")
    return None

def get_playlist_info(url):
    try:
        result = subprocess.run(
            ["yt-dlp", "--flat-playlist", "--print", "%(title)s", url],
            capture_output=True, text=True, timeout=30, check=True
        )
        videos = result.stdout.strip().splitlines()
        return videos
    except Exception as e:
        print(f"{R}[!] Gagal mengambil info playlist: {e}{N}")
        return []

def download_by_resolution(url, resolution_choice, extra_args=None):
    format_str = RESOLUTION_MAP.get(resolution_choice)
    if not format_str:
        print(f"{R}[!] Resolusi tidak dikenali.{N}")
        return

    extra_args = extra_args or []
    output_template = os.path.join(DOWNLOAD_DIR, "%(title).60s.%(ext)s")
    cmd = [
        "yt-dlp", "--no-cache-dir", "--ignore-errors",
        "--continue", "--no-warnings",
        "-f", format_str, "-o", output_template,
        url
    ] + extra_args

    typing(f"\n{C}[•] Mendownload video resolusi {resolution_choice}p...{N}")
    try:
        subprocess.run(cmd, timeout=600)
        typing(f"\n{G}[✓] Selesai! Cek folder: {DOWNLOAD_DIR}{N}")
    except subprocess.TimeoutExpired:
        print(f"{R}[!] Waktu download habis.{N}")
    except FileNotFoundError:
        print(f"{R}[!] yt-dlp tidak ditemukan!{N}")

def download_audio(url, extra_args=None):
    extra_args = extra_args or []
    output_template = os.path.join(DOWNLOAD_DIR, "%(title).60s.%(ext)s")
    cmd = [
        "yt-dlp", "--no-cache-dir", "--ignore-errors",
        "--continue", "--no-warnings",
        "-x", "--audio-format", "mp3",
        "--audio-quality", "0",
        "-o", output_template,
        url
    ] + extra_args

    typing(f"\n{C}[•] Download Audio...{N}")
    try:
        subprocess.run(cmd, timeout=600)
        typing(f"\n{G}[✓] Selesai! Cek folder: {DOWNLOAD_DIR}{N}")
    except subprocess.TimeoutExpired:
        print(f"{R}[!] Download audio terlalu lama, dibatalkan.{N}")
    except FileNotFoundError:
        print(f"{R}[!] yt-dlp tidak ditemukan!{N}")

def main():
    auto_update_ytdlp()
    while True:
        banner()
        try:
            raw = input(f"{Y}[?] Masukkan URL / Judul ('exit' untuk keluar): {N}").strip()
        except EOFError:
            break

        if raw.lower() in ['exit', 'keluar', 'x']:
            print(f"{C}Keluar dari program...{N}")
            break

        url = raw if is_url(raw) else search_youtube(raw)
        if not url:
            continue

        extra_args = []
        is_playlist = "playlist?" in url or "list=" in url
        if is_playlist:
            video_list = get_playlist_info(url)
            total = len(video_list)
            print(f"\n{C}Playlist terdeteksi: {total} video ditemukan.{N}")
            preview = "\n".join([f"{i+1}. {title}" for i, title in enumerate(video_list[:5])])
            print(f"{Y}Contoh video dalam playlist:\n{preview}{N}")

            confirm = input(f"{Y}[?] Mau download semua ({total} video)? [Y/n]: {N}").strip().lower()
            if confirm == "n":
                max_videos = input(f"{Y}[?] Berapa video yang ingin di-download? (1-{total}): {N}").strip()
                if max_videos.isdigit() and 1 <= int(max_videos) <= total:
                    extra_args = ["--playlist-end", str(max_videos)]
                else:
                    print(f"{R}[!] Input tidak valid. Membatalkan...{N}")
                    continue

        print(f"\n{C}[1] Download Video (pilih resolusi)")
        print(f"[2] Download Audio (.mp3)")
        print(f"[x] Batal{N}")
        mode = input(f"{Y}[?] Pilihan: {N}").strip()

        if mode == "1":
            print(f"\n{C}Pilih resolusi video:")
            for r in RESOLUTION_MAP.keys():
                print(f"• {r}p")
            resolution_choice = input(f"{Y}[?] Resolusi (misal 480): {N}").strip()
            download_by_resolution(url, resolution_choice, extra_args)
        elif mode == "2":
            download_audio(url, extra_args)
        elif mode.lower() in ["x", "exit", "keluar"]:
            print(f"{C}Dibatalkan...{N}")
        else:
            print(f"{R}[!] Pilihan tidak valid.{N}")

        input(f"\n{Y}Tekan Enter untuk lanjut...{N}")
        print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C}Keluar dari program...{N}")
        sys.exit(0)
