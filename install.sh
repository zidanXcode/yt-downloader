#!/bin/bash

APP_NAME="yt-downloader"
SCRIPT_NAME="yt.py"
INSTALL_PATH="$HOME/.local/bin"
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

pip_package_installed() {
    python3 -c "import $1" >/dev/null 2>&1
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
    log_info "Cek & install dependencies sistem..."

    update_pkg() {
        case "$INSTALL_CMD" in
            "pkg") pkg update -y >/dev/null 2>&1 ;;
            "apk") apk update >/dev/null 2>&1 ;;
            "apt") command_exists sudo && sudo apt update >/dev/null 2>&1 || apt update >/dev/null 2>&1 ;;
            "brew") brew update >/dev/null 2>&1 ;;
        esac
    }

    update_pkg & show_spinner $!

    install_pkg() {
        local pkg="$1"
        if ! command_exists "$pkg"; then
            case "$INSTALL_CMD" in
                "pkg") pkg install -y "$pkg" >/dev/null 2>&1 ;;
                "apk") apk add "$pkg" >/dev/null 2>&1 ;;
                "apt") command_exists sudo && sudo apt install -y "$pkg" >/dev/null 2>&1 || apt install -y "$pkg" >/dev/null 2>&1 ;;
                "brew") brew install "$pkg" >/dev/null 2>&1 ;;
            esac
            log_success "Installed: $pkg"
        else
            log_info "Sudah terinstall: $pkg"
        fi
    }

    install_pkg python
    install_pkg python3
    install_pkg pip
    install_pkg git
    install_pkg ffmpeg
    install_pkg curl
    install_pkg wget

    if command_exists mpv; then
        export HAS_MPV=1
        log_info "mpv terdeteksi. Play audio/video akan aktif."
    else
        install_pkg mpv
        if command_exists mpv; then
            export HAS_MPV=1
            log_success "mpv berhasil diinstall"
        else
            export HAS_MPV=0
            log_warning "mpv tidak tersedia. Play audio/video akan dinonaktifkan."
        fi
    fi

    log_success "Dependencies sistem dicek dan aman"
}

install_python_deps() {
    log_info "Cek & install modul Python..."

    for dep in "${PYTHON_DEPS[@]}"; do
        if ! pip_package_installed "$dep"; then
            pip3 install --upgrade "$dep" >/dev/null 2>&1 &
            show_spinner $!
            log_success "Installed Python module: $dep"
        else
            log_info "Sudah ada: $dep"
        fi
    done
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
