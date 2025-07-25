#!/usr/bin/env python3

import asyncio
import subprocess
import sys
import time
import platform
import os
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import logging
from datetime import datetime

class Colors:
    def _init_(self):
        self.enabled = self._should_use_colors()
        
    def _should_use_colors(self) -> bool:
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            return os.getenv('TERM', '').lower() != 'dumb'
        return False
    
    @property
    def RED(self) -> str: return '\033[1;31m' if self.enabled else ''
    @property  
    def GREEN(self) -> str: return '\033[1;32m' if self.enabled else ''
    @property
    def YELLOW(self) -> str: return '\033[1;33m' if self.enabled else ''
    @property
    def CYAN(self) -> str: return '\033[1;36m' if self.enabled else ''
    @property
    def MAGENTA(self) -> str: return '\033[1;35m' if self.enabled else ''
    @property
    def BLUE(self) -> str: return '\033[1;34m' if self.enabled else ''
    @property
    def RESET(self) -> str: return '\033[0m' if self.enabled else ''
    @property
    def BOLD(self) -> str: return '\033[1m' if self.enabled else ''

colors = Colors()

@dataclass
class VideoInfo:
    title: str
    url: str
    duration: str
    uploader: str
    view_count: Optional[int] = None
    upload_date: Optional[str] = None
    thumbnail: Optional[str] = None

class ProgressCallback:
    def _init_(self):
        self.last_percent = 0
        
    def _call_(self, d):
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                percent = int((d['downloaded_bytes'] / d['total_bytes']) * 100)
                if percent > self.last_percent:
                    self.last_percent = percent
                    print(f"\rProgress: {colors.CYAN}{percent}%{colors.RESET}", end='', flush=True)
        elif d['status'] == 'finished':
            print(f"\n{colors.GREEN}✓ Download selesai!{colors.RESET}")

class ModernYTDownloader:
    def _init_(self):
        self.platform_info = self._get_platform_info()
        self.download_path = self._get_download_path()
        self.logger = self._setup_logging()
        self.executor = ThreadPoolExecutor(max_workers=3)
        
    def _get_platform_info(self) -> Dict[str, str]:
        return {
            'system': platform.system(),
            'release': platform.release(),
            'machine': platform.machine(),
            'python_version': platform.python_version()
        }
    
    def _get_download_path(self) -> Path:
        system = platform.system().lower()
        
        if os.path.exists('/data/data/com.termux') or 'TERMUX_VERSION' in os.environ:
            termux_downloads = Path.home() / 'storage' / 'downloads'
            if termux_downloads.exists():
                return termux_downloads
            shared_downloads = Path('/storage/emulated/0/Download')
            if shared_downloads.exists():
                return shared_downloads
            return Path.home() / 'downloads'
        elif system == 'windows':
            return Path.home() / 'Downloads'
        elif system == 'darwin': 
            return Path.home() / 'Downloads'
        elif system == 'linux':
            return Path.home() / 'Downloads'
        else:
            return Path.home() / 'Downloads'
    
    def _setup_logging(self) -> logging.Logger:
        log_dir = Path.home() / '.ytdl_logs'
        log_dir.mkdir(exist_ok=True)
        
        logger = logging.getLogger('ytdl')
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(log_dir / f'ytdl_{datetime.now().strftime("%Y%m%d")}.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger

    async def check_ytdlp_installation(self) -> bool:
        try:
            result = await asyncio.create_subprocess_exec(
                'yt-dlp', '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                version = stdout.decode().strip()
                print(f"{colors.GREEN}✓ yt-dlp terdeteksi: v{version}{colors.RESET}")
                
                try:
                    year, month, day = version.split('.')[:3]
                    version_date = f"{year}{month.zfill(2)}{day.zfill(2)}"
                    if version_date < "20241104":
                        print(f"{colors.YELLOW}⚠ Versi yt-dlp lama terdeteksi. Disarankan update ke versi terbaru.{colors.RESET}")
                except:
                    pass 
                
                return True
            else:
                print(f"{colors.RED}✗ yt-dlp tidak ditemukan{colors.RESET}")
                return False
                
        except FileNotFoundError:
            print(f"{colors.RED}✗ yt-dlp tidak terinstall{colors.RESET}")
            print(f"{colors.YELLOW}Install dengan: pip install yt-dlp{colors.RESET}")
            return False

    async def update_ytdlp(self) -> bool:
        print(f"{colors.CYAN}Mengecek pembaruan yt-dlp...{colors.RESET}")
        try:
            process = await asyncio.create_subprocess_exec(
                'yt-dlp', '-U',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)
            
            if process.returncode == 0:
                print(f"{colors.GREEN}✓ yt-dlp berhasil diperbarui{colors.RESET}")
                return True
            else:
                print(f"{colors.YELLOW}⚠ Pembaruan tidak diperlukan atau gagal{colors.RESET}")
                return False
                
        except asyncio.TimeoutError:
            print(f"{colors.RED}✗ Timeout saat update yt-dlp{colors.RESET}")
            return False
        except Exception as e:
            self.logger.error(f"Error updating yt-dlp: {e}")
            print(f"{colors.RED}✗ Error saat update: {e}{colors.RESET}")
            return False

    def is_valid_url(self, url: str) -> bool:
        return url.startswith(('http://', 'https://', 'www.'))

    async def search_youtube(self, query: str, max_results: int = 5) -> List[VideoInfo]:
        print(f"{colors.CYAN}Mencari: {query}{colors.RESET}")
        
        try:
            cmd = [
                'yt-dlp',
                '--no-cache-dir',
                '--no-warnings',
                f'ytsearch{max_results}:{query}',
                '--print', '%(title)s|||%(webpage_url)s|||%(duration_string)s|||%(uploader)s|||%(view_count)s|||%(upload_date)s|||%(thumbnail)s'
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            
            if process.returncode != 0:
                print(f"{colors.RED}✗ Error pencarian: {stderr.decode()}{colors.RESET}")
                return []
            
            results = []
            lines = stdout.decode().strip().split('\n')
            
            for line in lines:
                if '|||' in line:
                    parts = line.split('|||')
                    if len(parts) >= 4:
                        video_info = VideoInfo(
                            title=parts[0],
                            url=parts[1],
                            duration=parts[2] if parts[2] != 'NA' else 'Live/Unknown',
                            uploader=parts[3],
                            view_count=int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else None,
                            upload_date=parts[5] if len(parts) > 5 else None,
                            thumbnail=parts[6] if len(parts) > 6 else None
                        )
                        results.append(video_info)
            
            return results
            
        except asyncio.TimeoutError:
            print(f"{colors.RED}✗ Timeout saat pencarian{colors.RESET}")
            return []
        except Exception as e:
            self.logger.error(f"Search error: {e}")
            print(f"{colors.RED}✗ Error pencarian: {e}{colors.RESET}")
            return []

    def display_search_results(self, results: List[VideoInfo]) -> Optional[VideoInfo]:
        if not results:
            print(f"{colors.RED}✗ Tidak ada hasil ditemukan{colors.RESET}")
            return None
        
        print(f"\n{colors.BOLD}📋 Hasil Pencarian:{colors.RESET}")
        print("-" * 80)
        
        for i, video in enumerate(results, 1):
            view_text = f"{video.view_count:,} views" if video.view_count else "Unknown views"
            print(f"{colors.YELLOW}[{i}]{colors.RESET} {video.title[:60]}...")
            print(f"    {colors.CYAN}Channel:{colors.RESET} {video.uploader}")
            print(f"    {colors.CYAN}Duration:{colors.RESET} {video.duration} | {colors.CYAN}Views:{colors.RESET} {view_text}")
            print()
        
        try:
            choice = input(f"{colors.YELLOW}Pilih nomor (1-{len(results)}) atau 'x' untuk batal: {colors.RESET}").strip()
            
            if choice.lower() == 'x':
                return None
            
            idx = int(choice) - 1
            if 0 <= idx < len(results):
                return results[idx]
            else:
                print(f"{colors.RED}✗ Pilihan tidak valid{colors.RESET}")
                return None
                
        except (ValueError, EOFError):
            print(f"{colors.RED}✗ Input tidak valid{colors.RESET}")
            return None

    async def get_video_info(self, url: str) -> Optional[VideoInfo]:
        try:
            cmd = [
                'yt-dlp',
                '--no-cache-dir',
                '--no-warnings',
                '--print', '%(title)s|||%(webpage_url)s|||%(duration_string)s|||%(uploader)s|||%(view_count)s|||%(upload_date)s|||%(thumbnail)s',
                url
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=20)
            
            if process.returncode == 0:
                line = stdout.decode().strip()
                parts = line.split('|||')
                
                if len(parts) >= 4:
                    return VideoInfo(
                        title=parts[0],
                        url=parts[1],
                        duration=parts[2] if parts[2] != 'NA' else 'Live/Unknown',
                        uploader=parts[3],
                        view_count=int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else None,
                        upload_date=parts[5] if len(parts) > 5 else None,
                        thumbnail=parts[6] if len(parts) > 6 else None
                    )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Get video info error: {e}")
            return None

    async def download_video(self, url: str, quality: str = 'best') -> bool:
        output_template = str(self.download_path / '%(title).100s.%(ext)s')
        
        quality_map = {
            'best': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            'worst': 'worstvideo+worstaudio/worst'
        }
        
        format_selector = quality_map.get(quality, quality_map['best'])
        
        cmd = [
            'yt-dlp',
            '--no-cache-dir',
            '--ignore-errors',
            '--continue',
            '--no-warnings',
            '--no-mtime',
            '--merge-output-format', 'mp4',
            '--format', format_selector,
            '--output', output_template,
            '--progress-template', 'download:%(progress._percent_str)s',
            url
        ]
        
        print(f"\n{colors.CYAN}Memulai download video...{colors.RESET}")
        print(f"{colors.CYAN}Lokasi: {self.download_path}{colors.RESET}")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                    
                output = line.decode().strip()
                if '%' in output and 'download' in output.lower():
                    print(f"\r{colors.CYAN}Progress: {output}{colors.RESET}", end='', flush=True)
            
            await process.wait()
            
            if process.returncode == 0:
                print(f"\n{colors.GREEN}✅ Video berhasil didownload!{colors.RESET}")
                return True
            else:
                print(f"\n{colors.RED}❌ Download gagal{colors.RESET}")
                return False
                
        except Exception as e:
            self.logger.error(f"Video download error: {e}")
            print(f"\n{colors.RED}❌ Error: {e}{colors.RESET}")
            return False

    async def download_audio(self, url: str, quality: str = 'best') -> bool:
        output_template = str(self.download_path / '%(title).100s.%(ext)s')
        
        cmd = [
            'yt-dlp',
            '--no-cache-dir',
            '--ignore-errors',
            '--continue',
            '--no-warnings',
            '--no-mtime',
            '--extract-audio',
            '--audio-format', 'mp3',
            '--audio-quality', '0' if quality == 'best' else '5',
            '--output', output_template,
            url
        ]
        
        print(f"\n{colors.CYAN}Memulai download audio...{colors.RESET}")
        print(f"{colors.CYAN}Lokasi: {self.download_path}{colors.RESET}")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT
            )
            
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                    
                output = line.decode().strip()
                if '%' in output and 'download' in output.lower():
                    print(f"\r{colors.CYAN}Progress: {output}{colors.RESET}", end='', flush=True)
            
            await process.wait()
            
            if process.returncode == 0:
                print(f"\n{colors.GREEN}✅ Audio berhasil didownload!{colors.RESET}")
                return True
            else:
                print(f"\n{colors.RED}Download gagal{colors.RESET}")
                return False
                
        except Exception as e:
            self.logger.error(f"Audio download error: {e}")
            print(f"\n{colors.RED}Error: {e}{colors.RESET}")
            return False

    def show_banner(self):
        banner = f"""
{colors.CYAN}🎬 Modern YouTube Downloader{colors.RESET}
{colors.CYAN}• version  : Enhanced v2.0{colors.RESET}
{colors.CYAN}• author   : Zidan{colors.RESET}
{colors.CYAN}• github   : https://github.com/zidanXcode{colors.RESET}
{colors.CYAN}• platform : {self.platform_info['system']} - {self.platform_info['release']}{colors.RESET}
{colors.CYAN}• python   : {self.platform_info['python_version']}{colors.RESET}
{colors.CYAN}• download : {str(self.download_path)}{colors.RESET}
        """
        print(banner)

    def show_menu(self) -> str:
        menu = f"""
{colors.BOLD}📋 Menu Options:{colors.RESET}
{colors.GREEN}[1]{colors.RESET} Download Video (MP4)
{colors.GREEN}[2]{colors.RESET} Download Audio (MP3)  
{colors.GREEN}[3]{colors.RESET} Batch Download (dari file)
{colors.GREEN}[4]{colors.RESET} Update yt-dlp
{colors.GREEN}[x]{colors.RESET} Exit

"""
        print(menu)
        return input(f"{colors.YELLOW}Pilihan Anda: {colors.RESET}").strip()

    async def batch_download(self, file_path: str):
        try:
            with open(file_path, 'r') as f:
                urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            if not urls:
                print(f"{colors.RED}✗ File kosong atau tidak valid{colors.RESET}")
                return
            
            print(f"{colors.CYAN}Memulai batch download {len(urls)} item...{colors.RESET}")
            
            for i, url in enumerate(urls, 1):
                print(f"\n{colors.YELLOW}[{i}/{len(urls)}]{colors.RESET} Processing: {url}")
                
                info = await self.get_video_info(url)
                if info:
                    print(f"🎬 {info.title}")
                    
                    choice = input(f"{colors.YELLOW}Download sebagai (v)ideo atau (a)udio? [v]: {colors.RESET}").lower()
                    
                    if choice == 'a':
                        await self.download_audio(url)
                    else:
                        await self.download_video(url)
                else:
                    print(f"{colors.RED}✗ Gagal mendapatkan info video{colors.RESET}")
                    
        except FileNotFoundError:
            print(f"{colors.RED}✗ File tidak ditemukan: {file_path}{colors.RESET}")
        except Exception as e:
            print(f"{colors.RED}✗ Error batch download: {e}{colors.RESET}")

    async def main_loop(self):
        if not await self.check_ytdlp_installation():
            print(f"{colors.RED}Silakan install yt-dlp terlebih dahulu:{colors.RESET}")
            print("pip install yt-dlp")
            return
        
        await self.update_ytdlp()
        
        while True:
            try:
                self.show_banner()
                choice = self.show_menu()
                
                if choice.lower() in ['x', 'exit', 'quit']:
                    print(f"{colors.CYAN}Terima kasih telah menggunakan YouTube Downloader!{colors.RESET}")
                    break
                
                elif choice == '1' or choice == '2':
                    query = input(f"\n{colors.YELLOW}Masukkan URL atau kata kunci pencarian: {colors.RESET}").strip()
                    
                    if not query:
                        continue
                    
                    video_info = None
                    
                    if self.is_valid_url(query):
                        video_info = await self.get_video_info(query)
                        if video_info:
                            print(f"\n{colors.BOLD}📺 Video Info:{colors.RESET}")
                            print(f"🎬 {video_info.title}")
                            print(f"👤 {video_info.uploader}")
                            print(f"⏱  {video_info.duration}")
                    else:
                        results = await self.search_youtube(query)
                        video_info = self.display_search_results(results)
                    
                    if video_info:
                        if choice == '1':
                            print(f"\n{colors.BOLD}Pilih Kualitas Video:{colors.RESET}")
                            print("1. Best (1080p)")
                            print("2. 720p")
                            print("3. 480p")
                            
                            quality_choice = input(f"{colors.YELLOW}Pilihan [1]: {colors.RESET}").strip()
                            quality_map = {'1': 'best', '2': '720p', '3': '480p'}
                            quality = quality_map.get(quality_choice, 'best')
                            
                            await self.download_video(video_info.url, quality)
                        else:
                            await self.download_audio(video_info.url)
                
                elif choice == '3':
                    file_path = input(f"{colors.YELLOW}Path file URL (satu URL per baris): {colors.RESET}").strip()
                    await self.batch_download(file_path)
                
                elif choice == '4':
                    await self.update_ytdlp()
                
                else:
                    print(f"{colors.RED}✗ Pilihan tidak valid{colors.RESET}")
                    continue
                
                input(f"\n{colors.YELLOW}Tekan Enter untuk melanjutkan...{colors.RESET}")
                
            except KeyboardInterrupt:
                print(f"\n{colors.CYAN}Program dihentikan oleh user{colors.RESET}")
                break
            except EOFError:
                break
            except Exception as e:
                self.logger.error(f"Main loop error: {e}")
                print(f"{colors.RED}Unexpected error: {e}{colors.RESET}")

def main():
    parser = argparse.ArgumentParser(description='Modern YouTube Downloader')
    parser.add_argument('--url', help='Direct URL to download')
    parser.add_argument('--audio', action='store_true', help='Download audio only')
    parser.add_argument('--batch', help='Batch download from file')
    parser.add_argument('--quality', default='best', help='Video quality (best, 1080p, 720p, 480p)')
    
    args = parser.parse_args()
    
    downloader = ModernYTDownloader()
    
    if args.url:
        async def direct_download():
            if args.audio:
                await downloader.download_audio(args.url, args.quality)
            else:
                await downloader.download_video(args.url, args.quality)
        
        asyncio.run(direct_download())
    elif args.batch:
        asyncio.run(downloader.batch_download(args.batch))
    else:
        asyncio.run(downloader.main_loop())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{colors.CYAN}Program dihentikan{colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{colors.RED}Fatal error: {e}{colors.RESET}")
        sys.exit(1)
