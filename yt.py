#!/usr/bin/env python3
import subprocess
import sys
import time
import os
import urllib.request
import hashlib

GITHUB_RAW_URL = "https://raw.githubusercontent.com/zidanXcode/yt-downloader/main/yt.py"
LOCAL_FILE = os.path.realpath(__file__)

R = '\033[1;31m'
G = '\033[1;32m'
Y = '\033[1;33m'
C = '\033[1;36m'
N = '\033[0m'

def hash_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def check_update():
    try:
        tmp_file = "/tmp/yt_latest.py"
        urllib.request.urlretrieve(GITHUB_RAW_URL, tmp_file)
        if hash_file(tmp_file) != hash_file(LOCAL_FILE):
            print(f"{Y}[⟳] Update tersedia! Mengupdate script...{N}")
            os.replace(tmp_file, LOCAL_FILE)
            print(f"{G}[✓] Script berhasil diperbarui! Jalankan ulang script.{N}")
            exit()
        else:
            os.remove(tmp_file)
    except:
        pass

def typing(text, delay=0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

check_update()

typing(f"""{C}
Youtube Downloader
• version : 1.0
• author  : Zidan
• github  : https://github.com/zidanXcode
{N}""", delay=0.004)

urls = input(f"{Y}[?] Masukkan URL atau Query: {N}").strip()
if not urls:
    print(f"{R}[!] Tidak ada input!{N}")
    sys.exit()

is_query = not urls.startswith("http")
if is_query:
    typing(f"{C}[•] Mencari video untuk: {urls}{N}")
    search_cmd = ["yt-dlp", f"ytsearch1:{urls}", "--print", "id"]
    try:
        result = subprocess.check_output(search_cmd, text=True).strip()
        if not result:
            print(f"{R}[!] Tidak ditemukan hasil!{N}")
            sys.exit()
        urls = f"https://youtu.be/{result}"
    except:
        print(f"{R}[!] Gagal melakukan pencarian!{N}")
        sys.exit()

print(f"{C}[1] Video (.mp4)")
print(f"[2] Audio (.mp3){N}")
mode = input(f"{Y}[?] Pilihan: {N}").strip()

output = "/sdcard/Download/%(playlist_title,s)s%(title).60s.%(ext)s"
base_cmd = [
    "yt-dlp",
    "--ignore-errors",
    "--continue",
    "--yes-playlist",
    "--no-warnings",
    "-o", output
]

if mode == "1":
    base_cmd += [
        "-f", "bv*[ext=mp4][height<=1080][vcodec^=avc1]+ba[ext=m4a]/bestvideo[height<=1080]+bestaudio",
        "--merge-output-format", "mp4"
    ]
elif mode == "2":
    base_cmd += [
        "-x", "--audio-format", "mp3",
        "--audio-quality", "0"
    ]
else:
    print(f"{R}[!] Pilihan tidak valid!{N}")
    sys.exit()

base_cmd += [urls]

typing(f"{C}[•] Sedang mendownload...{N}")
try:
    subprocess.run(base_cmd, check=True)
    typing(f"{G}[✓] Selesai! Cek folder /sdcard/Download{N}")
except subprocess.CalledProcessError:
    print(f"{R}[!] Terjadi error saat download!{N}")
