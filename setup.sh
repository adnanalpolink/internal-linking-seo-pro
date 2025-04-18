#!/bin/bash

# Install Python packages
pip install -r requirements.txt

# Download NLTK data
python -m nltk.downloader punkt
python -m nltk.downloader stopwords
python -m nltk.downloader wordnet

# Download spaCy model
python -m spacy download en_core_web_sm

# Create data directory if it doesn't exist
mkdir -p streamlit_app/data
