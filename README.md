# Smart Meeting Minutes Generator with Action Tracker

A comprehensive local web application that automatically generates structured meeting minutes from audio/video recordings using AI-powered speech recognition, speaker diarization, and natural language processing.

## Features

### Core Functionality
- **Speech-to-Text**: Uses OpenAI Whisper for accurate transcription
- **Speaker Diarization**: Identifies and separates different speakers using pyannote.audio
- **Text Preprocessing**: Removes filler words, expands contractions, standardizes dates
- **Smart Summarization**: Generates structured summaries using flan-t5-small model

### Meeting Analysis
- **Agenda Items**: Automatically extracts main topics discussed
- **Decisions Made**: Identifies key decisions and resolutions
- **Risk Assessment**: Highlights potential risks and concerns mentioned
- **Next Steps**: Captures follow-up actions and future plans

### Action Item Management
- **Automatic Detection**: Uses ML to identify action items from conversation
- **Assignee Extraction**: Maps action items to specific people using NER
- **Deadline Parsing**: Extracts and standardizes deadline information
- **Progress Tracking**: Maintains database of open/completed actions across meetings

### Export and Reporting
- **PDF Reports**: Professional formatted meeting minutes
- **JSON Export**: Structured data for integration with other tools
- **Action Dashboard**: Real-time view of all action items and their status

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLite**: Local database for action tracking
- **OpenAI Whisper**: Speech-to-text conversion
- **pyannote.audio**: Speaker diarization
- **HuggingFace Transformers**: Text summarization and NLP

### Frontend
- **HTML5 + TailwindCSS**: Responsive, modern UI
- **Alpine.js**: Lightweight JavaScript framework
- **Drag & Drop**: Intuitive file upload interface

### Machine Learning Models
- **Whisper (base)**: Speech recognition
- **flan-t5-small**: Text summarization
- **all-MiniLM-L6-v2**: Sentence embeddings for action detection
- **dslim/bert-base-NER**: Named entity recognition
- **pyannote/speaker-diarization-3.1**: Speaker identification

## Quick Start

### 1. Prerequisites
- Python 3.8+
- 4GB RAM (8GB recommended)
- HuggingFace account (free) for speaker diarization

### 2. Installation
\`\`\`bash
# Clone or extract project
cd mom-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Set up environment variables
echo "HUGGINGFACE_TOKEN=your_token_here" > .env

# Initialize database
python scripts/run_database_setup.py
\`\`\`

### 3. Run Application
\`\`\`bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
\`\`\`

### 4. Access Interface
Open http://127.0.0.1:8000 in your web browser

## Supported File Formats

- **Audio**: MP3, WAV, M4A
- **Video**: MP4, AVI, MOV (audio will be extracted)
- **Size Limit**: 500MB per file
- **Duration**: Optimized for meetings up to 2 hours

## Privacy and Security

- **100% Local Processing**: No data sent to external servers
- **Open Source Models**: All AI models run locally
- **Local Storage**: SQLite database stored on your machine
- **No Cloud Dependencies**: Works completely offline after initial setup

## Use Cases

### Business Meetings
- Team standups and retrospectives
- Client calls and project reviews
- Board meetings and strategic sessions
- Training sessions and workshops

### Academic Settings
- Research meetings and seminars
- Student group discussions
- Faculty meetings
- Thesis defense sessions

### Personal Projects
- Podcast planning sessions
- Interview recordings
- Creative brainstorming sessions
- Project planning meetings

## Architecture Overview

\`\`\`
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │    FastAPI       │    │   ML Pipeline   │
│   (HTML/JS)     │◄──►│    Backend       │◄──►│   (Whisper,     │
│                 │    │                  │    │    pyannote,    │
└─────────────────┘    └──────────────────┘    │    flan-t5)     │
                                │               └─────────────────┘
                                ▼
                       ┌──────────────────┐
                       │   SQLite DB      │
                       │   (Actions,      │
                       │    Meetings)     │
                       └──────────────────┘
\`\`\`

## Performance Considerations

### Hardware Requirements
- **Minimum**: 4GB RAM, 2GB storage
- **Recommended**: 8GB RAM, 4GB storage, SSD
- **GPU**: Optional, will accelerate processing if CUDA available

### Processing Times (approximate)
- **10-minute meeting**: 2-3 minutes processing
- **30-minute meeting**: 5-8 minutes processing  
- **60-minute meeting**: 10-15 minutes processing

### Optimization Tips
- Use MP3 format for faster processing
- Ensure good audio quality for better accuracy
- Close other applications during processing
- Use shorter segments for very long meetings

## Troubleshooting

### Common Issues

**"spaCy model not found"**
\`\`\`bash
python -m spacy download en_core_web_sm
\`\`\`

**"Could not load diarization pipeline"**
- Set HUGGINGFACE_TOKEN environment variable
- Accept model license at HuggingFace

**Memory errors**
- Use smaller files or increase system RAM
- Close other applications during processing

**Poor transcription quality**
- Ensure clear audio with minimal background noise
- Use external microphone for better quality
- Consider audio preprocessing tools

## Contributing

This is a local application designed for personal/organizational use. Key areas for enhancement:

- Additional language support
- Integration with calendar systems
- Advanced action item categorization
- Custom model fine-tuning
- Mobile app companion

## License

This project uses various open-source libraries and models. Please review individual component licenses:

- OpenAI Whisper: MIT License
- HuggingFace Transformers: Apache 2.0
- FastAPI: MIT License
- pyannote.audio: MIT License

## Acknowledgments

- OpenAI for Whisper speech recognition
- HuggingFace for transformer models and hosting
- pyannote team for speaker diarization
- FastAPI team for the excellent web framework
- The open-source ML community for making this possible

---

**Note**: This application is designed to run entirely on your local machine for privacy and security. No meeting data is transmitted to external servers.
