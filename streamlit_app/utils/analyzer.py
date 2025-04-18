import re
import string
import pandas as pd
import numpy as np
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Download NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

class ContentAnalyzer:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.pages_df = None
        self.links_df = None
        self.tfidf_matrix = None
        self.tfidf_vectorizer = None
        self.similarity_matrix = None
    
    def preprocess_text(self, text):
        """Preprocess text for analysis"""
        if not text or not isinstance(text, str):
            return ""
            
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        
        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token not in self.stop_words and len(token) > 2]
        
        return ' '.join(tokens)
    
    def extract_keywords(self, text, n=10):
        """Extract top keywords from text"""
        if not text or not isinstance(text, str):
            return []
            
        # Preprocess text
        processed_text = self.preprocess_text(text)
        
        # Tokenize
        tokens = word_tokenize(processed_text)
        
        # Count word frequencies
        word_freq = Counter(tokens)
        
        # Get top n keywords
        keywords = [word for word, freq in word_freq.most_common(n)]
        
        return keywords
    
    def extract_ngrams(self, text, n=2, top_n=10):
        """Extract top n-grams from text"""
        if not text or not isinstance(text, str):
            return []
            
        # Preprocess text
        processed_text = self.preprocess_text(text)
        
        # Tokenize
        tokens = word_tokenize(processed_text)
        
        # Generate n-grams
        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngrams.append(' '.join(tokens[i:i+n]))
        
        # Count n-gram frequencies
        ngram_freq = Counter(ngrams)
        
        # Get top n n-grams
        top_ngrams = [ngram for ngram, freq in ngram_freq.most_common(top_n)]
        
        return top_ngrams
    
    def analyze_pages(self, pages, links_df=None):
        """Analyze pages and extract topics"""
        if not pages:
            return pd.DataFrame()
        
        # Convert to DataFrame if it's a list
        if isinstance(pages, list):
            pages_df = pd.DataFrame(pages)
        else:
            pages_df = pages.copy()
        
        # Store the links DataFrame
        self.links_df = links_df
        
        # Preprocess content
        pages_df['processed_content'] = pages_df['content'].apply(self.preprocess_text)
        
        # Extract keywords
        pages_df['keywords'] = pages_df['content'].apply(lambda x: self.extract_keywords(x, n=10))
        
        # Extract bigrams
        pages_df['bigrams'] = pages_df['content'].apply(lambda x: self.extract_ngrams(x, n=2, top_n=5))
        
        # Calculate TF-IDF
        self.tfidf_vectorizer = TfidfVectorizer(max_features=1000)
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(pages_df['processed_content'])
        
        # Calculate similarity matrix
        self.similarity_matrix = cosine_similarity(self.tfidf_matrix)
        
        # Store the processed DataFrame
        self.pages_df = pages_df
        
        return pages_df
    
    def get_similar_pages(self, page_url, top_n=5):
        """Get pages similar to the given page"""
        if self.pages_df is None or self.similarity_matrix is None:
            return []
        
        # Find the index of the page
        try:
            page_idx = self.pages_df[self.pages_df['url'] == page_url].index[0]
        except (IndexError, KeyError):
            logger.warning(f"Page not found: {page_url}")
            return []
        
        # Get similarity scores
        similarity_scores = list(enumerate(self.similarity_matrix[page_idx]))
        
        # Sort by similarity score
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        
        # Get top N similar pages (excluding the page itself)
        similar_pages = []
        for idx, score in similarity_scores[1:top_n+1]:
            similar_pages.append({
                'url': self.pages_df.iloc[idx]['url'],
                'title': self.pages_df.iloc[idx]['title'],
                'similarity_score': score,
                'keywords': self.pages_df.iloc[idx]['keywords']
            })
        
        return similar_pages
    
    def get_orphaned_pages(self, min_incoming_links=3):
        """Get pages with fewer than min_incoming_links incoming links"""
        if self.pages_df is None or self.links_df is None:
            return []
        
        # Count incoming links for each page
        incoming_links = self.links_df['target_url'].value_counts().reset_index()
        incoming_links.columns = ['url', 'incoming_links']
        
        # Merge with pages DataFrame
        pages_with_links = pd.merge(self.pages_df, incoming_links, on='url', how='left')
        
        # Fill NaN values with 0
        pages_with_links['incoming_links'] = pages_with_links['incoming_links'].fillna(0)
        
        # Get orphaned pages
        orphaned_pages = pages_with_links[pages_with_links['incoming_links'] < min_incoming_links]
        
        return orphaned_pages
    
    def get_link_suggestions(self, page_url, top_n=5):
        """Get link suggestions for the given page"""
        if self.pages_df is None or self.similarity_matrix is None:
            return []
        
        # Find the index of the page
        try:
            page_idx = self.pages_df[self.pages_df['url'] == page_url].index[0]
        except (IndexError, KeyError):
            logger.warning(f"Page not found: {page_url}")
            return []
        
        # Get the page content
        page_content = self.pages_df.iloc[page_idx]['content']
        page_keywords = self.pages_df.iloc[page_idx]['keywords']
        
        # Get similar pages
        similar_pages = self.get_similar_pages(page_url, top_n=top_n*2)
        
        # Get existing outgoing links
        if self.links_df is not None:
            existing_links = self.links_df[self.links_df['source_url'] == page_url]['target_url'].tolist()
        else:
            existing_links = []
        
        # Filter out pages that are already linked
        similar_pages = [page for page in similar_pages if page['url'] not in existing_links]
        
        # Generate link suggestions
        suggestions = []
        for page in similar_pages[:top_n]:
            # Find matching keywords
            target_keywords = page['keywords']
            matching_keywords = list(set(page_keywords) & set(target_keywords))
            
            # If no matching keywords, use the top keyword from the target page
            if not matching_keywords and target_keywords:
                matching_keywords = [target_keywords[0]]
            
            # Create suggestion
            if matching_keywords:
                suggestions.append({
                    'source_url': page_url,
                    'target_url': page['url'],
                    'target_title': page['title'],
                    'similarity_score': page['similarity_score'],
                    'suggested_anchor': matching_keywords[0].title(),
                    'matching_keywords': matching_keywords
                })
        
        return suggestions
    
    def identify_topic_clusters(self, min_similarity=0.3):
        """Identify topic clusters based on content similarity"""
        if self.pages_df is None or self.similarity_matrix is None:
            return []
        
        # Create clusters
        clusters = []
        processed_indices = set()
        
        for i in range(len(self.pages_df)):
            if i in processed_indices:
                continue
            
            # Find similar pages
            similar_indices = [j for j in range(len(self.pages_df)) 
                              if self.similarity_matrix[i, j] >= min_similarity and i != j]
            
            # If there are similar pages, create a cluster
            if similar_indices:
                cluster = {
                    'pillar_page': {
                        'url': self.pages_df.iloc[i]['url'],
                        'title': self.pages_df.iloc[i]['title'],
                        'keywords': self.pages_df.iloc[i]['keywords']
                    },
                    'cluster_pages': []
                }
                
                for j in similar_indices:
                    cluster['cluster_pages'].append({
                        'url': self.pages_df.iloc[j]['url'],
                        'title': self.pages_df.iloc[j]['title'],
                        'similarity_score': self.similarity_matrix[i, j],
                        'keywords': self.pages_df.iloc[j]['keywords']
                    })
                
                clusters.append(cluster)
                processed_indices.update(similar_indices)
                processed_indices.add(i)
        
        return clusters
    
    def simulate_analysis(self, pages_df, links_df):
        """Simulate content analysis for testing purposes"""
        # Create a copy of the DataFrames
        pages = pages_df.copy()
        
        # Add simulated analysis results
        pages['processed_content'] = pages['content'].apply(lambda x: x[:100] + "...")
        
        # Generate random keywords
        all_keywords = ['seo', 'content', 'marketing', 'internal', 'linking', 'optimization', 
                       'strategy', 'analysis', 'website', 'traffic', 'ranking', 'search', 
                       'engine', 'google', 'backlinks', 'authority', 'relevance', 'structure']
        
        pages['keywords'] = pages.apply(lambda x: 
            np.random.choice(all_keywords, size=min(10, len(all_keywords)), replace=False).tolist(), 
            axis=1)
        
        # Generate random bigrams
        all_bigrams = ['internal linking', 'content strategy', 'seo optimization', 
                      'link building', 'search engine', 'keyword research', 
                      'site structure', 'page authority', 'user experience']
        
        pages['bigrams'] = pages.apply(lambda x: 
            np.random.choice(all_bigrams, size=min(5, len(all_bigrams)), replace=False).tolist(), 
            axis=1)
        
        # Store the processed DataFrames
        self.pages_df = pages
        self.links_df = links_df
        
        # Create a dummy similarity matrix
        n = len(pages)
        self.similarity_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    self.similarity_matrix[i, j] = 1.0
                else:
                    # Random similarity between 0.1 and 0.9
                    self.similarity_matrix[i, j] = 0.1 + 0.8 * np.random.random()
        
        return pages
