# Copycat

A web application that analyzes and compares two Carnatic music audio files to determine their similarity based on various musical aspects like swara patterns, pitch contours, and note distributions.

## Features

- Upload and compare two Carnatic music audio files
- Analyzes multiple aspects of similarity:
  - Overall musical similarity
  - Pattern similarity
  - Swara (note) similarity
- Generates detailed visualizations:
  - Note distribution comparison
  - Pitch contour comparison
  - Note-by-note similarity analysis
- Maintains a log of all comparisons
- Automatic cleanup of uploaded files for privacy

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/carnatic-music-analyzer.git
cd carnatic-music-analyzer
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:8080
```

3. Upload two Carnatic music audio files (.wav format recommended)
4. View the analysis results including:
   - Similarity scores
   - Visual comparisons
   - Note distribution graphs

## Technical Details

The analyzer uses several advanced techniques for music analysis:

- Pitch tracking using librosa's piptrack algorithm
- Note detection and conversion from frequency to musical notation
- Pattern matching using cosine similarity
- Swara analysis considering both frequency proximity and note distribution
- Custom visualization using matplotlib

## Project Structure

```
carnatic-music-analyzer/
├── app.py                     # Main Flask application
├── enhanced_carnatic_analyzer.py  # Core analysis logic
├── requirements.txt           # Python dependencies
├── static/
│   └── uploads/              # Temporary storage for visualizations
├── uploads/                  # Temporary storage for audio files
└── templates/
    ├── index.html           # Upload page
    ├── results.html         # Analysis results page
    └── logs.html            # Historical comparisons page
```

## Dependencies

Major dependencies include:
- Flask
- librosa
- numpy
- matplotlib
- scikit-learn
- scipy

See `requirements.txt` for a complete list.

## Server Deployment

When deploying to a server:

1. Ensure proper file permissions:
```bash
chmod 777 uploads
chmod 777 static/uploads
```

2. Configure your web server (e.g., nginx) to handle the static files

3. Set up proper security measures as this is handling file uploads

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Acknowledgments

- Built using librosa for audio analysis
- Inspired by Carnatic music theory and pattern recognition techniques
- Thanks to the Flask community for the web framework

## Contact

Your Name - [hrithicksundar@gmail.com](mailto:hrithicksundar@gmail.com)

Project Link: [https://github.com/Hrithick123/carnatic-music-analyzer](https://github.com/Hrithick123/carnatic-music-analyzer)
