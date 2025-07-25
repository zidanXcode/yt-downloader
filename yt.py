#!/usr/bin/env python3
import subprocess
import sys
import time
import platform
import os
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json
import re

IS_WINDOWS = platform.system().lower().startswith('win')
USE_COLOR = not IS_WINDOWS and hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

COLORS = {
    'red': '\033[1;31m' if USE_COLOR else '',
    'green': '\033[1;32m' if USE_COLOR else '',
    'yellow': '\033[1;33m' if USE_COLOR else '',
    'cyan': '\033[1;36m' if USE_COLOR else '',
    'blue': '\033[1;34m' if USE_COLOR else '',
    'magenta': '\033[1;35m' if USE_COLOR else '',
    'reset': '\033[0m' if USE_COLOR else ''
}

class YouTubeDownloader:
    def _init_(self):
        self.output_dir = self._get_output_directory()
        self.ytdlp_available = self._check_ytdlp()
        self.progress_lock = threading.Lock()
        
    def _get_output_directory(self):
        if IS_WINDOWS:
            return Path.home() / "Downloads"
        else:
            android_path = Path("/sdcard/Download")
            if android_path.exists():
                return android_path
            return Path.home() / "Downloads"
    
    def _check_ytdlp(self):
        try:
            result = subprocess.run(
                ["yt-dlp", "--version"], 
                capture_output=True, 
                timeout=5,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def print_colored(self, text, color='reset', end='\n'):
        print(f"{COLORS.get(color, '')}{text}{COLORS['reset']}", end=end)
    
    def typing_effect(self, text, delay=0.002):
        for char in text:
            try:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(delay)
            except KeyboardInterrupt:
                print()
                return
        print()
    
    def show_banner(self):
        os.system('clear' if not IS_WINDOWS else 'cls')
        print(f"{COLORS['cyan']}Youtube Downloader")
        print(f"• version : 1.0")
        print(f"• author  : Zidan")
        print(f"• github  : https://github.com/zidanXcode{COLORS['reset']}")
        print(f"• platform: {platform.system()} - {platform.release()}\n")
    
    def update_ytdlp(self):
        if not self.ytdlp_available:
            self.print_colored("[!] yt-dlp tidak tersedia. Install dengan: pip install yt-dlp", 'red')
            return False
            
        self.print_colored("[•] Mengecek pembaruan yt-dlp...", 'cyan')
        
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    subprocess.run, 
                    ["yt-dlp", "-U"], 
                    capture_output=True, 
                    text=True,
                    timeout=30
                )
                result = future.result()
                
            if result.returncode == 0:
                self.print_colored("[✓] yt-dlp sudah terbaru", 'green')
                return True
            else:
                self.print_colored(f"[!] Update gagal: {result.stderr}", 'red')
                return False
                
        except subprocess.TimeoutExpired:
            self.print_colored("[!] Timeout saat update yt-dlp", 'red')
            return False
        except Exception as e:
            self.print_colored(f"[!] Error update: {str(e)}", 'red')
            return False
    
    def validate_url(self, text):
        url_pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(text) is not None
    
    def search_youtube(self, query):
        self.print_colored(f"[•] Mencari: {query}", 'cyan')
        
        if not self.ytdlp_available:
            self.print_colored("[!] yt-dlp tidak tersedia", 'red')
            return None
        
        try:
            cmd = [
                "yt-dlp", 
                "--no-cache-dir",
                "--quiet",
                f"ytsearch3:{query}",
                "--dump-json"
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=20,
                check=True
            )
            
            videos = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        video_info = json.loads(line)
                        videos.append({
                            'title': video_info.get('title', 'Unknown'),
                            'url': video_info.get('webpage_url', ''),
                            'duration': video_info.get('duration_string', 'Unknown'),
                            'uploader': video_info.get('uploader', 'Unknown'),
                            'view_count': video_info.get('view_count', 0)
                        })
                    except json.JSONDecodeError:
                        continue
            
            if videos:
                return self._display_search_results(videos)
            else:
                self.print_colored("[!] Tidak ada hasil ditemukan", 'red')
                return None
                
        except subprocess.TimeoutExpired:
            self.print_colored("[!] Timeout saat pencarian", 'red')
        except subprocess.CalledProcessError as e:
            self.print_colored(f"[!] Error pencarian: {e.stderr if e.stderr else 'Unknown error'}", 'red')
        except Exception as e:
            self.print_colored(f"[!] Error: {str(e)}", 'red')
        
        return None
    
    def _display_search_results(self, videos):
        print(f"\n{COLORS['yellow']}Hasil Pencarian:{COLORS['reset']}")
        print("=" * 60)
        
        for i, video in enumerate(videos, 1):
            view_str = f"{video['view_count']:,}" if video['view_count'] else "Unknown"
            print(f"{COLORS['cyan']}[{i}]{COLORS['reset']} {video['title'][:50]}...")
            print(f"    📺 {video['uploader']} | ⏱ {video['duration']} | 👁 {view_str}")
            print()
        
        while True:
            try:
                choice = input(f"{COLORS['yellow']}[?] Pilih video (1-{len(videos)}) atau 'x' untuk batal: {COLORS['reset']}").strip()
                
                if choice.lower() in ['x', 'exit', 'batal']:
                    return None
                
                choice_num = int(choice)
                if 1 <= choice_num <= len(videos):
                    selected = videos[choice_num - 1]
                    print(f"\n{COLORS['green']}✓ Dipilih: {selected['title'][:50]}...{COLORS['reset']}")
                    return selected['url']
                else:
                    self.print_colored(f"[!] Pilih antara 1-{len(videos)}", 'red')
                    
            except ValueError:
                self.print_colored("[!] Input tidak valid", 'red')
            except KeyboardInterrupt:
                return None
    
    def _get_download_command(self, url, format_type, output_path):
        base_cmd = [
            "yt-dlp",
            "--no-cache-dir",
            "--ignore-errors",
            "--continue",
            "--progress",
            "--no-warnings",
            "-o", str(output_path / "%(title).60s.%(ext)s")
        ]
        
        if format_type == "video":
            base_cmd.extend([
                "--merge-output-format", "mp4",
                "-f", "bv*[height<=1080][vcodec^=avc1]+ba[ext=m4a]/best[height<=1080]"
            ])
        elif format_type == "audio":
            base_cmd.extend([
                "-x", "--audio-format", "mp3",
                "--audio-quality", "0",
                "--embed-metadata"
            ])
        
        base_cmd.append(url)
        return base_cmd
    
    def download_content(self, url, format_type):
        if not self.ytdlp_available:
            self.print_colored("[!] yt-dlp tidak tersedia", 'red')
            return False
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        cmd = self._get_download_command(url, format_type, self.output_dir)
        format_name = "Video" if format_type == "video" else "Audio"
        
        self.print_colored(f"\n[•] Memulai download {format_name.lower()}...", 'cyan')
        self.print_colored(f"[•] Lokasi: {self.output_dir}", 'blue')
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )
            
            for line in process.stdout:
                if "[download]" in line and "%" in line:
                    with self.progress_lock:
                        print(f"\r{COLORS['green']}{line.strip()}{COLORS['reset']}", end='', flush=True)
            
            process.wait()
            print() 
            
            if process.returncode == 0:
                self.print_colored(f"[✓] {format_name} berhasil didownload!", 'green')
                return True
            else:
                self.print_colored(f"[!] Download {format_name.lower()} gagal", 'red')
                return False
                
        except subprocess.TimeoutExpired:
            self.print_colored(f"[!] Download {format_name.lower()} timeout", 'red')
            return False
        except Exception as e:
            self.print_colored(f"[!] Error download: {str(e)}", 'red')
            return False
    
    def get_user_choice(self):
        print(f"\n{COLORS['cyan']}Format Download:{COLORS['reset']}")
        print(f"{COLORS['green']}[1]{COLORS['reset']} Video MP4")
        print(f"{COLORS['green']}[2]{COLORS['reset']} Audio MP3")
        print(f"{COLORS['red']}[x]{COLORS['reset']} Batal")
        
        while True:
            try:
                choice = input(f"{COLORS['yellow']}[?] Pilihan: {COLORS['reset']}").strip()
                
                if choice == "1":
                    return "video"
                elif choice == "2":
                    return "audio"
                elif choice.lower() in ["x", "exit", "batal"]:
                    return None
                else:
                    self.print_colored("[!] Pilih 1, 2, atau x", 'red')
                    
            except KeyboardInterrupt:
                return None
    
    def run(self):
        if not self.ytdlp_available:
            self.print_colored("[!] CRITICAL: yt-dlp tidak ditemukan!", 'red')
            self.print_colored("[•] Install dengan: pip install yt-dlp", 'yellow')
            return
        
        self.update_ytdlp()
        
        while True:
            try:
                self.show_banner()
                
                user_input = input(f"{COLORS['yellow']}[?] URL/Pencarian ('exit' untuk keluar): {COLORS['reset']}").strip()
                
                if user_input.lower() in ['exit', 'keluar', 'x', 'quit']:
                    self.print_colored("Terima kasih telah menggunakan YouTube Downloader!", 'cyan')
                    break
                
                if not user_input:
                    self.print_colored("[!] Input tidak boleh kosong", 'red')
                    input(f"{COLORS['yellow']}Tekan Enter untuk lanjut...{COLORS['reset']}")
                    continue
                
                if self.validate_url(user_input):
                    url = user_input
                    self.print_colored("[✓] URL valid terdeteksi", 'green')
                else:
                    url = self.search_youtube(user_input)
                    if not url:
                        input(f"{COLORS['yellow']}Tekan Enter untuk lanjut...{COLORS['reset']}")
                        continue
                
                format_choice = self.get_user_choice()
                if not format_choice:
                    self.print_colored("[•] Dibatalkan", 'yellow')
                    input(f"{COLORS['yellow']}Tekan Enter untuk lanjut...{COLORS['reset']}")
                    continue
                
                success = self.download_content(url, format_choice)
                
                if success:
                    self.print_colored(f"\nDownload selesai! Cek folder: {self.output_dir}", 'green')
                else:
                    self.print_colored("\nDownload gagal. Coba lagi.", 'red')
                
                input(f"\n{COLORS['yellow']}Tekan Enter untuk lanjut...{COLORS['reset']}")
                
            except KeyboardInterrupt:
                self.print_colored("\n\nKeluar dari program...", 'cyan')
                break
            except Exception as e:
                self.print_colored(f"\n[!] Error tidak terduga: {str(e)}", 'red')
                input(f"{COLORS['yellow']}Tekan Enter untuk lanjut...{COLORS['reset']}")

def main():
    try:
        downloader = YouTubeDownloader()
        downloader.run()
    except KeyboardInterrupt:
        print(f"\n{COLORS['cyan']}Program dihentikan oleh user.{COLORS['reset']}")
        sys.exit(0)
    except Exception as e:
        print(f"{COLORS['red']}Error fatal: {str(e)}{COLORS['reset']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
