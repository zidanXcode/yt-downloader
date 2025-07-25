#!/usr/bin/env python3
import subprocess
import sys
import time
import platform
import os

IS_WINDOWS = platform.system().lower().startswith('win')
USE_COLOR = not IS_WINDOWS

R = '\033[1;31m' if USE_COLOR else ''
G = '\033[1;32m' if USE_COLOR else ''
Y = '\033[1;33m' if USE_COLOR else ''
C = '\033[1;36m' if USE_COLOR else ''
N = '\033[0m' if USE_COLOR else ''

def typing(text, delay=0.004):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def banner():
    print(f"{C}Youtube Downloader")
    print(f"• version : 1.0")
    print(f"• author  : Zidan")
    print(f"• github  : https://github.com/zidanXcode{N}")
    print(f"• platform: {platform.system()} - {platform.release()}\n")

def auto_update_ytdlp():
    try:
        typing(f"{C}[•] Mengecek pembaruan yt-dlp...{N}")
        subprocess.run(["yt-dlp", "-U"], check=True)
    except subprocess.CalledProcessError:
        print(f"{R}[!] Gagal mengecek pembaruan yt-dlp.{N}")
    except FileNotFoundError:
        print(f"{R}[!] yt-dlp tidak ditemukan. Pastikan yt-dlp sudah terinstall.{N}")

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
        else:
            print(f"{R}[!] Gagal mendapatkan hasil.{N}")
    except subprocess.TimeoutExpired:
        print(f"{R}[!] Timeout saat mencari video.{N}")
    except subprocess.CalledProcessError:
        print(f"{R}[!] Error saat pencarian YouTube.{N}")
    except FileNotFoundError:
        print(f"{R}[!] yt-dlp tidak ditemukan. Pastikan yt-dlp sudah terinstall.{N}")
    return None

def download_video(url):
    output_path = os.path.expanduser("~/Downloads/%(title).60s.%(ext)s") if IS_WINDOWS else "/sdcard/Download/%(title).60s.%(ext)s"
    cmd = [
        "yt-dlp",
        "--no-cache-dir",
        "--ignore-errors",
        "--continue",
        "--no-warnings",
        "--merge-output-format", "mp4",
        "-f", "bv*[ext=mp4][height<=1080][vcodec^=avc1]+ba[ext=m4a]/bestvideo[height<=1080]+bestaudio",
        "-o", output_path,
        url
    ]
    typing(f"\n{C}[•] Download Video...{N}")
    try:
        subprocess.run(cmd, timeout=600)
    except subprocess.TimeoutExpired:
        print(f"{R}[!] Download video terlalu lama, dibatalkan.{N}")
    except FileNotFoundError:
        print(f"{R}[!] yt-dlp tidak ditemukan. Pastikan yt-dlp sudah terinstall.{N}")

def download_audio(url):
    output_path = os.path.expanduser("~/Downloads/%(title).60s.%(ext)s") if IS_WINDOWS else "/sdcard/Download/%(title).60s.%(ext)s"
    cmd = [
        "yt-dlp",
        "--no-cache-dir",
        "--ignore-errors",
        "--continue",
        "--no-warnings",
        "-x", "--audio-format", "mp3",
        "--audio-quality", "0",
        "-o", output_path,
        url
    ]
    typing(f"\n{C}[•] Download Audio...{N}")
    try:
        subprocess.run(cmd, timeout=600)
    except subprocess.TimeoutExpired:
        print(f"{R}[!] Download audio terlalu lama, dibatalkan.{N}")
    except FileNotFoundError:
        print(f"{R}[!] yt-dlp tidak ditemukan. Pastikan yt-dlp sudah terinstall.{N}")

def main():
    auto_update_ytdlp()
    while True:
        banner()
        try:
            raw = input(f"{Y}[?] Masukkan URL / Judul Pencarian ('exit' untuk keluar): {N}").strip()
        except EOFError:
            break

        if raw.lower() in ['exit', 'keluar', 'x']:
            print(f"{C}Keluar dari program...{N}")
            break

        if is_url(raw):
            url = raw
        else:
            url = search_youtube(raw)
            if not url:
                continue

        print(f"\n{C}[1] Download Video (.mp4)")
        print(f"[2] Download Audio (.mp3)")
        print(f"[x] Batal{N}")
        mode = input(f"{Y}[?] Pilihan: {N}").strip()

        if mode == "1":
            download_video(url)
        elif mode == "2":
            download_audio(url)
        elif mode.lower() in ["x", "exit", "keluar"]:
            print(f"{C}Batal...{N}")
            continue
        else:
            print(f"{R}[!] Pilihan tidak valid.{N}")
            continue

        typing(f"\n{G}[✓] Selesai! Cek folder {'~/Downloads' if IS_WINDOWS else '/sdcard/Download'}{N}")
        input(f"\n{Y}Tekan Enter untuk lanjut...{N}")
        print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C}Keluar dari program...{N}")
        sys.exit(0)
