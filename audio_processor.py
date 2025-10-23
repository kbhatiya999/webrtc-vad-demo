#!/usr/bin/env python3
"""
Advanced Audio Processing with WebRTC VAD
Processes WAV files frame-by-frame, detects speech regions, and visualizes results
"""

import webrtcvad
import wave
import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime
import os
import sys
from typing import List, Tuple, Dict, Any


class AudioProcessor:
    """Advanced audio processor with WebRTC VAD integration"""
    
    def __init__(self, aggressiveness: int = 2, frame_duration_ms: int = 30):
        """
        Initialize the audio processor
        
        Args:
            aggressiveness: VAD aggressiveness level (0-3)
            frame_duration_ms: Frame duration in milliseconds (10, 20, or 30)
        """
        self.vad = webrtcvad.Vad(aggressiveness)
        self.aggressiveness = aggressiveness
        self.frame_duration_ms = frame_duration_ms
        self.supported_rates = [8000, 16000, 32000, 48000]
        self.supported_durations = [10, 20, 30]
        
        if frame_duration_ms not in self.supported_durations:
            raise ValueError(f"Frame duration must be one of {self.supported_durations}ms")
    
    def read_wav_file(self, filepath: str) -> Tuple[np.ndarray, int, int]:
        """
        Read a WAV file and return audio data, sample rate, and channels
        
        Args:
            filepath: Path to the WAV file
            
        Returns:
            Tuple of (audio_data, sample_rate, num_channels)
        """
        try:
            with wave.open(filepath, 'rb') as wf:
                sample_rate = wf.getframerate()
                num_channels = wf.getnchannels()
                sample_width = wf.getsampwidth()
                num_frames = wf.getnframes()
                
                if sample_rate not in self.supported_rates:
                    raise ValueError(f"Unsupported sample rate: {sample_rate}. Must be one of {self.supported_rates}")
                
                if sample_width != 2:
                    raise ValueError(f"Unsupported sample width: {sample_width}. Must be 2 (16-bit)")
                
                if num_channels != 1:
                    raise ValueError(f"Unsupported channel count: {num_channels}. Must be 1 (mono)")
                
                # Read PCM data
                pcm_data = wf.readframes(num_frames)
                audio_data = np.frombuffer(pcm_data, dtype=np.int16)
                
                print(f"✓ Loaded audio file: {filepath}")
                print(f"  Sample rate: {sample_rate} Hz")
                print(f"  Channels: {num_channels}")
                print(f"  Duration: {num_frames / sample_rate:.2f} seconds")
                print(f"  Sample width: {sample_width} bytes")
                
                return audio_data, sample_rate, num_channels
                
        except Exception as e:
            raise Exception(f"Error reading WAV file: {e}")
    
    def frame_generator(self, audio_data: np.ndarray, sample_rate: int) -> Tuple[np.ndarray, float]:
        """
        Generate audio frames from PCM data
        
        Args:
            audio_data: PCM audio data
            sample_rate: Sample rate in Hz
            
        Yields:
            Tuple of (frame_data, timestamp_in_seconds)
        """
        frame_size = int(sample_rate * (self.frame_duration_ms / 1000.0))
        offset = 0
        frame_index = 0
        
        while offset + frame_size <= len(audio_data):
            frame = audio_data[offset:offset + frame_size]
            timestamp = frame_index * (self.frame_duration_ms / 1000.0)
            yield frame, timestamp
            offset += frame_size
            frame_index += 1
    
    def detect_speech_regions(self, audio_data: np.ndarray, sample_rate: int) -> List[Dict[str, Any]]:
        """
        Detect speech regions in audio data
        
        Args:
            audio_data: PCM audio data
            sample_rate: Sample rate in Hz
            
        Returns:
            List of speech region dictionaries with start/end times and confidence
        """
        print(f"\n🔍 Processing audio with VAD (aggressiveness: {self.aggressiveness})...")
        
        speech_regions = []
        current_region = None
        frame_count = 0
        speech_frames = 0
        
        for frame, timestamp in self.frame_generator(audio_data, sample_rate):
            try:
                # Convert to bytes for VAD
                frame_bytes = frame.tobytes()
                is_speech = self.vad.is_speech(frame_bytes, sample_rate)
                
                if is_speech:
                    speech_frames += 1
                    if current_region is None:
                        # Start new speech region
                        current_region = {
                            'start_time': timestamp,
                            'end_time': timestamp + (self.frame_duration_ms / 1000.0),
                            'frame_count': 1
                        }
                    else:
                        # Extend current region
                        current_region['end_time'] = timestamp + (self.frame_duration_ms / 1000.0)
                        current_region['frame_count'] += 1
                else:
                    if current_region is not None:
                        # End current speech region
                        current_region['duration'] = current_region['end_time'] - current_region['start_time']
                        current_region['confidence'] = min(current_region['frame_count'] / 10.0, 1.0)  # Simple confidence metric
                        speech_regions.append(current_region)
                        current_region = None
                
                frame_count += 1
                
            except Exception as e:
                print(f"⚠️  Error processing frame at {timestamp:.2f}s: {e}")
                continue
        
        # Handle case where audio ends during speech
        if current_region is not None:
            current_region['duration'] = current_region['end_time'] - current_region['start_time']
            current_region['confidence'] = min(current_region['frame_count'] / 10.0, 1.0)
            speech_regions.append(current_region)
        
        # Calculate statistics
        total_duration = len(audio_data) / sample_rate
        speech_duration = sum(region['duration'] for region in speech_regions)
        speech_percentage = (speech_duration / total_duration) * 100 if total_duration > 0 else 0
        
        print(f"✓ Processing complete!")
        print(f"  Total frames: {frame_count}")
        print(f"  Speech frames: {speech_frames}")
        print(f"  Speech regions found: {len(speech_regions)}")
        print(f"  Total speech duration: {speech_duration:.2f}s ({speech_percentage:.1f}%)")
        
        return speech_regions
    
    def save_results_to_json(self, speech_regions: List[Dict[str, Any]], 
                           audio_file: str, output_file: str = None) -> str:
        """
        Save speech detection results to JSON file
        
        Args:
            speech_regions: List of speech region dictionaries
            audio_file: Original audio file path
            output_file: Output JSON file path (optional)
            
        Returns:
            Path to the saved JSON file
        """
        if output_file is None:
            base_name = os.path.splitext(os.path.basename(audio_file))[0]
            output_file = f"{base_name}_speech_detection.json"
        
        # Prepare results data
        results = {
            'metadata': {
                'audio_file': os.path.basename(audio_file),
                'processing_timestamp': datetime.now().isoformat(),
                'vad_aggressiveness': self.aggressiveness,
                'frame_duration_ms': self.frame_duration_ms,
                'total_regions': len(speech_regions)
            },
            'speech_regions': speech_regions,
            'summary': {
                'total_speech_duration': sum(region['duration'] for region in speech_regions),
                'average_region_duration': np.mean([region['duration'] for region in speech_regions]) if speech_regions else 0,
                'longest_region_duration': max([region['duration'] for region in speech_regions]) if speech_regions else 0,
                'shortest_region_duration': min([region['duration'] for region in speech_regions]) if speech_regions else 0
            }
        }
        
        # Save to JSON file
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✓ Results saved to: {output_file}")
        return output_file
    
    def visualize_results(self, audio_data: np.ndarray, sample_rate: int, 
                         speech_regions: List[Dict[str, Any]], 
                         output_file: str = None, show_plot: bool = True) -> str:
        """
        Create visualization of speech detection results
        
        Args:
            audio_data: Original audio data
            sample_rate: Sample rate in Hz
            speech_regions: List of speech region dictionaries
            output_file: Output image file path (optional)
            show_plot: Whether to display the plot
            
        Returns:
            Path to the saved image file
        """
        print("\n📊 Creating visualization...")
        
        # Create time axis
        duration = len(audio_data) / sample_rate
        time_axis = np.linspace(0, duration, len(audio_data))
        
        # Normalize audio for visualization
        audio_normalized = audio_data / np.max(np.abs(audio_data))
        
        # Create the plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        
        # Plot 1: Audio waveform with speech regions highlighted
        ax1.plot(time_axis, audio_normalized, 'b-', alpha=0.7, linewidth=0.5)
        ax1.set_title('Audio Waveform with Speech Detection', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Amplitude (normalized)')
        ax1.grid(True, alpha=0.3)
        
        # Highlight speech regions
        for i, region in enumerate(speech_regions):
            start_time = region['start_time']
            end_time = region['end_time']
            confidence = region.get('confidence', 1.0)
            
            # Color based on confidence
            color = plt.cm.RdYlGn(confidence)  # Green for high confidence, red for low
            
            rect = patches.Rectangle((start_time, -1), end_time - start_time, 2, 
                                   alpha=0.3, facecolor=color, edgecolor='red', linewidth=1)
            ax1.add_patch(rect)
            
            # Add region number
            ax1.text(start_time + (end_time - start_time) / 2, 0.8, f'R{i+1}', 
                    ha='center', va='center', fontweight='bold', fontsize=8)
        
        ax1.set_xlim(0, duration)
        ax1.set_ylim(-1.1, 1.1)
        
        # Plot 2: Speech activity timeline
        ax2.set_title('Speech Activity Timeline', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Speech Activity')
        ax2.set_xlabel('Time (seconds)')
        ax2.grid(True, alpha=0.3)
        
        # Create speech activity signal
        speech_activity = np.zeros_like(time_axis)
        for region in speech_regions:
            start_idx = int(region['start_time'] * sample_rate)
            end_idx = int(region['end_time'] * sample_rate)
            start_idx = max(0, min(start_idx, len(speech_activity) - 1))
            end_idx = max(0, min(end_idx, len(speech_activity) - 1))
            speech_activity[start_idx:end_idx] = 1
        
        ax2.fill_between(time_axis, 0, speech_activity, alpha=0.7, color='green', label='Speech')
        ax2.set_ylim(-0.1, 1.1)
        ax2.legend()
        
        # Add statistics text
        total_speech = sum(region['duration'] for region in speech_regions)
        speech_percentage = (total_speech / duration) * 100 if duration > 0 else 0
        
        stats_text = f"""Statistics:
Total Duration: {duration:.2f}s
Speech Duration: {total_speech:.2f}s ({speech_percentage:.1f}%)
Speech Regions: {len(speech_regions)}
VAD Aggressiveness: {self.aggressiveness}"""
        
        ax2.text(0.02, 0.98, stats_text, transform=ax2.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        
        # Save plot
        if output_file is None:
            base_name = os.path.splitext(os.path.basename(audio_data))[0] if hasattr(audio_data, '__len__') else 'speech_detection'
            output_file = f"{base_name}_visualization.png"
        
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Visualization saved to: {output_file}")
        
        if show_plot:
            plt.show()
        else:
            plt.close()
        
        return output_file
    
    def process_audio_file(self, audio_file: str, output_dir: str = None) -> Dict[str, str]:
        """
        Complete audio processing pipeline
        
        Args:
            audio_file: Path to input WAV file
            output_dir: Output directory for results (optional)
            
        Returns:
            Dictionary with paths to output files
        """
        print(f"🎵 Processing audio file: {audio_file}")
        
        # Create output directory
        if output_dir is None:
            output_dir = os.path.dirname(audio_file) or '.'
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Read audio file
        audio_data, sample_rate, num_channels = self.read_wav_file(audio_file)
        
        # Detect speech regions
        speech_regions = self.detect_speech_regions(audio_data, sample_rate)
        
        # Generate output filenames
        base_name = os.path.splitext(os.path.basename(audio_file))[0]
        json_file = os.path.join(output_dir, f"{base_name}_speech_detection.json")
        viz_file = os.path.join(output_dir, f"{base_name}_visualization.png")
        
        # Save results
        self.save_results_to_json(speech_regions, audio_file, json_file)
        self.visualize_results(audio_data, sample_rate, speech_regions, viz_file, show_plot=False)
        
        print(f"\n✅ Processing complete! Results saved to: {output_dir}")
        
        return {
            'json_file': json_file,
            'visualization_file': viz_file,
            'speech_regions_count': len(speech_regions)
        }


def main():
    """Example usage of the AudioProcessor"""
    if len(sys.argv) != 2:
        print("Usage: python audio_processor.py <audio_file.wav>")
        print("Example: python audio_processor.py sample.wav")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    
    if not os.path.exists(audio_file):
        print(f"Error: Audio file '{audio_file}' not found")
        sys.exit(1)
    
    # Create processor with different aggressiveness levels
    for aggressiveness in [0, 1, 2, 3]:
        print(f"\n{'='*60}")
        print(f"Processing with VAD aggressiveness level: {aggressiveness}")
        print(f"{'='*60}")
        
        processor = AudioProcessor(aggressiveness=aggressiveness)
        results = processor.process_audio_file(audio_file)
        
        print(f"Results for aggressiveness {aggressiveness}:")
        print(f"  JSON file: {results['json_file']}")
        print(f"  Visualization: {results['visualization_file']}")
        print(f"  Speech regions: {results['speech_regions_count']}")


if __name__ == "__main__":
    main()