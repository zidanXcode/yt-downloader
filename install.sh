#!/bin/bash

echo "Menginstall Youtube Downloader..."

pkg update -y && pkg upgrade -y
pkg install -y python git ffmpeg curl

if ! command -v yt-dlp >/dev/null 2>&1; then
    echo "Menginstall yt-dlp..."
    curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /data/data/com.termux/files/usr/bin/yt-dlp
    chmod +x /data/data/com.termux/files/usr/bin/yt-dlp
else
    echo "✅ yt-dlp sudah terinstall."
fi

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

echo ""
echo "✅ Instalasi selesai!"
echo "Jalankan 'source ~/.bashrc' atau restart Termux untuk mulai menggunakan."
echo "Ketik 'ytdl' di terminal untuk membuka Youtube Downloader buatan Zidan."
