#!/usr/bin/env python3
"""
Real-time Microphone Speech Detection
Continuously monitors audio input and displays speech detection status
"""

import webrtcvad
import pyaudio
import numpy as np
import threading
import time
import sys
import signal
from collections import deque
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle


class RealtimeSpeechDetector:
    """Real-time speech detection using microphone input"""
    
    def __init__(self, aggressiveness: int = 2, frame_duration_ms: int = 30, 
                 sample_rate: int = 16000, chunk_size: int = 1024):
        """
        Initialize the real-time speech detector
        
        Args:
            aggressiveness: VAD aggressiveness level (0-3)
            frame_duration_ms: Frame duration in milliseconds (10, 20, or 30)
            sample_rate: Audio sample rate in Hz
            chunk_size: Audio chunk size for PyAudio
        """
        self.vad = webrtcvad.Vad(aggressiveness)
        self.aggressiveness = aggressiveness
        self.frame_duration_ms = frame_duration_ms
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        
        # Calculate frame size for VAD
        self.frame_size = int(sample_rate * (frame_duration_ms / 1000.0))
        
        # Audio buffer for frame accumulation
        self.audio_buffer = deque(maxlen=self.frame_size * 2)
        
        # Speech detection state
        self.is_speaking = False
        self.speech_start_time = None
        self.speech_regions = []
        self.current_region = None
        
        # Statistics
        self.total_frames = 0
        self.speech_frames = 0
        self.session_start_time = time.time()
        
        # Control flags
        self.running = False
        self.audio_thread = None
        self.visualization_thread = None
        
        # Visualization data
        self.speech_history = deque(maxlen=200)  # Keep last 200 frames
        self.time_history = deque(maxlen=200)
        
        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
        
        print(f"🎤 Real-time Speech Detector initialized")
        print(f"   Sample rate: {sample_rate} Hz")
        print(f"   Frame duration: {frame_duration_ms} ms")
        print(f"   VAD aggressiveness: {aggressiveness}")
        print(f"   Frame size: {self.frame_size} samples")
    
    def find_audio_device(self):
        """Find and return the default audio input device"""
        try:
            # Try to get default input device
            default_device = self.audio.get_default_input_device_info()
            print(f"✓ Using default audio device: {default_device['name']}")
            return default_device['index']
        except Exception as e:
            print(f"⚠️  Could not get default device: {e}")
            # List available devices
            print("\nAvailable audio input devices:")
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    print(f"  {i}: {device_info['name']} (inputs: {device_info['maxInputChannels']})")
            return 0  # Fallback to first device
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback for processing audio data"""
        if status:
            print(f"Audio callback status: {status}")
        
        # Convert bytes to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        
        # Add to buffer
        self.audio_buffer.extend(audio_data)
        
        # Process when we have enough data for a frame
        if len(self.audio_buffer) >= self.frame_size:
            # Extract frame
            frame = np.array(list(self.audio_buffer)[:self.frame_size])
            self.audio_buffer = deque(list(self.audio_buffer)[self.frame_size:], maxlen=self.frame_size * 2)
            
            # Process frame
            self.process_audio_frame(frame)
        
        return (in_data, pyaudio.paContinue)
    
    def process_audio_frame(self, frame):
        """Process a single audio frame for speech detection"""
        try:
            # Convert to bytes for VAD
            frame_bytes = frame.tobytes()
            is_speech = self.vad.is_speech(frame_bytes, self.sample_rate)
            
            # Update statistics
            self.total_frames += 1
            if is_speech:
                self.speech_frames += 1
            
            # Update speech state
            current_time = time.time()
            frame_timestamp = current_time - self.session_start_time
            
            if is_speech:
                if not self.is_speaking:
                    # Start of speech
                    self.is_speaking = True
                    self.speech_start_time = current_time
                    self.current_region = {
                        'start_time': frame_timestamp,
                        'start_real_time': current_time,
                        'frame_count': 1
                    }
                    print(f"🎤 Speech started at {frame_timestamp:.2f}s")
                else:
                    # Continue speech
                    if self.current_region:
                        self.current_region['frame_count'] += 1
            else:
                if self.is_speaking:
                    # End of speech
                    self.is_speaking = False
                    if self.current_region:
                        self.current_region['end_time'] = frame_timestamp
                        self.current_region['end_real_time'] = current_time
                        self.current_region['duration'] = self.current_region['end_time'] - self.current_region['start_time']
                        self.speech_regions.append(self.current_region)
                        print(f"🔇 Speech ended at {frame_timestamp:.2f}s (duration: {self.current_region['duration']:.2f}s)")
                        self.current_region = None
            
            # Update visualization data
            self.speech_history.append(1 if is_speech else 0)
            self.time_history.append(frame_timestamp)
            
        except Exception as e:
            print(f"⚠️  Error processing frame: {e}")
    
    def start_audio_stream(self):
        """Start the audio input stream"""
        try:
            device_index = self.find_audio_device()
            
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=self.audio_callback
            )
            
            self.stream.start_stream()
            print("✓ Audio stream started")
            
        except Exception as e:
            print(f"❌ Error starting audio stream: {e}")
            raise
    
    def stop_audio_stream(self):
        """Stop the audio input stream"""
        if hasattr(self, 'stream') and self.stream.is_active():
            self.stream.stop_stream()
            self.stream.close()
            print("✓ Audio stream stopped")
        
        self.audio.terminate()
    
    def print_status(self):
        """Print current status information"""
        current_time = time.time() - self.session_start_time
        speech_percentage = (self.speech_frames / self.total_frames * 100) if self.total_frames > 0 else 0
        
        print(f"\r⏱️  Time: {current_time:.1f}s | "
              f"Frames: {self.total_frames} | "
              f"Speech: {self.speech_frames} ({speech_percentage:.1f}%) | "
              f"Regions: {len(self.speech_regions)} | "
              f"Status: {'🎤 SPEAKING' if self.is_speaking else '🔇 SILENT'}", end='', flush=True)
    
    def create_realtime_visualization(self):
        """Create real-time visualization of speech detection"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        def animate(frame):
            ax1.clear()
            ax2.clear()
            
            if len(self.time_history) > 0:
                # Plot 1: Real-time speech activity
                times = list(self.time_history)
                speech = list(self.speech_history)
                
                ax1.plot(times, speech, 'b-', linewidth=2)
                ax1.fill_between(times, 0, speech, alpha=0.3, color='green')
                ax1.set_title('Real-time Speech Detection', fontsize=14, fontweight='bold')
                ax1.set_ylabel('Speech Activity')
                ax1.set_ylim(-0.1, 1.1)
                ax1.grid(True, alpha=0.3)
                
                # Add current status
                status_text = 'SPEAKING' if self.is_speaking else 'SILENT'
                status_color = 'green' if self.is_speaking else 'red'
                ax1.text(0.02, 0.95, f"Status: {status_text}", 
                        transform=ax1.transAxes, fontsize=12, fontweight='bold',
                        bbox=dict(boxstyle='round', facecolor=status_color, alpha=0.3))
                
                # Plot 2: Speech regions timeline
                ax2.set_title('Speech Regions Timeline', fontsize=14, fontweight='bold')
                ax2.set_ylabel('Region')
                ax2.set_xlabel('Time (seconds)')
                ax2.grid(True, alpha=0.3)
                
                # Plot speech regions
                for i, region in enumerate(self.speech_regions[-10:]):  # Show last 10 regions
                    start_time = region['start_time']
                    duration = region['duration']
                    ax2.barh(i, duration, left=start_time, height=0.8, 
                            alpha=0.7, color='green', edgecolor='darkgreen')
                    ax2.text(start_time + duration/2, i, f'R{len(self.speech_regions)-10+i+1}', 
                            ha='center', va='center', fontsize=8, fontweight='bold')
                
                # Add current region if speaking
                if self.is_speaking and self.current_region:
                    current_duration = time.time() - self.session_start_time - self.current_region['start_time']
                    ax2.barh(len(self.speech_regions), current_duration, 
                            left=self.current_region['start_time'], height=0.8,
                            alpha=0.5, color='orange', edgecolor='red')
                    ax2.text(self.current_region['start_time'] + current_duration/2, 
                            len(self.speech_regions), 'CURRENT', 
                            ha='center', va='center', fontsize=8, fontweight='bold')
                
                # Set axis limits
                if times:
                    ax1.set_xlim(max(0, times[-1] - 30), times[-1] + 2)  # Show last 30 seconds
                    ax2.set_xlim(max(0, times[-1] - 30), times[-1] + 2)
        
        # Start animation
        ani = animation.FuncAnimation(fig, animate, interval=100, blit=False)
        plt.tight_layout()
        plt.show()
        
        return ani
    
    def run_console_mode(self):
        """Run in console mode with status updates"""
        print("\n🎤 Starting real-time speech detection...")
        print("Press Ctrl+C to stop")
        
        try:
            self.start_audio_stream()
            self.running = True
            
            while self.running:
                self.print_status()
                time.sleep(0.1)  # Update every 100ms
                
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping speech detection...")
        finally:
            self.running = False
            self.stop_audio_stream()
            self.print_final_stats()
    
    def run_visualization_mode(self):
        """Run with real-time visualization"""
        print("\n🎤 Starting real-time speech detection with visualization...")
        print("Close the plot window to stop")
        
        try:
            self.start_audio_stream()
            self.running = True
            
            # Start visualization in a separate thread
            viz_thread = threading.Thread(target=self.create_realtime_visualization)
            viz_thread.daemon = True
            viz_thread.start()
            
            # Keep running until plot is closed
            while self.running and viz_thread.is_alive():
                time.sleep(0.1)
                
        except Exception as e:
            print(f"❌ Error in visualization mode: {e}")
        finally:
            self.running = False
            self.stop_audio_stream()
            self.print_final_stats()
    
    def print_final_stats(self):
        """Print final statistics"""
        total_time = time.time() - self.session_start_time
        speech_percentage = (self.speech_frames / self.total_frames * 100) if self.total_frames > 0 else 0
        total_speech_time = sum(region['duration'] for region in self.speech_regions)
        
        print(f"\n\n📊 Final Statistics:")
        print(f"   Total session time: {total_time:.2f}s")
        print(f"   Total frames processed: {self.total_frames}")
        print(f"   Speech frames: {self.speech_frames} ({speech_percentage:.1f}%)")
        print(f"   Speech regions detected: {len(self.speech_regions)}")
        print(f"   Total speech time: {total_speech_time:.2f}s")
        print(f"   Average region duration: {total_speech_time/len(self.speech_regions):.2f}s" if self.speech_regions else "   No speech regions detected")
        
        if self.speech_regions:
            print(f"\n📝 Speech Regions:")
            for i, region in enumerate(self.speech_regions[-5:], 1):  # Show last 5 regions
                print(f"   Region {i}: {region['start_time']:.2f}s - {region['end_time']:.2f}s "
                      f"(duration: {region['duration']:.2f}s, frames: {region['frame_count']})")


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n🛑 Received interrupt signal. Stopping...")
    sys.exit(0)


def main():
    """Main function for real-time speech detection"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Real-time Speech Detection Demo")
        print("\nUsage:")
        print("  python realtime_microphone.py [--visualization] [--aggressiveness N]")
        print("\nOptions:")
        print("  --visualization    Show real-time plot (requires matplotlib)")
        print("  --aggressiveness N Set VAD aggressiveness (0-3, default: 2)")
        print("\nExamples:")
        print("  python realtime_microphone.py")
        print("  python realtime_microphone.py --visualization")
        print("  python realtime_microphone.py --aggressiveness 3")
        sys.exit(0)
    
    # Parse command line arguments
    use_visualization = '--visualization' in sys.argv
    aggressiveness = 2
    
    for i, arg in enumerate(sys.argv):
        if arg == '--aggressiveness' and i + 1 < len(sys.argv):
            try:
                aggressiveness = int(sys.argv[i + 1])
                if not 0 <= aggressiveness <= 3:
                    print("Error: Aggressiveness must be between 0 and 3")
                    sys.exit(1)
            except ValueError:
                print("Error: Aggressiveness must be a number")
                sys.exit(1)
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and run detector
    detector = RealtimeSpeechDetector(aggressiveness=aggressiveness)
    
    try:
        if use_visualization:
            detector.run_visualization_mode()
        else:
            detector.run_console_mode()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()