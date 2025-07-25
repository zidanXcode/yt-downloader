#!/bin/bash

echo "Menginstall Youtube Downloader..."

pkg update -y && pkg upgrade -y
pkg install -y python git ffmpeg

if [ ! -d "$HOME/yt-downloader" ]; then
    git clone https://github.com/zidanXcode/yt-downloader.git $HOME/yt-downloader
else
    echo "Folder yt-downloader sudah ada, skip cloning."
fi

if ! grep -q "alias ytdl=" "$HOME/.bashrc"; then
    echo "Menambahkan alias ytdl ke .bashrc..."
    cat << 'EOF' >> "$HOME/.bashrc"

alias ytdl='cd ~/yt-downloader && git pull --quiet && python yt.py'
EOF
else
    echo "✅ Alias ytdl sudah ada."
fi

echo "✅ Instalasi selesai!"
echo "Ketik 'ytdl' di terminal untuk menjalankan downloader."
echo "Note: Jalankan 'source ~/.bashrc' atau restart Termux untuk mengaktifkan alias."