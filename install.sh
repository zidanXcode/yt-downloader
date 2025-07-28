#!/bin/bash

APP_NAME="yt-downloader"
SCRIPT_NAME="yt.py"
INSTALL_PATH="$HOME/.local/bin"
REPO_URL="https://github.com/yt-dlp/yt-dlp.git"
PYTHON_DEPS=("yt-dlp" "rich" "requests")

RED='\033[0;31m'
GRN='\033[0;32m'
YEL='\033[1;33m'
CYA='\033[1;36m'
NOC='\033[0m'

log_info()    { echo -e "${CYA}[•] $1${NOC}"; }
log_success() { echo -e "${GRN}[✓] $1${NOC}"; }
log_warning() { echo -e "${YEL}[!] $1${NOC}"; }
log_error()   { echo -e "${RED}[✗] $1${NOC}"; }

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

detect_package_manager() {
    if command_exists pkg; then
        INSTALL_CMD="pkg"
    elif command_exists apk; then
        INSTALL_CMD="apk"
    elif command_exists apt; then
        INSTALL_CMD="apt"
    elif command_exists brew; then
        INSTALL_CMD="brew"
    else
        INSTALL_CMD="unknown"
    fi
}

show_spinner() {
    pid=$1
    spin='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    i=0
    while kill -0 $pid 2>/dev/null; do
        i=$(( (i+1) % 10 ))
        printf "\r${CYA}[•] Loading ${spin:$i:1}${NOC}"
        sleep .1
    done
    printf "\r"
}

install_dependencies() {
    log_info "Menginstall dependencies sistem..."

    case "$INSTALL_CMD" in
        "pkg") 
            pkg update -y >/dev/null 2>&1 &
            show_spinner $!
            pkg install -y python ffmpeg git curl wget mpv >/dev/null 2>&1 &
            show_spinner $!
            ;;
        
        "apk")
            apk update >/dev/null 2>&1 &
            show_spinner $!
            apk add python3 py3-pip ffmpeg git curl wget >/dev/null 2>&1 &
            show_spinner $!
            log_warning "mpv tidak tersedia di iSH. Fitur Play tidak aktif."
            ;;

        "apt")
            if command_exists sudo; then
                sudo apt update >/dev/null 2>&1 &
            else
                apt update >/dev/null 2>&1 &
            fi
            show_spinner $!

            if command_exists sudo; then
                sudo apt install -y python3 python3-pip ffmpeg git curl wget mpv >/dev/null 2>&1 &
            else
                apt install -y python3 python3-pip ffmpeg git curl wget mpv >/dev/null 2>&1 &
            fi
            show_spinner $!
            ;;

        "brew")
            brew update >/dev/null 2>&1 &
            show_spinner $!
            brew install python ffmpeg git mpv >/dev/null 2>&1 &
            show_spinner $!
            ;;

        *)
            log_error "Package manager tidak dikenali."
            log_warning "Silakan install manual: python3, pip3, ffmpeg, git, mpv"
            ;;
    esac

    log_success "Dependencies sistem berhasil diinstall"
}

install_python_deps() {
    log_info "Menginstall modul Python..."
    for dep in "${PYTHON_DEPS[@]}"; do
        pip3 install --upgrade "$dep" >/dev/null 2>&1 &
        show_spinner $!
    done
    log_success "Modul Python berhasil diinstall"
}

install_script() {
    mkdir -p "$INSTALL_PATH"
    cp "$SCRIPT_NAME" "$INSTALL_PATH/$APP_NAME"
    chmod +x "$INSTALL_PATH/$APP_NAME"

    if ! echo "$PATH" | grep -q "$INSTALL_PATH"; then
        echo "export PATH=\"\$PATH:$INSTALL_PATH\"" >> "$HOME/.bashrc"
        echo "export PATH=\"\$PATH:$INSTALL_PATH\"" >> "$HOME/.zshrc"
        export PATH="$PATH:$INSTALL_PATH"
        log_warning "PATH diperbarui. Restart shell jika perintah belum dikenali."
    fi

    log_success "Script berhasil diinstal sebagai: ${CYA}$APP_NAME${NOC}"
}

clear
echo -e "${GRN}== ${CYA}YT Downloader Installer${GRN} =="
echo -e "${YEL}+ Support Play via mpv${NOC}"
echo ""

detect_package_manager
install_dependencies
install_python_deps
install_script

echo ""
log_success "Instalasi selesai! Jalankan dengan: ${CYA}$APP_NAME${NOC}"
