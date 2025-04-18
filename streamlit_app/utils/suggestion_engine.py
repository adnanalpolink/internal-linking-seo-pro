import pandas as pd
import numpy as np
import re
from collections import defaultdict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SuggestionEngine:
    def __init__(self, content_analyzer=None):
        self.content_analyzer = content_analyzer
        self.pages_df = None
        self.links_df = None
        self.orphaned_pages = None
        self.topic_clusters = None
    
    def set_data(self, pages_df, links_df):
        """Set the data for the suggestion engine"""
        self.pages_df = pages_df
        self.links_df = links_df
    
    def find_link_opportunities(self, min_incoming_links=3):
        """Find link opportunities for orphaned pages"""
        if self.pages_df is None or self.links_df is None or self.content_analyzer is None:
            return []
        
        # Get orphaned pages
        self.orphaned_pages = self.content_analyzer.get_orphaned_pages(min_incoming_links)
        
        # Generate link opportunities
        opportunities = []
        
        for _, orphaned_page in self.orphaned_pages.iterrows():
            # Get similar pages that could link to this orphaned page
            similar_pages = self.content_analyzer.get_similar_pages(orphaned_page['url'])
            
            # Get existing incoming links
            existing_sources = self.links_df[self.links_df['target_url'] == orphaned_page['url']]['source_url'].tolist()
            
            # Filter out pages that already link to this orphaned page
            similar_pages = [page for page in similar_pages if page['url'] not in existing_sources]
            
            # Add to opportunities
            for page in similar_pages:
                # Find matching keywords
                orphaned_keywords = orphaned_page['keywords']
                page_keywords = page['keywords']
                matching_keywords = list(set(orphaned_keywords) & set(page_keywords))
                
                # If no matching keywords, use the top keyword from the orphaned page
                if not matching_keywords and orphaned_keywords:
                    matching_keywords = [orphaned_keywords[0]]
                
                # Create opportunity
                if matching_keywords:
                    opportunities.append({
                        'orphaned_url': orphaned_page['url'],
                        'orphaned_title': orphaned_page['title'],
                        'source_url': page['url'],
                        'source_title': page['title'],
                        'similarity_score': page['similarity_score'],
                        'suggested_anchor': matching_keywords[0].title(),
                        'matching_keywords': matching_keywords
                    })
        
        return opportunities
    
    def find_topic_cluster_opportunities(self):
        """Find link opportunities within topic clusters"""
        if self.pages_df is None or self.links_df is None or self.content_analyzer is None:
            return []
        
        # Identify topic clusters
        self.topic_clusters = self.content_analyzer.identify_topic_clusters()
        
        # Generate link opportunities within clusters
        opportunities = []
        
        for cluster in self.topic_clusters:
            pillar_page = cluster['pillar_page']
            cluster_pages = cluster['cluster_pages']
            
            # Check links from cluster pages to pillar page
            for page in cluster_pages:
                # Check if this page links to the pillar page
                links_to_pillar = self.links_df[
                    (self.links_df['source_url'] == page['url']) & 
                    (self.links_df['target_url'] == pillar_page['url'])
                ]
                
                if len(links_to_pillar) == 0:
                    # Find matching keywords
                    pillar_keywords = pillar_page['keywords']
                    page_keywords = page['keywords']
                    matching_keywords = list(set(pillar_keywords) & set(page_keywords))
                    
                    # If no matching keywords, use the top keyword from the pillar page
                    if not matching_keywords and pillar_keywords:
                        matching_keywords = [pillar_keywords[0]]
                    
                    # Create opportunity
                    if matching_keywords:
                        opportunities.append({
                            'cluster_type': 'to_pillar',
                            'source_url': page['url'],
                            'source_title': page['title'],
                            'target_url': pillar_page['url'],
                            'target_title': pillar_page['title'],
                            'similarity_score': page['similarity_score'],
                            'suggested_anchor': matching_keywords[0].title(),
                            'matching_keywords': matching_keywords
                        })
            
            # Check links from pillar page to cluster pages
            for page in cluster_pages:
                # Check if the pillar page links to this page
                links_from_pillar = self.links_df[
                    (self.links_df['source_url'] == pillar_page['url']) & 
                    (self.links_df['target_url'] == page['url'])
                ]
                
                if len(links_from_pillar) == 0:
                    # Find matching keywords
                    pillar_keywords = pillar_page['keywords']
                    page_keywords = page['keywords']
                    matching_keywords = list(set(pillar_keywords) & set(page_keywords))
                    
                    # If no matching keywords, use the top keyword from the cluster page
                    if not matching_keywords and page_keywords:
                        matching_keywords = [page_keywords[0]]
                    
                    # Create opportunity
                    if matching_keywords:
                        opportunities.append({
                            'cluster_type': 'from_pillar',
                            'source_url': pillar_page['url'],
                            'source_title': pillar_page['title'],
                            'target_url': page['url'],
                            'target_title': page['title'],
                            'similarity_score': page['similarity_score'],
                            'suggested_anchor': matching_keywords[0].title(),
                            'matching_keywords': matching_keywords
                        })
        
        return opportunities
    
    def get_contextual_link_suggestions(self, page_url, content=None):
        """Get contextual link suggestions for the given page content"""
        if self.pages_df is None or self.content_analyzer is None:
            return []
        
        # Get the page content if not provided
        if content is None:
            try:
                page_row = self.pages_df[self.pages_df['url'] == page_url].iloc[0]
                content = page_row['content']
            except (IndexError, KeyError):
                logger.warning(f"Page not found: {page_url}")
                return []
        
        # Get link suggestions
        suggestions = self.content_analyzer.get_link_suggestions(page_url)
        
        # Find contexts for each suggestion
        contextual_suggestions = []
        
        for suggestion in suggestions:
            anchor = suggestion['suggested_anchor'].lower()
            
            # Find occurrences of the anchor in the content
            matches = list(re.finditer(r'\b' + re.escape(anchor) + r'\b', content.lower()))
            
            if matches:
                # Get context around the first match
                match = matches[0]
                start = max(0, match.start() - 50)
                end = min(len(content), match.end() + 50)
                
                # Extract context
                context = content[start:end]
                
                # Highlight the anchor
                anchor_start = match.start() - start
                anchor_end = match.end() - start
                highlighted_context = context[:anchor_start] + "**" + context[anchor_start:anchor_end] + "**" + context[anchor_end:]
                
                # Add to contextual suggestions
                contextual_suggestions.append({
                    **suggestion,
                    'context': highlighted_context,
                    'context_position': match.start(),
                    'occurrences': len(matches)
                })
            else:
                # If no exact match, look for partial matches
                for keyword in suggestion['matching_keywords']:
                    matches = list(re.finditer(r'\b' + re.escape(keyword.lower()) + r'\b', content.lower()))
                    
                    if matches:
                        # Get context around the first match
                        match = matches[0]
                        start = max(0, match.start() - 50)
                        end = min(len(content), match.end() + 50)
                        
                        # Extract context
                        context = content[start:end]
                        
                        # Highlight the keyword
                        keyword_start = match.start() - start
                        keyword_end = match.end() - start
                        highlighted_context = context[:keyword_start] + "**" + context[keyword_start:keyword_end] + "**" + context[keyword_end:]
                        
                        # Add to contextual suggestions
                        contextual_suggestions.append({
                            **suggestion,
                            'suggested_anchor': keyword.title(),  # Update suggested anchor
                            'context': highlighted_context,
                            'context_position': match.start(),
                            'occurrences': len(matches)
                        })
                        
                        break
        
        # Sort by context position
        contextual_suggestions.sort(key=lambda x: x['context_position'])
        
        return contextual_suggestions
    
    def get_site_stats(self):
        """Get site statistics"""
        if self.pages_df is None or self.links_df is None:
            return {
                'pages_indexed': 0,
                'orphaned_pages': 0,
                'internal_links': 0,
                'topic_clusters': 0
            }
        
        # Count orphaned pages if not already calculated
        if self.orphaned_pages is None and self.content_analyzer is not None:
            self.orphaned_pages = self.content_analyzer.get_orphaned_pages()
        
        # Count topic clusters if not already calculated
        if self.topic_clusters is None and self.content_analyzer is not None:
            self.topic_clusters = self.content_analyzer.identify_topic_clusters()
        
        # Calculate statistics
        stats = {
            'pages_indexed': len(self.pages_df),
            'orphaned_pages': len(self.orphaned_pages) if self.orphaned_pages is not None else 0,
            'internal_links': len(self.links_df),
            'topic_clusters': len(self.topic_clusters) if self.topic_clusters is not None else 0
        }
        
        return stats
    
    def simulate_suggestions(self, pages_df, links_df):
        """Simulate link suggestions for testing purposes"""
        # Set the data
        self.pages_df = pages_df
        self.links_df = links_df
        
        # Simulate orphaned pages (about 20% of pages)
        n_orphaned = max(1, int(len(pages_df) * 0.2))
        orphaned_indices = np.random.choice(len(pages_df), size=n_orphaned, replace=False)
        self.orphaned_pages = pages_df.iloc[orphaned_indices]
        
        # Simulate topic clusters (about 3-5 clusters)
        n_clusters = min(5, max(3, int(len(pages_df) / 10)))
        self.topic_clusters = []
        
        for i in range(n_clusters):
            # Select a random pillar page
            pillar_idx = np.random.choice(len(pages_df))
            pillar_page = {
                'url': pages_df.iloc[pillar_idx]['url'],
                'title': pages_df.iloc[pillar_idx]['title'],
                'keywords': ['keyword1', 'keyword2', 'keyword3']
            }
            
            # Select 3-7 random cluster pages
            n_cluster_pages = np.random.randint(3, 8)
            cluster_indices = np.random.choice(
                [j for j in range(len(pages_df)) if j != pillar_idx], 
                size=min(n_cluster_pages, len(pages_df) - 1), 
                replace=False
            )
            
            cluster_pages = []
            for idx in cluster_indices:
                cluster_pages.append({
                    'url': pages_df.iloc[idx]['url'],
                    'title': pages_df.iloc[idx]['title'],
                    'similarity_score': 0.5 + 0.5 * np.random.random(),
                    'keywords': ['keyword1', 'keyword4', 'keyword5']
                })
            
            self.topic_clusters.append({
                'pillar_page': pillar_page,
                'cluster_pages': cluster_pages
            })
        
        # Generate simulated link opportunities
        orphaned_opportunities = []
        
        for _, orphaned_page in self.orphaned_pages.iterrows():
            # Generate 2-4 opportunities per orphaned page
            n_opportunities = np.random.randint(2, 5)
            
            for _ in range(n_opportunities):
                # Select a random source page
                source_idx = np.random.choice(len(pages_df))
                source_page = pages_df.iloc[source_idx]
                
                # Create opportunity
                orphaned_opportunities.append({
                    'orphaned_url': orphaned_page['url'],
                    'orphaned_title': orphaned_page['title'],
                    'source_url': source_page['url'],
                    'source_title': source_page['title'],
                    'similarity_score': 0.5 + 0.5 * np.random.random(),
                    'suggested_anchor': 'Anchor Text',
                    'matching_keywords': ['keyword1', 'keyword2']
                })
        
        # Generate simulated cluster opportunities
        cluster_opportunities = []
        
        for cluster in self.topic_clusters:
            pillar_page = cluster['pillar_page']
            
            for page in cluster['cluster_pages']:
                # 50% chance of needing a link to pillar
                if np.random.random() < 0.5:
                    cluster_opportunities.append({
                        'cluster_type': 'to_pillar',
                        'source_url': page['url'],
                        'source_title': page['title'],
                        'target_url': pillar_page['url'],
                        'target_title': pillar_page['title'],
                        'similarity_score': page['similarity_score'],
                        'suggested_anchor': 'Pillar Topic',
                        'matching_keywords': ['keyword1', 'keyword2']
                    })
                
                # 50% chance of needing a link from pillar
                if np.random.random() < 0.5:
                    cluster_opportunities.append({
                        'cluster_type': 'from_pillar',
                        'source_url': pillar_page['url'],
                        'source_title': pillar_page['title'],
                        'target_url': page['url'],
                        'target_title': page['title'],
                        'similarity_score': page['similarity_score'],
                        'suggested_anchor': 'Subtopic',
                        'matching_keywords': ['keyword4', 'keyword5']
                    })
        
        return {
            'orphaned_opportunities': orphaned_opportunities,
            'cluster_opportunities': cluster_opportunities
        }
