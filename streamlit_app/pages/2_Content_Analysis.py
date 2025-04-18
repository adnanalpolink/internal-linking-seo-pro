import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
import sys
from datetime import datetime
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import networkx as nx

# Add the parent directory to the path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.analyzer import ContentAnalyzer

# Set page configuration
st.set_page_config(
    page_title="Content Analysis - Internal Linking SEO Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        color: #4285f4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #5f6368;
        margin-bottom: 1rem;
    }
    .card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
        margin-bottom: 1rem;
    }
    .keyword-tag {
        display: inline-block;
        background-color: #e8f0fe;
        color: #1a73e8;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        font-size: 0.875rem;
    }
    .similarity-score {
        display: inline-block;
        background-color: #e6f4ea;
        color: #137333;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = ContentAnalyzer()

if 'pages_df' not in st.session_state:
    st.session_state.pages_df = None

if 'links_df' not in st.session_state:
    st.session_state.links_df = None

# Data paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
PAGES_DATA_PATH = os.path.join(DATA_DIR, "pages_data.csv")
LINKS_DATA_PATH = os.path.join(DATA_DIR, "links_data.csv")

# Load data if available
def load_data():
    if os.path.exists(PAGES_DATA_PATH) and os.path.exists(LINKS_DATA_PATH):
        pages_df = pd.read_csv(PAGES_DATA_PATH)
        links_df = pd.read_csv(LINKS_DATA_PATH)
        return pages_df, links_df
    return None, None

# Load data if not already in session state
if st.session_state.pages_df is None or st.session_state.links_df is None:
    pages_df, links_df = load_data()
    if pages_df is not None and links_df is not None:
        st.session_state.pages_df = pages_df
        st.session_state.links_df = links_df
        
        # Simulate content analysis
        st.session_state.analyzer.simulate_analysis(pages_df, links_df)

# Main header
st.markdown('<h1 class="main-header">Content Analysis</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Analyze your website content to identify topics and relationships</p>', unsafe_allow_html=True)

# Check if data is available
if st.session_state.pages_df is None or st.session_state.links_df is None:
    st.warning("No data available. Please crawl your website first.")
    if st.button("Go to Site Crawler"):
        st.switch_page("pages/1_Site_Crawler.py")
else:
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Page Analysis", "Topic Analysis", "Content Relationships"])
    
    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Page Content Analysis")
        
        # Page selector
        selected_page = st.selectbox(
            "Select a page to analyze:",
            options=st.session_state.pages_df['url'].tolist(),
            format_func=lambda x: st.session_state.pages_df[st.session_state.pages_df['url'] == x]['title'].iloc[0] if len(st.session_state.pages_df[st.session_state.pages_df['url'] == x]) > 0 else x
        )
        
        # Get page data
        page_data = st.session_state.pages_df[st.session_state.pages_df['url'] == selected_page].iloc[0]
        
        # Display page info
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(page_data['title'])
            st.write(f"**URL:** {page_data['url']}")
            
            # Display content preview
            st.write("**Content Preview:**")
            st.write(page_data['content'][:500] + "..." if len(page_data['content']) > 500 else page_data['content'])
        
        with col2:
            # Display page metrics
            st.write("**Page Metrics:**")
            
            # Get incoming links
            incoming_links = st.session_state.links_df[st.session_state.links_df['target_url'] == selected_page]
            
            # Get outgoing links
            outgoing_links = st.session_state.links_df[st.session_state.links_df['source_url'] == selected_page]
            
            metrics_df = pd.DataFrame({
                'Metric': ['Crawl Depth', 'Incoming Links', 'Outgoing Links', 'Content Length'],
                'Value': [
                    page_data['depth'],
                    len(incoming_links),
                    len(outgoing_links),
                    len(page_data['content'])
                ]
            })
            
            st.dataframe(metrics_df, use_container_width=True, hide_index=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Keywords and topics
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Keywords and Topics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Display keywords
            st.write("**Top Keywords:**")
            
            keywords_html = ""
            for keyword in page_data['keywords']:
                keywords_html += f'<span class="keyword-tag">{keyword}</span>'
            
            st.markdown(keywords_html, unsafe_allow_html=True)
            
            # Display bigrams
            st.write("**Top Phrases:**")
            
            bigrams_html = ""
            for bigram in page_data['bigrams']:
                bigrams_html += f'<span class="keyword-tag">{bigram}</span>'
            
            st.markdown(bigrams_html, unsafe_allow_html=True)
        
        with col2:
            # Create word cloud
            if len(page_data['keywords']) > 0:
                # Create a dictionary of word frequencies
                word_freq = {word: 10 + i for i, word in enumerate(reversed(page_data['keywords']))}
                
                # Generate word cloud
                wordcloud = WordCloud(
                    width=400,
                    height=200,
                    background_color='white',
                    colormap='Blues',
                    max_words=50
                ).generate_from_frequencies(word_freq)
                
                # Display word cloud
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Similar pages
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Similar Pages")
        
        # Get similar pages
        similar_pages = st.session_state.analyzer.get_similar_pages(selected_page)
        
        if similar_pages:
            for i, page in enumerate(similar_pages):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.write(f"**{page['title']}**")
                    st.write(f"URL: {page['url']}")
                    
                    # Display matching keywords
                    keywords_html = ""
                    for keyword in page['keywords'][:5]:  # Show only first 5 keywords
                        keywords_html += f'<span class="keyword-tag">{keyword}</span>'
                    
                    st.markdown(keywords_html, unsafe_allow_html=True)
                
                with col2:
                    # Display similarity score
                    similarity_percentage = int(page['similarity_score'] * 100)
                    st.markdown(f'<div class="similarity-score">{similarity_percentage}% Match</div>', unsafe_allow_html=True)
                
                if i < len(similar_pages) - 1:
                    st.markdown("<hr>", unsafe_allow_html=True)
        else:
            st.info("No similar pages found.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Topic Distribution")
        
        # Get all keywords from all pages
        all_keywords = []
        for _, page in st.session_state.pages_df.iterrows():
            all_keywords.extend(page['keywords'])
        
        # Count keyword frequencies
        keyword_counts = pd.Series(all_keywords).value_counts().reset_index()
        keyword_counts.columns = ['Keyword', 'Count']
        
        # Display top keywords
        top_keywords = keyword_counts.head(20)
        
        fig = px.bar(
            top_keywords,
            x='Count',
            y='Keyword',
            orientation='h',
            title='Top 20 Keywords Across All Pages',
            color='Count',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Topic clusters
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Topic Clusters")
        
        # Identify topic clusters
        topic_clusters = st.session_state.analyzer.identify_topic_clusters()
        
        if topic_clusters:
            # Create tabs for each cluster
            cluster_tabs = st.tabs([f"Cluster {i+1}: {cluster['pillar_page']['title'][:20]}..." for i, cluster in enumerate(topic_clusters)])
            
            for i, (tab, cluster) in enumerate(zip(cluster_tabs, topic_clusters)):
                with tab:
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        # Display pillar page
                        st.write("**Pillar Page:**")
                        st.write(f"**{cluster['pillar_page']['title']}**")
                        st.write(f"URL: {cluster['pillar_page']['url']}")
                        
                        # Display pillar page keywords
                        keywords_html = ""
                        for keyword in cluster['pillar_page']['keywords']:
                            keywords_html += f'<span class="keyword-tag">{keyword}</span>'
                        
                        st.markdown(keywords_html, unsafe_allow_html=True)
                        
                        # Display cluster pages
                        st.write("**Cluster Pages:**")
                        
                        for page in cluster['cluster_pages']:
                            st.write(f"- **{page['title']}**")
                            st.write(f"  URL: {page['url']}")
                            st.write(f"  Similarity: {int(page['similarity_score'] * 100)}%")
                    
                    with col2:
                        # Create a network visualization of the cluster
                        G = nx.Graph()
                        
                        # Add pillar page
                        G.add_node(cluster['pillar_page']['url'], title=cluster['pillar_page']['title'], is_pillar=True)
                        
                        # Add cluster pages and edges
                        for page in cluster['cluster_pages']:
                            G.add_node(page['url'], title=page['title'], is_pillar=False)
                            G.add_edge(cluster['pillar_page']['url'], page['url'], weight=page['similarity_score'])
                        
                        # Create positions
                        pos = nx.spring_layout(G, seed=42)
                        
                        # Create figure
                        fig, ax = plt.subplots(figsize=(8, 8))
                        
                        # Draw nodes
                        nx.draw_networkx_nodes(
                            G, pos,
                            nodelist=[cluster['pillar_page']['url']],
                            node_color='#4285f4',
                            node_size=500,
                            alpha=0.8,
                            ax=ax
                        )
                        
                        nx.draw_networkx_nodes(
                            G, pos,
                            nodelist=[page['url'] for page in cluster['cluster_pages']],
                            node_color='#34a853',
                            node_size=300,
                            alpha=0.8,
                            ax=ax
                        )
                        
                        # Draw edges
                        nx.draw_networkx_edges(
                            G, pos,
                            width=2,
                            alpha=0.5,
                            edge_color='#5f6368',
                            ax=ax
                        )
                        
                        # Draw labels
                        nx.draw_networkx_labels(
                            G, pos,
                            labels={node: data['title'][:20] + '...' for node, data in G.nodes(data=True)},
                            font_size=8,
                            font_color='black',
                            ax=ax
                        )
                        
                        # Remove axis
                        ax.set_axis_off()
                        
                        # Display plot
                        st.pyplot(fig)
        else:
            st.info("No topic clusters identified.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Content Similarity Matrix")
        
        # Create a heatmap of content similarity
        if hasattr(st.session_state.analyzer, 'similarity_matrix') and st.session_state.analyzer.similarity_matrix is not None:
            # Get a subset of pages for better visualization
            max_pages = min(20, len(st.session_state.pages_df))
            subset_indices = list(range(max_pages))
            
            # Get page titles
            page_titles = [st.session_state.pages_df.iloc[i]['title'][:30] + '...' for i in subset_indices]
            
            # Create heatmap data
            heatmap_data = st.session_state.analyzer.similarity_matrix[:max_pages, :max_pages]
            
            # Create heatmap
            fig = px.imshow(
                heatmap_data,
                x=page_titles,
                y=page_titles,
                color_continuous_scale='Blues',
                title='Content Similarity Between Pages'
            )
            
            fig.update_layout(
                height=600,
                xaxis={'tickangle': 45}
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Content similarity matrix not available.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Content gaps
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Content Gaps")
        
        # Get orphaned pages
        orphaned_pages = st.session_state.analyzer.get_orphaned_pages()
        
        if len(orphaned_pages) > 0:
            st.write(f"Found {len(orphaned_pages)} pages with fewer than 3 incoming links:")
            
            for _, page in orphaned_pages.iterrows():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**{page['title']}**")
                    st.write(f"URL: {page['url']}")
                    
                    # Display keywords
                    keywords_html = ""
                    for keyword in page['keywords'][:5]:  # Show only first 5 keywords
                        keywords_html += f'<span class="keyword-tag">{keyword}</span>'
                    
                    st.markdown(keywords_html, unsafe_allow_html=True)
                
                with col2:
                    # Display incoming links count
                    st.write(f"**Incoming Links:** {page['incoming_links']}")
                    
                    # Add button to view link suggestions
                    if st.button("View Suggestions", key=f"gap_{page['url']}"):
                        # Store the selected page for link suggestions
                        st.session_state.selected_orphaned_page = page['url']
                        st.switch_page("pages/3_Link_Suggestions.py")
                
                st.markdown("<hr>", unsafe_allow_html=True)
        else:
            st.success("No content gaps found! All pages have at least 3 incoming links.")
        
        st.markdown('</div>', unsafe_allow_html=True)
