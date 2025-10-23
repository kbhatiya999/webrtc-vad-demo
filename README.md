# Advanced WebRTC VAD Demo

Comprehensive Voice Activity Detection using WebRTC VAD - Advanced Python demo with audio file processing, real-time monitoring, and visualization.

## Overview

This repository demonstrates advanced usage of **WebRTC Voice Activity Detection (VAD)** in Python for detecting speech in audio streams and files. WebRTC VAD is a lightweight, efficient algorithm used in Google's WebRTC project for real-time communication applications.

## Features

### 🎵 Audio File Processing
- **Frame-by-frame processing** of WAV audio files
- **Speech region detection** with precise timestamps
- **JSON output** with detailed results and statistics
- **Matplotlib visualization** of speech detection results
- **Multiple aggressiveness levels** for different use cases

### 🎤 Real-time Microphone Monitoring
- **Live speech detection** from microphone input
- **Console mode** with real-time status updates
- **Visualization mode** with live plotting
- **Speech region tracking** and statistics
- **Configurable audio parameters**

### 📊 Advanced Visualization
- **Waveform display** with speech regions highlighted
- **Timeline visualization** of speech activity
- **Real-time plots** for live monitoring
- **Statistical analysis** and reporting
- **High-quality image export**

### 🔧 Technical Features
- **Cross-platform compatibility** (Windows, macOS, Linux)
- **Multiple sample rates** (8kHz, 16kHz, 32kHz, 48kHz)
- **Configurable frame durations** (10ms, 20ms, 30ms)
- **Robust error handling** and validation
- **Modular architecture** for easy integration

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager
- Audio input device (for real-time demo)

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install webrtcvad-wheels wave numpy matplotlib scipy pyaudio
```

### System Requirements

- **Audio Processing**: Requires audio input device for real-time features
- **Visualization**: Requires display for matplotlib plots
- **Audio Format**: 16-bit mono PCM WAV files for file processing

## Usage

### Quick Start

```bash
# Run the comprehensive demo
python demo.py

# Show all available options
python demo.py --help
```

### Audio File Processing

```bash
# Process a WAV file with default settings
python demo.py --audio sample.wav

# Process with high aggressiveness (noise filtering)
python demo.py --audio sample.wav --aggressiveness 3

# Create a sample audio file for testing
python demo.py --create-sample
```

### Real-time Microphone Detection

```bash
# Console mode with live status updates
python demo.py --realtime

# Visualization mode with live plotting
python demo.py --realtime --visualization

# High sensitivity for quiet environments
python demo.py --realtime --aggressiveness 0
```

### Advanced Usage

```bash
# Process audio file and show visualization
python audio_processor.py sample.wav

# Run real-time detection with custom settings
python realtime_microphone.py --visualization --aggressiveness 2
```

### VAD Aggressiveness Modes

| Mode | Description | Use Case | Best For |
|------|-------------|----------|----------|
| 0 | Quality mode | High-quality recordings | Studio recordings, clear speech |
| 1 | Low bitrate | General purpose | Balanced detection |
| 2 | Aggressive | Telephony | Phone calls, video calls |
| 3 | Very aggressive | Noisy environments | Background noise, crowds |

## Code Examples

### Basic VAD Usage

```python
import webrtcvad

# Initialize VAD with mode 2 (aggressive)
vad = webrtcvad.Vad(2)

# Check if audio frame contains speech
# frame must be 10, 20, or 30ms of 16-bit PCM audio
is_speech = vad.is_speech(audio_frame, sample_rate)
```

### Advanced Audio Processing

```python
from audio_processor import AudioProcessor

# Create processor with custom settings
processor = AudioProcessor(aggressiveness=2, frame_duration_ms=30)

# Process audio file
results = processor.process_audio_file("sample.wav")

# Access results
print(f"Speech regions found: {results['speech_regions_count']}")
print(f"JSON file: {results['json_file']}")
print(f"Visualization: {results['visualization_file']}")
```

### Real-time Detection

```python
from realtime_microphone import RealtimeSpeechDetector

# Create detector
detector = RealtimeSpeechDetector(aggressiveness=2)

# Run in console mode
detector.run_console_mode()

# Or with visualization
detector.run_visualization_mode()
```

## Technical Requirements

### Audio Format Specifications
- **Format**: 16-bit mono PCM WAV files
- **Sample Rates**: 8000, 16000, 32000, or 48000 Hz
- **Frame Duration**: 10, 20, or 30 milliseconds
- **Channels**: Mono (single channel) only

### Output Formats
- **JSON**: Detailed speech detection results with timestamps
- **PNG**: High-resolution visualization plots
- **Console**: Real-time status updates and statistics

### Performance Notes
- **Real-time processing**: Optimized for live audio streams
- **Memory efficient**: Frame-based processing with minimal memory usage
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Low latency**: Suitable for real-time applications

## File Structure

```
/workspace/
├── demo.py                    # Main demo script with CLI interface
├── audio_processor.py         # Advanced audio file processing
├── realtime_microphone.py     # Real-time microphone detection
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── LICENSE                    # MIT License
```

## Output Files

### Audio Processing Results
- `{filename}_speech_detection.json` - Detailed results with timestamps
- `{filename}_visualization.png` - High-resolution plot of speech regions

### JSON Output Format
```json
{
  "metadata": {
    "audio_file": "sample.wav",
    "processing_timestamp": "2024-01-01T12:00:00",
    "vad_aggressiveness": 2,
    "frame_duration_ms": 30,
    "total_regions": 5
  },
  "speech_regions": [
    {
      "start_time": 0.5,
      "end_time": 2.1,
      "duration": 1.6,
      "confidence": 0.8,
      "frame_count": 53
    }
  ],
  "summary": {
    "total_speech_duration": 8.5,
    "average_region_duration": 1.7,
    "longest_region_duration": 3.2,
    "shortest_region_duration": 0.3
  }
}
```

## Cursor AI Agent Collaboration

This repository is optimized for collaboration with Cursor AI agents. The modular design allows for easy extension:

1. **Audio Processing**: Extend `AudioProcessor` class for custom analysis
2. **Real-time Detection**: Modify `RealtimeSpeechDetector` for specific use cases
3. **Visualization**: Customize matplotlib plots in both modules
4. **Integration**: Use as a library in larger projects

## Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## License

MIT License - see LICENSE file for details

## Resources

- [WebRTC Project](https://webrtc.org/)
- [webrtcvad-wheels PyPI](https://pypi.org/project/webrtcvad-wheels/)
- [Original Google WebRTC VAD](https://chromium.googlesource.com/external/webrtc/+/branch-heads/43/webrtc/common_audio/vad/)

## Advanced Features

### Custom Audio Processing
- **Batch processing**: Process multiple audio files
- **Custom frame sizes**: Adjustable frame durations
- **Multiple aggressiveness**: Compare different VAD settings
- **Export options**: JSON, CSV, or custom formats

### Real-time Applications
- **Voice activity logging**: Track speaking time and patterns
- **Audio quality monitoring**: Detect audio issues in real-time
- **Integration ready**: Easy to embed in larger applications
- **Performance optimized**: Low CPU usage for continuous operation

### Visualization Options
- **Interactive plots**: Zoom, pan, and explore results
- **Export formats**: PNG, PDF, SVG for reports
- **Custom styling**: Modify colors, fonts, and layouts
- **Statistical overlays**: Add confidence intervals and metrics

## Next Steps

After running the demo, consider:

1. **Speech Recognition Integration**: Combine with speech-to-text systems
2. **Audio Analysis**: Add spectral analysis and feature extraction
3. **Machine Learning**: Train custom models on VAD results
4. **Real-time Applications**: Build voice-controlled interfaces
5. **Audio Quality Assessment**: Monitor and improve audio quality
6. **Batch Processing**: Process large audio datasets
7. **API Development**: Create web services for audio analysis

## Troubleshooting

### Common Issues

**Audio device not found:**
- Ensure microphone is connected and working
- Check system audio permissions
- Try different audio devices with `--help`

**Import errors:**
- Install all dependencies: `pip install -r requirements.txt`
- Check Python version (3.7+ required)

**Visualization not showing:**
- Install matplotlib: `pip install matplotlib`
- Check display settings for headless systems

**Audio file format errors:**
- Ensure WAV files are 16-bit mono PCM
- Convert audio files if needed: `ffmpeg -i input.wav -ar 16000 -ac 1 -sample_fmt s16 output.wav`
