#!/bin/bash

echo "Menginstall yt-downloader..."

PLATFORM="$(uname -o 2>/dev/null || uname -s)"
IS_TERMUX=$(command -v termux-info >/dev/null && echo true)
IS_ISH=$(grep -qi 'iSH' /proc/version && echo true)

if [ "$IS_TERMUX" = true ]; then
    pkg update -y && pkg install -y python ffmpeg git
elif [ "$IS_ISH" = true ]; then
    apk update && apk add python3 py3-pip ffmpeg git
elif [[ "$PLATFORM" == Linux ]]; then
    sudo apt update && sudo apt install -y python3 python3-pip ffmpeg git
elif [[ "$PLATFORM" == Darwin ]]; then
    brew install python ffmpeg git
fi

if ! command -v yt-dlp >/dev/null 2>&1; then
    echo "Menginstall yt-dlp..."
    pip3 install --upgrade yt-dlp
else
    echo "✅ yt-dlp sudah terinstall"
fi

if [ ! -d "$HOME/yt-downloader" ]; then
    git clone https://github.com/zidanXcode/yt-downloader "$HOME/yt-downloader"
else
    echo "Folder yt-downloader sudah ada"
fi

echo ""
echo "✅ Instalasi selesai! Jalankan dengan:"
echo "   cd ~/yt-downloader && python3 yt.py"
