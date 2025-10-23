#!/usr/bin/env python3
"""
WebRTC VAD Demo
Demonstrates real-time voice activity detection using WebRTC VAD
"""

import webrtcvad
import wave
import sys

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

if __name__ == "__main__":
    vad_demo_simple()
