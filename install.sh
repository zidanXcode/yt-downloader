#!/bin/bash

set -e

RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
BLUE='\033[1;34m'
NC='\033[0m' # No Color

if [[ ! -t 1 ]] || [[ "${TERM}" == "dumb" ]]; then
    RED=''
    GREEN=''
    YELLOW=''
    CYAN=''
    BLUE=''
    NC=''
fi

log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

show_spinner() {
    local pid=$1
    local delay=0.1
    local spinstr='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c]  " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b\b"
    done
    printf "    \b\b\b\b"
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

detect_system() {
    log_info "Mendeteksi sistem..."
    
    PLATFORM="$(uname -o 2>/dev/null || uname -s)"
    ARCH="$(uname -m)"
    
    IS_TERMUX=$(command_exists termux-info && echo true || echo false)
    IS_ISH=$(grep -qi 'iSH' /proc/version 2>/dev/null && echo true || echo false)
    IS_WSL=$(grep -qi microsoft /proc/version 2>/dev/null && echo true || echo false)
    
    log_info "Platform: ${PLATFORM}"
    log_info "Architecture: ${ARCH}"
    
    if [ "$IS_TERMUX" = true ]; then
        log_info "Environment: Termux (Android)"
        INSTALL_CMD="pkg"
        PYTHON_CMD="python"
        PIP_CMD="pip"
    elif [ "$IS_ISH" = true ]; then
        log_info "Environment: iSH (iOS)"
        INSTALL_CMD="apk"
        PYTHON_CMD="python3"
        PIP_CMD="pip3"
    elif [ "$IS_WSL" = true ]; then
        log_info "Environment: WSL (Windows Subsystem for Linux)"
        INSTALL_CMD="apt"
        PYTHON_CMD="python3"
        PIP_CMD="pip3"
    elif [[ "$PLATFORM" == Linux ]]; then
        log_info "Environment: Linux"
        INSTALL_CMD="apt"
        PYTHON_CMD="python3"
        PIP_CMD="pip3"
    elif [[ "$PLATFORM" == Darwin ]]; then
        log_info "Environment: macOS"
        INSTALL_CMD="brew"
        PYTHON_CMD="python3"
        PIP_CMD="pip3"
    else
        log_warning "Platform tidak dikenali: $PLATFORM"
        INSTALL_CMD="unknown"
        PYTHON_CMD="python3"
        PIP_CMD="pip3"
    fi
}

install_dependencies() {
    log_info "Menginstall dependencies sistem..."
    
    case "$INSTALL_CMD" in
        "pkg") 
            log_info "Updating Termux packages..."
            pkg update -y >/dev/null 2>&1 &
            show_spinner $!
            
            log_info "Installing Python, FFmpeg, dan Git..."
            pkg install -y python ffmpeg git curl wget >/dev/null 2>&1 &
            show_spinner $!
            ;;
            
        "apk")
            log_info "Updating Alpine packages..."
            apk update >/dev/null 2>&1 &
            show_spinner $!
            
            log_info "Installing Python, FFmpeg, dan Git..."
            apk add python3 py3-pip ffmpeg git curl wget >/dev/null 2>&1 &
            show_spinner $!
            ;;
            
        "apt") 
            log_info "Updating apt packages..."
            if command_exists sudo; then
                sudo apt update >/dev/null 2>&1 &
            else
                apt update >/dev/null 2>&1 &
            fi
            show_spinner $!
            
            log_info "Installing Python, FFmpeg, dan Git..."
            if command_exists sudo; then
                sudo apt install -y python3 python3-pip ffmpeg git curl wget >/dev/null 2>&1 &
            else
                apt install -y python3 python3-pip ffmpeg git curl wget >/dev/null 2>&1 &
            fi
            show_spinner $!
            ;;
            
        "brew") 
            if ! command_exists brew; then
                log_error "Homebrew tidak ditemukan. Install Homebrew terlebih dahulu:"
                log_info "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                exit 1
            fi
            
            log_info "Updating Homebrew..."
            brew update >/dev/null 2>&1 &
            show_spinner $!
            
            log_info "Installing Python, FFmpeg, dan Git..."
            brew install python ffmpeg git >/dev/null 2>&1 &
            show_spinner $!
            ;;
            
        *)
            log_error "Package manager tidak didukung: $INSTALL_CMD"
            log_warning "Install manual: python3, python3-pip, ffmpeg, git"
            ;;
    esac
    
    log_success "Dependencies sistem berhasil diinstall"
}

verify_python() {
    log_info "Verifikasi instalasi Python..."
    
    if ! command_exists "$PYTHON_CMD"; then
        log_error "Python tidak ditemukan setelah instalasi"
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    log_success "Python $PYTHON_VERSION terdeteksi"
    
    PYTHON_MAJOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.major)")
    PYTHON_MINOR=$($PYTHON_CMD -c "import sys; print(sys.version_info.minor)")
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 7 ]); then
        log_error "Python 3.7+ diperlukan. Versi saat ini: $PYTHON_VERSION"
        exit 1
    fi
}

install_ytdlp() {
    log_info "Mengecek yt-dlp..."
    
    if command_exists yt-dlp; then
        CURRENT_VERSION=$(yt-dlp --version 2>/dev/null || echo "unknown")
        log_warning "yt-dlp sudah terinstall (versi: $CURRENT_VERSION)"
        
        read -p "$(echo -e "${YELLOW}Update ke versi terbaru? (y/n): ${NC}")" -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Skip update yt-dlp"
            return
        fi
    fi
    
    log_info "Installing/updating yt-dlp..."
    
    if $PIP_CMD install --upgrade yt-dlp >/dev/null 2>&1; then
        log_success "yt-dlp berhasil diinstall via pip"
    elif $PYTHON_CMD -m pip install --upgrade yt-dlp >/dev/null 2>&1; then
        log_success "yt-dlp berhasil diinstall via python -m pip"
    elif curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o ~/.local/bin/yt-dlp && chmod +x ~/.local/bin/yt-dlp; then
        log_success "yt-dlp berhasil diinstall via binary download"
        export PATH="$HOME/.local/bin:$PATH"
    else
        log_error "Gagal menginstall yt-dlp"
        exit 1
    fi
    
    if command_exists yt-dlp; then
        NEW_VERSION=$(yt-dlp --version 2>/dev/null || echo "unknown")
        log_success "yt-dlp versi $NEW_VERSION siap digunakan"
    else
        log_error "yt-dlp tidak dapat diverifikasi setelah instalasi"
        exit 1
    fi
}

setup_project() {
    PROJECT_DIR="$HOME/yt-downloader"
    
    log_info "Setup project directory..."
    
    if [ -d "$PROJECT_DIR" ]; then
        log_warning "Directory $PROJECT_DIR sudah ada"
        
        read -p "$(echo -e "${YELLOW}Update dari repository? (y/n): ${NC}")" -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Updating repository..."
            cd "$PROJECT_DIR"
            if git pull origin main >/dev/null 2>&1; then
                log_success "Repository berhasil diupdate"
            else
                log_warning "Gagal update repository, menggunakan versi lokal"
            fi
        fi
    else
        log_info "Cloning repository..."
        if git clone https://github.com/zidanXcode/yt-downloader "$PROJECT_DIR" >/dev/null 2>&1; then
            log_success "Repository berhasil diclone"
        else
            log_error "Gagal clone repository"
            log_info "Membuat directory manual..."
            mkdir -p "$PROJECT_DIR"
        fi
    fi
    
    if [ -f "$PROJECT_DIR/yt.py" ]; then
        chmod +x "$PROJECT_DIR/yt.py"
        log_success "Script yt.py siap digunakan"
    else
        log_warning "File yt.py tidak ditemukan di repository"
    fi
}

create_aliases() {
    log_info "Membuat alias untuk kemudahan..."
    
    SHELL_RC=""
    if [ -n "$BASH_VERSION" ]; then
        SHELL_RC="$HOME/.bashrc"
    elif [ -n "$ZSH_VERSION" ]; then
        SHELL_RC="$HOME/.zshrc"
    else
        SHELL_RC="$HOME/.profile"
    fi
    
    if [ -f "$SHELL_RC" ]; then
        if ! grep -q "alias ytdl=" "$SHELL_RC" 2>/dev/null; then
            echo "" >> "$SHELL_RC"
            echo "# YouTube Downloader alias" >> "$SHELL_RC"
            echo "alias ytdl='cd ~/yt-downloader && $PYTHON_CMD yt.py'" >> "$SHELL_RC"
            log_success "Alias 'ytdl' ditambahkan ke $SHELL_RC"
        else
            log_info "Alias 'ytdl' sudah ada"
        fi
    fi
}

run_test() {
    log_info "Menjalankan test cepat..."
    
    if command_exists yt-dlp && command_exists "$PYTHON_CMD"; then
        if yt-dlp --version >/dev/null 2>&1; then
            log_success "yt-dlp berfungsi dengan baik"
        else
            log_warning "yt-dlp mungkin bermasalah"
        fi
        
        if $PYTHON_CMD -c "import sys; print('Python test OK')" >/dev/null 2>&1; then
            log_success "Python berfungsi dengan baik"
        else
            log_warning "Python mungkin bermasalah"
        fi
        
        log_success "Semua komponen siap digunakan!"
    else
        log_warning "Beberapa komponen mungkin belum ready"
    fi
}

main() {
    clear
    echo -e "${CYAN}"
    echo "================================================"
    echo "    YouTube Downloader - Auto Installer"
    echo "    Author: Zidan (Optimized Version)"
    echo "================================================"
    echo -e "${NC}"
    
    log_info "Memulai instalasi YouTube Downloader..."
    
    detect_system
    install_dependencies
    verify_python
    install_ytdlp
    setup_project
    create_aliases
    run_test
    
    echo ""
    echo -e "${GREEN}================================================"
    echo "           ✅ INSTALASI SELESAI!"
    echo "================================================${NC}"
    echo ""
    echo -e "${YELLOW}Cara menjalankan:${NC}"
    echo -e "  ${CYAN}1. Manual:${NC}"
    echo "     cd ~/yt-downloader && $PYTHON_CMD yt.py"
    echo ""
    echo -e "  ${CYAN}2. Menggunakan alias (restart terminal dulu):${NC}"
    echo "     ytdl"
    echo ""
    echo -e "${BLUE}Tips:${NC}"
    echo "• Restart terminal untuk menggunakan alias 'ytdl'"
    echo "• Update berkala dengan: $PIP_CMD install --upgrade yt-dlp"
    echo "• Report bugs ke: https://github.com/zidanXcode/yt-downloader"
    echo ""
}

trap 'log_error "Instalasi dibatalkan atau error terjadi"; exit 1' INT TERM

main "$@"
