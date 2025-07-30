#!/usr/bin/env python3
import subprocess, sys, time, platform, os, shutil, threading, re

IS_WINDOWS = platform.system().lower().startswith('win')
IS_ANDROID = 'android' in platform.platform().lower() or 'termux' in os.getenv("PREFIX", "").lower()
USE_COLOR = not IS_WINDOWS

R = '\033[1;31m' if USE_COLOR else ''
G = '\033[1;32m' if USE_COLOR else ''
Y = '\033[1;33m' if USE_COLOR else ''
C = '\033[1;36m' if USE_COLOR else ''
N = '\033[0m' if USE_COLOR else ''

DOWNLOAD_DIR = os.path.expanduser("/Downloads") if IS_WINDOWS else "/sdcard/Download" if IS_ANDROID else os.path.expanduser("/Downloads")
RESOLUTION_MAP = {
    "140": "140",
    "360": "bv*[height<=360]+ba/best[height<=360]",
    "480": "bv*[height<=480]+ba/best[height<=480]",
    "720": "bv*[height<=720]+ba/best[height<=720]",
    "1080": "bv*[height<=1080]+ba/best[height<=1080]",
}

mpv_process = None

def typing(text, delay=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def safe_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def banner():
    print(f"{C}Youtube Downloader CLI")
    print(f"\u2022 version : 2.1")
    print(f"\u2022 author  : Zidan")
    print(f"\u2022 github  : https://github.com/zidanXcode{N}")
    print(f"\u2022 platform: {platform.system()} - {platform.release()}\n")

def auto_update_ytdlp():
    try:
        typing(f"{C}[\u2022] Mengecek pembaruan yt-dlp...{N}")
        subprocess.run(["yt-dlp", "-U"], check=True)
    except Exception as e:
        print(f"{R}[!] Gagal memperbarui yt-dlp: {e}{N}")

def is_url(text):
    return text.startswith("http://") or text.startswith("https://")

def search_youtube(query):
    print(f"{C}[\u2022] Mencari video: {query}{N}")
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
        return result.stdout.strip().splitlines()
    except Exception as e:
        print(f"{R}[!] Gagal mengambil info playlist: {e}{N}")
        return []

def download_video(url, res, extra_args=None):
    format_str = RESOLUTION_MAP.get(res)
    if not format_str:
        print(f"{R}[!] Resolusi tidak dikenali.{N}")
        return
    output_template = os.path.join(DOWNLOAD_DIR, "%(title).60s.%(ext)s")
    cmd = ["yt-dlp", "-f", format_str, "-o", output_template, url]
    cmd += extra_args or []
    typing(f"\n{C}[\u2022] Mendownload video {res}p...{N}")
    try:
        subprocess.run(cmd, timeout=600)
        print(f"{G}[\u2713] Selesai! Lihat di: {DOWNLOAD_DIR}{N}")
    except Exception as e:
        print(f"{R}[!] Gagal download video: {e}{N}")

def download_audio(url, extra_args=None):
    output_template = os.path.join(DOWNLOAD_DIR, "%(title).60s.%(ext)s")
    cmd = ["yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "0", "-o", output_template, url]
    cmd += extra_args or []
    typing(f"\n{C}[\u2022] Mendownload Audio...{N}")
    try:
        subprocess.run(cmd, timeout=600)
        print(f"{G}[\u2713] Selesai! Lihat di: {DOWNLOAD_DIR}{N}")
    except Exception as e:
        print(f"{R}[!] Gagal download audio: {e}{N}")

def play_audio_background(url):
    global mpv_process
    if shutil.which("mpv"):
        typing(f"{C}[\u2022] Streaming audio... (Ketik 'stop' untuk berhenti){N}")
        try:
            mpv_process = subprocess.Popen(["mpv", "--no-video", "--volume=100", url])
        except Exception as e:
            print(f"{R}[!] Gagal play audio: {e}{N}")
    else:
        print(f"{R}[!] mpv tidak ditemukan. Instal dulu.{N}")

def stop_audio():
    global mpv_process
    if mpv_process and mpv_process.poll() is None:
        mpv_process.terminate()
        print(f"{G}[\u2713] Audio dihentikan.{N}")
    else:
        print(f"{Y}[\u2022] Tidak ada audio yang sedang diputar.{N}")

def tampilkan_lirik(lrc_path):
    if not os.path.isfile(lrc_path):
        print(f"{Y}[\u2022] Tidak ditemukan lirik (.lrc) untuk audio ini.{N}")
        return
    with open(lrc_path, 'r', encoding="utf-8") as f:
        lines = f.readlines()
    timestamps, teks = [], []
    for line in lines:
        if line.startswith("["):
            try:
                waktu, teks_line = line.strip().split("]", 1)
                waktu = waktu[1:]
                m, s = map(float, waktu.split(":"))
                detik = m * 60 + s
                timestamps.append(detik)
                teks.append(teks_line)
            except: continue
    start_time = time.time()
    for i in range(len(timestamps)):
        while time.time() - start_time < timestamps[i]:
            time.sleep(0.05)
        sys.stdout.write(f"{G}♪ {N}")
        sys.stdout.flush()
        typing(teks[i], delay=0.03)

def main():
    auto_update_ytdlp()
    while True:
        banner()
        try:
            raw = input(f"{Y}[?] Masukkan URL / Judul ('exit' untuk keluar): {N}").strip()
        except EOFError:
            break
        if raw.lower() in ['exit', 'keluar', 'x']:
            print(f"{C}Keluar...{N}")
            stop_audio()
            break
        url = raw if is_url(raw) else search_youtube(raw)
        if not url: continue

        extra_args = []
        if "playlist?" in url or "list=" in url:
            videos = get_playlist_info(url)
            total = len(videos)
            print(f"\n{C}Playlist terdeteksi: {total} video.{N}")
            preview = "\n".join([f"{i+1}. {title}" for i, title in enumerate(videos[:5])])
            print(f"{Y}Contoh:\n{preview}{N}")
            confirm = input(f"{Y}[?] Download semua? [Y/n]: {N}").strip().lower()
            if confirm == "n":
                max_videos = input(f"{Y}[?] Jumlah video? (1-{total}): {N}").strip()
                if max_videos.isdigit():
                    extra_args = ["--playlist-end", max_videos]

        print(f"\n{C}[1] Download Video")
        print(f"[2] Download Audio")
        print(f"[3] Play Audio")
        print(f"[x] Batal{N}")
        mode = input(f"{Y}[?] Pilih: {N}").strip()

        if mode == "1":
            print(f"\n{C}Resolusi tersedia:")
            print(" \u2022 ".join([f"{r}p" for r in RESOLUTION_MAP.keys()]))
            res = input(f"{Y}[?] Resolusi (misal 480): {N}").strip()
            download_video(url, res, extra_args)
        elif mode == "2":
            download_audio(url, extra_args)
        elif mode == "3":
            play_audio_background(url)
            try:
                info = subprocess.run(
                    ["yt-dlp", "--print", "%(title)s", url],
                    capture_output=True, text=True, timeout=10, check=True
                )
                judul = info.stdout.strip()
                safe_judul = safe_filename(judul)
                lrc_path = os.path.join(DOWNLOAD_DIR, f"{safe_judul}.lrc")
                threading.Thread(target=tampilkan_lirik, args=(lrc_path,), daemon=True).start()
            except: pass

            while mpv_process and mpv_process.poll() is None:
                try:
                    user_input = input(f"{Y}[?] Ketik 'stop' untuk hentikan audio: {N}").strip().lower()
                    if user_input == "stop":
                        stop_audio()
                        break
                except KeyboardInterrupt:
                    stop_audio()
                    break
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
        stop_audio()
        sys.exit(0)
