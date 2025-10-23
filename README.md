# WebRTC VAD Demo

Real-time Voice Activity Detection using WebRTC VAD - Python demo with audio processing examples.

## Overview

This repository demonstrates how to use **WebRTC Voice Activity Detection (VAD)** in Python for detecting speech in audio streams. WebRTC VAD is a lightweight, efficient algorithm used in Google's WebRTC project for real-time communication applications.

## Features

- Simple demonstration of WebRTC VAD initialization
- Support for 4 aggressiveness modes (0-3)
- Frame-based audio processing
- Cross-platform compatibility
- Easy to integrate into existing projects

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install webrtcvad-wheels wave numpy
```

## Usage

### Run the Simple Demo

```bash
python demo.py
```

This will initialize the VAD with all 4 aggressiveness modes and confirm the library is working.

### VAD Aggressiveness Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| 0 | Least aggressive | High-quality recordings |
| 1 | Low bitrate | General purpose |
| 2 | Aggressive | Telephony |
| 3 | Very aggressive | Noisy environments |

## Code Example

```python
import webrtcvad

# Initialize VAD with mode 2 (aggressive)
vad = webrtcvad.Vad(2)

# Check if audio frame contains speech
# frame must be 10, 20, or 30ms of 16-bit PCM audio
is_speech = vad.is_speech(audio_frame, sample_rate)
```

## Technical Requirements

- **Audio Format**: 16-bit mono PCM
- **Sample Rates**: 8000, 16000, 32000, or 48000 Hz
- **Frame Duration**: 10, 20, or 30 milliseconds

## Cursor AI Agent Collaboration

This repository is optimized for collaboration with Cursor AI agents. To work with Cursor:

1. Clone this repository
2. Open in Cursor editor
3. Use AI agent to:
   - Add audio file processing
   - Implement real-time microphone input
   - Create visualization of speech detection
   - Add more advanced examples

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

## Next Steps

After running the demo, consider:

1. Processing audio files with VAD
2. Building a real-time speech detector
3. Integrating with speech recognition systems
4. Creating voice-controlled applications
