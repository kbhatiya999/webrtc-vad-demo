#!/usr/bin/env python3
"""
Advanced WebRTC VAD Demo
Comprehensive demonstration of voice activity detection with audio processing and real-time monitoring
"""

import webrtcvad
import wave
import sys
import os
import argparse
from audio_processor import AudioProcessor
from realtime_microphone import RealtimeSpeechDetector


def read_wave(path):
    """Reads a .wav file and returns PCM audio data"""
    with wave.open(path, 'rb') as wf:
        num_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        sample_rate = wf.getframerate()
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate


def frame_generator(frame_duration_ms, audio, sample_rate):
    """Generates audio frames from PCM audio data"""
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    while offset + n < len(audio):
        yield audio[offset:offset + n]
        offset += n


def vad_demo_simple():
    """Simple VAD demo without audio file"""
    print("=== WebRTC VAD Simple Demo ===")
    print("\nInitializing VAD with different aggressiveness modes...\n")
    
    # Create VAD instances with different aggressiveness
    for mode in range(4):
        vad = webrtcvad.Vad(mode)
        print(f"Mode {mode}: VAD initialized successfully")
    
    print("\n✓ VAD library is working correctly!")
    print("\nAggressiveness levels:")
    print("  0: Quality mode (least aggressive)")
    print("  1: Low bitrate mode")
    print("  2: Aggressive mode")
    print("  3: Very aggressive mode (most noise filtering)")


def demo_audio_processing(audio_file, aggressiveness=2):
    """Demo advanced audio file processing"""
    print(f"\n{'='*60}")
    print(f"🎵 Advanced Audio File Processing Demo")
    print(f"{'='*60}")
    
    if not os.path.exists(audio_file):
        print(f"❌ Error: Audio file '{audio_file}' not found")
        return
    
    try:
        processor = AudioProcessor(aggressiveness=aggressiveness)
        results = processor.process_audio_file(audio_file)
        
        print(f"\n✅ Processing complete!")
        print(f"   JSON results: {results['json_file']}")
        print(f"   Visualization: {results['visualization_file']}")
        print(f"   Speech regions: {results['speech_regions_count']}")
        
    except Exception as e:
        print(f"❌ Error processing audio file: {e}")


def demo_realtime_detection(use_visualization=False, aggressiveness=2):
    """Demo real-time microphone speech detection"""
    print(f"\n{'='*60}")
    print(f"🎤 Real-time Microphone Speech Detection Demo")
    print(f"{'='*60}")
    
    try:
        detector = RealtimeSpeechDetector(aggressiveness=aggressiveness)
        
        if use_visualization:
            detector.run_visualization_mode()
        else:
            detector.run_console_mode()
            
    except Exception as e:
        print(f"❌ Error in real-time detection: {e}")


def create_sample_audio():
    """Create a sample audio file for testing (if no audio file is provided)"""
    print("\n📝 Creating sample audio file for testing...")
    
    try:
        import numpy as np
        import wave
        
        # Generate a simple test signal with speech-like patterns
        sample_rate = 16000
        duration = 5  # seconds
        
        # Create time array
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Generate a signal with alternating speech and silence
        # Speech regions: 0-1s, 2-3s, 4-5s
        audio = np.zeros_like(t)
        
        # Add speech-like content (sine waves with modulation)
        speech_regions = [(0, 1), (2, 3), (4, 5)]
        for start, end in speech_regions:
            mask = (t >= start) & (t < end)
            # Create a modulated sine wave to simulate speech
            freq = 200 + 50 * np.sin(2 * np.pi * 2 * t[mask])  # Frequency modulation
            audio[mask] = 0.3 * np.sin(2 * np.pi * freq * t[mask]) * np.sin(2 * np.pi * 10 * t[mask])
        
        # Add some noise
        noise = 0.05 * np.random.randn(len(t))
        audio += noise
        
        # Convert to 16-bit PCM
        audio_16bit = (audio * 32767).astype(np.int16)
        
        # Save as WAV file
        sample_file = "sample_audio.wav"
        with wave.open(sample_file, 'wb') as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)
            wf.writeframes(audio_16bit.tobytes())
        
        print(f"✓ Sample audio file created: {sample_file}")
        print(f"   Duration: {duration}s")
        print(f"   Sample rate: {sample_rate} Hz")
        print(f"   Speech regions: {speech_regions}")
        
        return sample_file
        
    except Exception as e:
        print(f"❌ Error creating sample audio: {e}")
        return None


def main():
    """Main demo function with command line interface"""
    parser = argparse.ArgumentParser(
        description="Advanced WebRTC VAD Demo - Audio processing and real-time speech detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python demo.py                                    # Run simple VAD demo
  python demo.py --audio sample.wav                # Process audio file
  python demo.py --realtime                        # Start real-time detection
  python demo.py --realtime --visualization        # Real-time with plot
  python demo.py --create-sample                   # Create sample audio file
  python demo.py --audio sample.wav --aggressiveness 3  # Process with high aggressiveness
        """
    )
    
    parser.add_argument('--audio', '-a', type=str, help='Audio file to process')
    parser.add_argument('--realtime', '-r', action='store_true', help='Start real-time microphone detection')
    parser.add_argument('--visualization', '-v', action='store_true', help='Show real-time visualization plot')
    parser.add_argument('--aggressiveness', type=int, default=2, choices=[0,1,2,3], 
                       help='VAD aggressiveness level (0-3, default: 2)')
    parser.add_argument('--create-sample', action='store_true', help='Create a sample audio file for testing')
    parser.add_argument('--simple', action='store_true', help='Run only the simple VAD demo')
    
    args = parser.parse_args()
    
    print("🎵 Advanced WebRTC VAD Demo")
    print("=" * 50)
    
    # Create sample audio if requested
    if args.create_sample:
        sample_file = create_sample_audio()
        if sample_file:
            print(f"\nYou can now process this sample file with:")
            print(f"  python demo.py --audio {sample_file}")
        return
    
    # Run simple demo if requested or no other options
    if args.simple or (not args.audio and not args.realtime):
        vad_demo_simple()
        
        if not args.simple:
            print(f"\n💡 Try other features:")
            print(f"   python demo.py --help                    # Show all options")
            print(f"   python demo.py --create-sample          # Create test audio")
            print(f"   python demo.py --realtime               # Real-time detection")
            print(f"   python demo.py --audio <file.wav>       # Process audio file")
    
    # Process audio file
    if args.audio:
        demo_audio_processing(args.audio, args.aggressiveness)
    
    # Run real-time detection
    if args.realtime:
        demo_realtime_detection(args.visualization, args.aggressiveness)


if __name__ == "__main__":
    main()
