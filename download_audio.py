#!/usr/bin/env python3
"""
YouTube Audio Downloader for WebRTC VAD Demo
Downloads audio from YouTube videos and converts to WAV format for processing
"""

import os
import sys
import subprocess
import argparse
import json
from pathlib import Path
from typing import Optional, List, Dict
import yt_dlp
from pydub import AudioSegment


class YouTubeAudioDownloader:
    """Downloads and processes audio from YouTube videos"""
    
    def __init__(self, output_dir: str = "."):
        """
        Initialize the downloader
        
        Args:
            output_dir: Directory to save downloaded audio files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Default AdamSeekerOfficial videos (short, clear speech)
        self.default_videos = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up (classic)
            "https://www.youtube.com/watch?v=9bZkp7q19f0",  # PSY - GANGNAM STYLE
            "https://www.youtube.com/watch?v=kJQP7kiw5Fk",  # Luis Fonsi - Despacito
        ]
        
        # AdamSeekerOfficial channel videos (if available)
        self.adam_seeker_videos = [
            "https://www.youtube.com/watch?v=example1",  # Replace with actual video IDs
            "https://www.youtube.com/watch?v=example2",
        ]
    
    def get_channel_videos(self, channel_url: str, max_videos: int = 10) -> List[Dict]:
        """
        Get list of videos from a YouTube channel
        
        Args:
            channel_url: YouTube channel URL
            max_videos: Maximum number of videos to fetch
            
        Returns:
            List of video information dictionaries
        """
        print(f"🔍 Fetching videos from channel: {channel_url}")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'playlistend': max_videos,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(channel_url, download=False)
                
                if 'entries' in info:
                    videos = []
                    for entry in info['entries']:
                        if entry and 'id' in entry:
                            videos.append({
                                'id': entry['id'],
                                'title': entry.get('title', 'Unknown'),
                                'duration': entry.get('duration', 0),
                                'url': f"https://www.youtube.com/watch?v={entry['id']}"
                            })
                    return videos
                else:
                    print("❌ No videos found in channel")
                    return []
                    
        except Exception as e:
            print(f"❌ Error fetching channel videos: {e}")
            return []
    
    def get_video_info(self, video_url: str) -> Optional[Dict]:
        """
        Get information about a specific video
        
        Args:
            video_url: YouTube video URL
            
        Returns:
            Video information dictionary or None if error
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                return {
                    'id': info.get('id'),
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'url': video_url
                }
        except Exception as e:
            print(f"❌ Error getting video info: {e}")
            return None
    
    def download_audio(self, video_url: str, output_filename: str = "sample_audio.wav", 
                      duration_limit: int = 60) -> bool:
        """
        Download audio from YouTube video and convert to WAV
        
        Args:
            video_url: YouTube video URL
            output_filename: Output WAV filename
            duration_limit: Maximum duration in seconds (0 = no limit)
            
        Returns:
            True if successful, False otherwise
        """
        print(f"🎵 Downloading audio from: {video_url}")
        
        # Get video info first
        video_info = self.get_video_info(video_url)
        if not video_info:
            return False
        
        print(f"📺 Video: {video_info['title']}")
        print(f"👤 Uploader: {video_info['uploader']}")
        print(f"⏱️  Duration: {video_info['duration']}s")
        
        # Check duration limit
        if duration_limit > 0 and video_info['duration'] > duration_limit:
            print(f"⚠️  Video duration ({video_info['duration']}s) exceeds limit ({duration_limit}s)")
            print("   Consider using --duration-limit 0 to disable limit")
            return False
        
        # Configure yt-dlp options
        temp_filename = f"temp_audio_{video_info['id']}.%(ext)s"
        temp_path = self.output_dir / temp_filename
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(temp_path),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            # Download audio
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            # Find the downloaded file
            temp_files = list(self.output_dir.glob(f"temp_audio_{video_info['id']}.*"))
            if not temp_files:
                print("❌ Downloaded file not found")
                return False
            
            temp_file = temp_files[0]
            print(f"✓ Audio downloaded: {temp_file.name}")
            
            # Convert to WAV format
            output_path = self.output_dir / output_filename
            success = self.convert_to_wav(str(temp_file), str(output_path))
            
            # Clean up temp file
            temp_file.unlink()
            
            if success:
                print(f"✅ Audio converted and saved: {output_path}")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ Error downloading audio: {e}")
            return False
    
    def convert_to_wav(self, input_file: str, output_file: str) -> bool:
        """
        Convert audio file to WAV format (16-bit, 16kHz mono)
        
        Args:
            input_file: Input audio file path
            output_file: Output WAV file path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print("🔄 Converting to WAV format (16-bit, 16kHz mono)...")
            
            # Load audio file
            audio = AudioSegment.from_file(input_file)
            
            # Convert to mono
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # Set sample rate to 16kHz
            audio = audio.set_frame_rate(16000)
            
            # Set sample width to 16-bit
            audio = audio.set_sample_width(2)
            
            # Export as WAV
            audio.export(output_file, format="wav")
            
            # Verify the file
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"✓ WAV file created: {file_size:,} bytes")
                return True
            else:
                print("❌ WAV file not created")
                return False
                
        except Exception as e:
            print(f"❌ Error converting to WAV: {e}")
            return False
    
    def list_channel_videos(self, channel_url: str, max_videos: int = 10):
        """
        List videos from a YouTube channel
        
        Args:
            channel_url: YouTube channel URL
            max_videos: Maximum number of videos to show
        """
        videos = self.get_channel_videos(channel_url, max_videos)
        
        if not videos:
            print("❌ No videos found")
            return
        
        print(f"\n📺 Found {len(videos)} videos from channel:")
        print("-" * 80)
        
        for i, video in enumerate(videos, 1):
            duration_str = f"{video['duration']//60}:{video['duration']%60:02d}" if video['duration'] else "Unknown"
            print(f"{i:2d}. {video['title'][:60]:<60} ({duration_str})")
            print(f"    URL: {video['url']}")
            print()
    
    def download_from_channel(self, channel_url: str, output_filename: str = "sample_audio.wav",
                             duration_limit: int = 60, video_index: int = 0) -> bool:
        """
        Download audio from a specific video in a channel
        
        Args:
            channel_url: YouTube channel URL
            output_filename: Output WAV filename
            duration_limit: Maximum duration in seconds
            video_index: Index of video to download (0-based)
            
        Returns:
            True if successful, False otherwise
        """
        videos = self.get_channel_videos(channel_url, max_videos=video_index + 5)
        
        if not videos:
            print("❌ No videos found in channel")
            return False
        
        if video_index >= len(videos):
            print(f"❌ Video index {video_index} out of range (max: {len(videos)-1})")
            return False
        
        selected_video = videos[video_index]
        print(f"🎯 Selected video: {selected_video['title']}")
        
        return self.download_audio(selected_video['url'], output_filename, duration_limit)


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(
        description="Download audio from YouTube videos for WebRTC VAD processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python download_audio.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
  python download_audio.py --channel "https://www.youtube.com/@AdamSeekerOfficial" --index 0
  python download_audio.py --list-channel "https://www.youtube.com/@AdamSeekerOfficial"
  python download_audio.py --default
        """
    )
    
    parser.add_argument('--url', '-u', type=str, help='YouTube video URL to download')
    parser.add_argument('--channel', '-c', type=str, help='YouTube channel URL')
    parser.add_argument('--index', '-i', type=int, default=0, help='Video index from channel (0-based)')
    parser.add_argument('--output', '-o', type=str, default='sample_audio.wav', 
                       help='Output WAV filename (default: sample_audio.wav)')
    parser.add_argument('--duration-limit', '-d', type=int, default=60,
                       help='Maximum duration in seconds (0 = no limit, default: 60)')
    parser.add_argument('--list-channel', '-l', type=str, 
                       help='List videos from a channel')
    parser.add_argument('--default', action='store_true',
                       help='Download from default video list')
    parser.add_argument('--adam-seeker', action='store_true',
                       help='Download from AdamSeekerOfficial channel')
    
    args = parser.parse_args()
    
    # Create downloader
    downloader = YouTubeAudioDownloader()
    
    print("🎵 YouTube Audio Downloader for WebRTC VAD")
    print("=" * 50)
    
    success = False
    
    if args.list_channel:
        # List channel videos
        downloader.list_channel_videos(args.list_channel)
        success = True
        
    elif args.url:
        # Download specific video
        success = downloader.download_audio(args.url, args.output, args.duration_limit)
        
    elif args.channel:
        # Download from channel
        success = downloader.download_from_channel(
            args.channel, args.output, args.duration_limit, args.index
        )
        
    elif args.adam_seeker:
        # Download from AdamSeekerOfficial channel
        channel_url = "https://www.youtube.com/@AdamSeekerOfficial"
        print(f"🎯 Downloading from AdamSeekerOfficial channel...")
        success = downloader.download_from_channel(
            channel_url, args.output, args.duration_limit, args.index
        )
        
    elif args.default:
        # Download from default videos
        print("🎯 Downloading from default video list...")
        for i, video_url in enumerate(downloader.default_videos):
            print(f"\nTrying video {i+1}/{len(downloader.default_videos)}...")
            if downloader.download_audio(video_url, args.output, args.duration_limit):
                success = True
                break
        if not success:
            print("❌ Failed to download from all default videos")
            
    else:
        print("❌ No action specified. Use --help for usage information.")
        parser.print_help()
        sys.exit(1)
    
    if success:
        print(f"\n✅ Audio download completed successfully!")
        print(f"📁 Output file: {args.output}")
        print(f"\n💡 You can now process the audio with:")
        print(f"   python3 demo.py --audio {args.output}")
    else:
        print(f"\n❌ Audio download failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()