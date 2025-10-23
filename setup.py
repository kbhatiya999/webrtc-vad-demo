#!/usr/bin/env python3
"""
Setup script for Advanced WebRTC VAD Demo
Installs dependencies and downloads sample audio
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from download_audio import YouTubeAudioDownloader


def run_command(command: str, description: str) -> bool:
    """
    Run a shell command and return success status
    
    Args:
        command: Command to run
        description: Description of what the command does
        
    Returns:
        True if successful, False otherwise
    """
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False


def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    # Check if pip is available
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ pip not found. Please install pip first.")
        return False
    
    # Install requirements
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", 
                      "Installing requirements"):
        return False
    
    # Install system dependencies for pyaudio (if on Linux)
    if sys.platform.startswith('linux'):
        print("🔧 Installing system dependencies for audio processing...")
        run_command("sudo apt-get update", "Updating package list")
        run_command("sudo apt-get install -y portaudio19-dev python3-pyaudio", 
                   "Installing PortAudio development libraries")
    
    return True


def download_sample_audio(video_url: str = None, channel_url: str = None, 
                         video_index: int = 0, duration_limit: int = 60):
    """
    Download sample audio for testing
    
    Args:
        video_url: Specific YouTube video URL
        channel_url: YouTube channel URL
        video_index: Index of video from channel
        duration_limit: Maximum duration in seconds
    """
    print("🎵 Downloading sample audio...")
    
    downloader = YouTubeAudioDownloader()
    
    # Check if sample audio already exists
    sample_file = Path("sample_audio.wav")
    if sample_file.exists():
        print(f"⚠️  Sample audio already exists: {sample_file}")
        response = input("   Do you want to replace it? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("✓ Keeping existing sample audio")
            return True
    
    success = False
    
    if video_url:
        # Download specific video
        print(f"🎯 Downloading from specific video: {video_url}")
        success = downloader.download_audio(video_url, "sample_audio.wav", duration_limit)
        
    elif channel_url:
        # Download from channel
        print(f"🎯 Downloading from channel: {channel_url}")
        success = downloader.download_from_channel(
            channel_url, "sample_audio.wav", duration_limit, video_index
        )
        
    else:
        # Try AdamSeekerOfficial channel first, then fallback to default videos
        print("🎯 Trying AdamSeekerOfficial channel...")
        adam_seeker_url = "https://www.youtube.com/@AdamSeekerOfficial"
        
        # List available videos first
        videos = downloader.get_channel_videos(adam_seeker_url, max_videos=5)
        if videos:
            print(f"📺 Found {len(videos)} videos from AdamSeekerOfficial:")
            for i, video in enumerate(videos[:3]):  # Show first 3
                duration_str = f"{video['duration']//60}:{video['duration']%60:02d}" if video['duration'] else "Unknown"
                print(f"   {i+1}. {video['title'][:50]} ({duration_str})")
            
            success = downloader.download_from_channel(
                adam_seeker_url, "sample_audio.wav", duration_limit, video_index
            )
        
        if not success:
            print("⚠️  AdamSeekerOfficial channel not available, trying default videos...")
            for i, video_url in enumerate(downloader.default_videos):
                print(f"\nTrying default video {i+1}/{len(downloader.default_videos)}...")
                if downloader.download_audio(video_url, "sample_audio.wav", duration_limit):
                    success = True
                    break
    
    if success:
        print("✅ Sample audio downloaded successfully!")
        
        # Verify the file
        if sample_file.exists():
            file_size = sample_file.stat().st_size
            print(f"📁 File: {sample_file} ({file_size:,} bytes)")
            
            # Test the audio file
            print("🧪 Testing audio file...")
            try:
                from audio_processor import AudioProcessor
                processor = AudioProcessor(aggressiveness=2)
                audio_data, sample_rate, channels = processor.read_wav_file(str(sample_file))
                print(f"✓ Audio file is valid: {sample_rate}Hz, {channels} channel(s), {len(audio_data)} samples")
            except Exception as e:
                print(f"⚠️  Audio file validation failed: {e}")
        else:
            print("❌ Sample audio file not found after download")
            return False
    else:
        print("❌ Failed to download sample audio")
        return False
    
    return True


def create_desktop_shortcuts():
    """Create desktop shortcuts for easy access (optional)"""
    print("🔗 Creating desktop shortcuts...")
    
    # This is a placeholder - actual implementation would depend on the OS
    print("💡 Desktop shortcuts not implemented in this version")
    print("   You can run the demo with: python3 demo.py")


def verify_installation():
    """Verify that the installation is working correctly"""
    print("🧪 Verifying installation...")
    
    try:
        # Test imports
        import webrtcvad
        import numpy
        import matplotlib
        import scipy
        import yt_dlp
        import pydub
        print("✅ All Python packages imported successfully")
        
        # Test VAD initialization
        vad = webrtcvad.Vad(2)
        print("✅ WebRTC VAD initialized successfully")
        
        # Test audio processing
        from audio_processor import AudioProcessor
        processor = AudioProcessor(aggressiveness=2)
        print("✅ Audio processor created successfully")
        
        # Test real-time detector (without starting audio)
        from realtime_microphone import RealtimeSpeechDetector
        detector = RealtimeSpeechDetector(aggressiveness=2)
        print("✅ Real-time detector created successfully")
        
        print("🎉 Installation verification completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Installation verification failed: {e}")
        return False


def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(
        description="Setup script for Advanced WebRTC VAD Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 setup.py                                    # Full setup with default audio
  python3 setup.py --video-url "https://youtube.com/watch?v=VIDEO_ID"
  python3 setup.py --channel "https://youtube.com/@ChannelName" --video-index 1
  python3 setup.py --no-audio                        # Skip audio download
  python3 setup.py --verify-only                     # Only verify installation
        """
    )
    
    parser.add_argument('--video-url', '-u', type=str, 
                       help='Specific YouTube video URL to download')
    parser.add_argument('--channel', '-c', type=str,
                       help='YouTube channel URL to download from')
    parser.add_argument('--video-index', '-i', type=int, default=0,
                       help='Index of video from channel (0-based, default: 0)')
    parser.add_argument('--duration-limit', '-d', type=int, default=60,
                       help='Maximum duration in seconds (0 = no limit, default: 60)')
    parser.add_argument('--no-audio', action='store_true',
                       help='Skip audio download step')
    parser.add_argument('--verify-only', action='store_true',
                       help='Only verify installation, skip setup')
    parser.add_argument('--no-deps', action='store_true',
                       help='Skip dependency installation')
    
    args = parser.parse_args()
    
    print("🎵 Advanced WebRTC VAD Demo - Setup")
    print("=" * 50)
    
    # Verify only mode
    if args.verify_only:
        success = verify_installation()
        sys.exit(0 if success else 1)
    
    # Install dependencies
    if not args.no_deps:
        if not install_dependencies():
            print("❌ Dependency installation failed!")
            sys.exit(1)
    else:
        print("⏭️  Skipping dependency installation")
    
    # Download sample audio
    if not args.no_audio:
        if not download_sample_audio(
            video_url=args.video_url,
            channel_url=args.channel,
            video_index=args.video_index,
            duration_limit=args.duration_limit
        ):
            print("❌ Audio download failed!")
            sys.exit(1)
    else:
        print("⏭️  Skipping audio download")
    
    # Verify installation
    if not verify_installation():
        print("❌ Installation verification failed!")
        sys.exit(1)
    
    # Create shortcuts (optional)
    create_desktop_shortcuts()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📚 Next steps:")
    print("   1. Run the demo: python3 demo.py")
    print("   2. Process audio: python3 demo.py --audio sample_audio.wav")
    print("   3. Real-time detection: python3 demo.py --realtime")
    print("   4. Get help: python3 demo.py --help")
    print("\n📖 For more information, see README.md")


if __name__ == "__main__":
    main()