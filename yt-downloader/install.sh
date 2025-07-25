#!/bin/bash
echo "[•] Menginstall yt-dlp dan dependensi..."
pkg update -y
pkg install -y python ffmpeg
pip install -U yt-dlp

echo "[•] Menyalin yt.py ke /data/data/com.termux/files/usr/bin/ytdl"
install yt.py /data/data/com.termux/files/usr/bin/ytdl
chmod +x /data/data/com.termux/files/usr/bin/ytdl

echo "[✓] Instalasi selesai! Sekarang kamu bisa gunakan perintah: ytdl"
