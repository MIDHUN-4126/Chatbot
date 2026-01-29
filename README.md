# Government Website Navigation Chatbot

A fully functional, private chatbot system for navigating complex Indian government websites with Tamil language support. Built without external LLM APIs for complete data privacy.

## Features

- **100% Private**: No external API calls, all processing happens locally
- **Tamil Language Support**: Natural language processing for Tamil and English
- **Government Website Navigation**: Specialized for Indian government portals
- **Smart Search**: Intent recognition and context-aware responses
- **Knowledge Base**: Vector-based document retrieval
- **Web Interface**: User-friendly chat interface

## Architecture

```
├── data_collection/     # Web scraping modules for government websites
├── nlp_engine/          # Local NLP processing (Tamil + English)
├── knowledge_base/      # Vector store and document management
├── chatbot_engine/      # Intent recognition and response generation
├── web_interface/       # Flask-based chat UI
├── data/                # Scraped data and processed documents
└── models/              # Local ML models and embeddings
```

## Technology Stack

- **NLP**: spaCy, Transformers (local models)
- **Tamil Support**: Indic NLP, Tamil BERT
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **Web Framework**: Flask
- **Data Collection**: BeautifulSoup4, Scrapy
- **Database**: SQLite for metadata

## Installation

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Download models
python setup_models.py
```

## Usage

1. **Collect Data**: Scrape government websites
```bash
python data_collection/scraper.py --config config/websites.json
```

2. **Build Knowledge Base**: Process and index documents
```bash
python knowledge_base/build_index.py
```

3. **Run Chatbot**:
```bash
python app.py
```

Visit `http://localhost:5000` for the web interface.

## Configuration

Edit `config/config.yaml` to:
- Add government website URLs
- Configure Tamil/English language preferences
- Adjust NLP models
- Set scraping parameters

## Privacy & Security

- All data stored locally
- No external API calls
- No data sharing
- Encrypted local storage option available

## Supported Government Portals

- Tamil Nadu Government Portal
- India.gov.in
- Digital India
- UMANG Services
- State-specific services

## License

Private Use - All Rights Reserved
