#!/usr/bin/env python3
import subprocess
import sys
import time
import re

R = '\033[1;31m'
G = '\033[1;32m'
Y = '\033[1;33m'
C = '\033[1;36m'
N = '\033[0m'

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
    print(f"• github  : \033]8;;https://github.com/zidanXcode\ahttps://github.com/zidanXcode\033]8;;\a{N}\n")

def is_url(text):
    return text.startswith("http://") or text.startswith("https://")

def search_youtube(query):
    print(f"{C}[•] Mencari video: {query}{N}")
    try:
        result = subprocess.run(
            ["yt-dlp", f"ytsearch1:{query}", "--print", "%(title)s ||| %(webpage_url)s ||| %(duration_string)s ||| %(uploader)s"],
            capture_output=True, text=True, check=True
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
    except subprocess.CalledProcessError:
        print(f"{R}[!] Error saat pencarian YouTube.{N}")
    return None

def download_video(url):
    cmd = [
        "yt-dlp",
        "--ignore-errors",
        "--continue",
        "--no-warnings",
        "--merge-output-format", "mp4",
        "-f", "bv*[ext=mp4][height<=1080][vcodec^=avc1]+ba[ext=m4a]/bestvideo[height<=1080]+bestaudio",
        "-o", "/sdcard/Download/%(title).60s.%(ext)s",
        url
    ]
    typing(f"\n{C}[•] Download Video...{N}")
    subprocess.run(cmd)

def download_audio(url):
    cmd = [
        "yt-dlp",
        "--ignore-errors",
        "--continue",
        "--no-warnings",
        "-x", "--audio-format", "mp3",
        "--audio-quality", "0",
        "-o", "/sdcard/Download/%(title).60s.%(ext)s",
        url
    ]
    typing(f"\n{C}[•] Download Audio...{N}")
    subprocess.run(cmd)

def main():
    while True:
        banner()
        raw = input(f"{Y}[?] Masukkan URL / Judul Pencarian ('exit' untuk keluar): {N}").strip()
        if raw.lower() in ['exit', 'keluar', 'x']:
            print(f"{C}Keluar dari program...{N}")
            sys.exit()

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

        typing(f"\n{G}[✓] Selesai! Cek folder /sdcard/Download{N}")
        input(f"\n{Y}Tekan Enter untuk lanjut...{N}")
        print()

if _name_ == "_main_":
    main()
