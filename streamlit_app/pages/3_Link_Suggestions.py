import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
import sys
from datetime import datetime
import numpy as np

# Add the parent directory to the path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.analyzer import ContentAnalyzer
from utils.suggestion_engine import SuggestionEngine

# Set page configuration
st.set_page_config(
    page_title="Link Suggestions - Internal Linking SEO Pro",
    page_icon="🔗",
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
    .suggestion-card {
        border: 1px solid #dadce0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .suggestion-title {
        font-size: 1.25rem;
        font-weight: bold;
        color: #202124;
        margin-bottom: 0.5rem;
    }
    .suggestion-url {
        color: #1a73e8;
        margin-bottom: 0.5rem;
        word-break: break-all;
    }
    .suggestion-context {
        background-color: #f8f9fa;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        font-family: monospace;
        white-space: pre-wrap;
        font-size: 0.875rem;
    }
    .html-code {
        background-color: #f8f9fa;
        padding: 0.75rem;
        border-radius: 0.25rem;
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        font-family: monospace;
        white-space: pre-wrap;
        font-size: 0.875rem;
        border: 1px solid #dadce0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = ContentAnalyzer()

if 'suggestion_engine' not in st.session_state:
    st.session_state.suggestion_engine = SuggestionEngine(st.session_state.analyzer)

if 'pages_df' not in st.session_state:
    st.session_state.pages_df = None

if 'links_df' not in st.session_state:
    st.session_state.links_df = None

if 'selected_orphaned_page' not in st.session_state:
    st.session_state.selected_orphaned_page = None

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
        
        # Set data for suggestion engine
        st.session_state.suggestion_engine.set_data(pages_df, links_df)

# Main header
st.markdown('<h1 class="main-header">Link Suggestions</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Get contextual internal linking recommendations for your content</p>', unsafe_allow_html=True)

# Check if data is available
if st.session_state.pages_df is None or st.session_state.links_df is None:
    st.warning("No data available. Please crawl your website first.")
    if st.button("Go to Site Crawler"):
        st.switch_page("pages/1_Site_Crawler.py")
else:
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Contextual Link Suggestions", "Orphaned Content", "Topic Cluster Links"])
    
    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Contextual Link Suggestions")
        
        # Page selector
        if st.session_state.selected_orphaned_page:
            # Use the selected orphaned page from the Content Analysis page
            selected_page = st.session_state.selected_orphaned_page
            st.session_state.selected_orphaned_page = None  # Reset after using
        else:
            selected_page = st.selectbox(
                "Select a page to get link suggestions:",
                options=st.session_state.pages_df['url'].tolist(),
                format_func=lambda x: st.session_state.pages_df[st.session_state.pages_df['url'] == x]['title'].iloc[0] if len(st.session_state.pages_df[st.session_state.pages_df['url'] == x]) > 0 else x
            )
        
        # Get page data
        page_data = st.session_state.pages_df[st.session_state.pages_df['url'] == selected_page].iloc[0]
        
        # Display page info
        st.write(f"**Selected Page:** {page_data['title']}")
        st.write(f"**URL:** {page_data['url']}")
        
        # Get contextual link suggestions
        contextual_suggestions = st.session_state.suggestion_engine.get_contextual_link_suggestions(selected_page)
        
        if contextual_suggestions:
            st.write(f"Found {len(contextual_suggestions)} contextual link suggestions:")
            
            # Display suggestions
            for i, suggestion in enumerate(contextual_suggestions):
                st.markdown(f'<div class="suggestion-card">', unsafe_allow_html=True)
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f'<div class="suggestion-title">{suggestion["target_title"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="suggestion-url">{suggestion["target_url"]}</div>', unsafe_allow_html=True)
                
                with col2:
                    # Display similarity score
                    similarity_percentage = int(suggestion['similarity_score'] * 100)
                    st.markdown(f'<div class="similarity-score">{similarity_percentage}% Match</div>', unsafe_allow_html=True)
                    
                    if 'occurrences' in suggestion:
                        st.write(f"Found in {suggestion['occurrences']} places")
                
                # Display context
                if 'context' in suggestion:
                    st.markdown("**Context:**")
                    st.markdown(f'<div class="suggestion-context">{suggestion["context"]}</div>', unsafe_allow_html=True)
                
                # Display suggested anchor text
                st.markdown("**Suggested Anchor Text:**")
                st.markdown(f'<div class="keyword-tag">{suggestion["suggested_anchor"]}</div>', unsafe_allow_html=True)
                
                # Display HTML code
                with st.expander("Show HTML Code"):
                    html_code = f'<a href="{suggestion["target_url"]}" title="{suggestion["target_title"]}">{suggestion["suggested_anchor"]}</a>'
                    st.markdown(f'<div class="html-code">{html_code}</div>', unsafe_allow_html=True)
                    st.code(html_code, language='html')
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No contextual link suggestions found for this page.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Orphaned Content Recommendations")
        
        # Get orphaned content opportunities
        orphaned_opportunities = st.session_state.suggestion_engine.find_link_opportunities()
        
        if orphaned_opportunities:
            # Group by orphaned page
            orphaned_pages = {}
            for opp in orphaned_opportunities:
                if opp['orphaned_url'] not in orphaned_pages:
                    orphaned_pages[opp['orphaned_url']] = {
                        'title': opp['orphaned_title'],
                        'opportunities': []
                    }
                orphaned_pages[opp['orphaned_url']]['opportunities'].append(opp)
            
            # Create expanders for each orphaned page
            for orphaned_url, data in orphaned_pages.items():
                with st.expander(f"{data['title']} ({len(data['opportunities'])} opportunities)"):
                    st.write(f"**Orphaned Page:** {data['title']}")
                    st.write(f"**URL:** {orphaned_url}")
                    
                    # Display opportunities
                    for opp in data['opportunities']:
                        st.markdown(f'<div class="suggestion-card">', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f'<div class="suggestion-title">Link from: {opp["source_title"]}</div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="suggestion-url">{opp["source_url"]}</div>', unsafe_allow_html=True)
                        
                        with col2:
                            # Display similarity score
                            similarity_percentage = int(opp['similarity_score'] * 100)
                            st.markdown(f'<div class="similarity-score">{similarity_percentage}% Match</div>', unsafe_allow_html=True)
                        
                        # Display matching keywords
                        st.markdown("**Matching Keywords:**")
                        keywords_html = ""
                        for keyword in opp['matching_keywords']:
                            keywords_html += f'<span class="keyword-tag">{keyword}</span>'
                        
                        st.markdown(keywords_html, unsafe_allow_html=True)
                        
                        # Display suggested anchor text
                        st.markdown("**Suggested Anchor Text:**")
                        st.markdown(f'<div class="keyword-tag">{opp["suggested_anchor"]}</div>', unsafe_allow_html=True)
                        
                        # Display HTML code
                        with st.expander("Show HTML Code"):
                            html_code = f'<a href="{opp["orphaned_url"]}" title="{opp["orphaned_title"]}">{opp["suggested_anchor"]}</a>'
                            st.markdown(f'<div class="html-code">{html_code}</div>', unsafe_allow_html=True)
                            st.code(html_code, language='html')
                        
                        st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No orphaned content opportunities found.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Topic Cluster Link Recommendations")
        
        # Get topic cluster opportunities
        cluster_opportunities = st.session_state.suggestion_engine.find_topic_cluster_opportunities()
        
        if cluster_opportunities:
            # Separate opportunities by type
            to_pillar = [opp for opp in cluster_opportunities if opp['cluster_type'] == 'to_pillar']
            from_pillar = [opp for opp in cluster_opportunities if opp['cluster_type'] == 'from_pillar']
            
            # Create two columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Links to Pillar Pages**")
                
                if to_pillar:
                    for opp in to_pillar:
                        st.markdown(f'<div class="suggestion-card">', unsafe_allow_html=True)
                        
                        st.markdown(f'<div class="suggestion-title">Link from: {opp["source_title"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="suggestion-url">{opp["source_url"]}</div>', unsafe_allow_html=True)
                        
                        st.markdown(f'<div class="suggestion-title">To pillar: {opp["target_title"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="suggestion-url">{opp["target_url"]}</div>', unsafe_allow_html=True)
                        
                        # Display similarity score
                        similarity_percentage = int(opp['similarity_score'] * 100)
                        st.markdown(f'<div class="similarity-score">{similarity_percentage}% Match</div>', unsafe_allow_html=True)
                        
                        # Display suggested anchor text
                        st.markdown("**Suggested Anchor Text:**")
                        st.markdown(f'<div class="keyword-tag">{opp["suggested_anchor"]}</div>', unsafe_allow_html=True)
                        
                        # Display HTML code
                        with st.expander("Show HTML Code"):
                            html_code = f'<a href="{opp["target_url"]}" title="{opp["target_title"]}">{opp["suggested_anchor"]}</a>'
                            st.markdown(f'<div class="html-code">{html_code}</div>', unsafe_allow_html=True)
                            st.code(html_code, language='html')
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("No links to pillar pages needed.")
            
            with col2:
                st.write("**Links from Pillar Pages**")
                
                if from_pillar:
                    for opp in from_pillar:
                        st.markdown(f'<div class="suggestion-card">', unsafe_allow_html=True)
                        
                        st.markdown(f'<div class="suggestion-title">Link from pillar: {opp["source_title"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="suggestion-url">{opp["source_url"]}</div>', unsafe_allow_html=True)
                        
                        st.markdown(f'<div class="suggestion-title">To: {opp["target_title"]}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="suggestion-url">{opp["target_url"]}</div>', unsafe_allow_html=True)
                        
                        # Display similarity score
                        similarity_percentage = int(opp['similarity_score'] * 100)
                        st.markdown(f'<div class="similarity-score">{similarity_percentage}% Match</div>', unsafe_allow_html=True)
                        
                        # Display suggested anchor text
                        st.markdown("**Suggested Anchor Text:**")
                        st.markdown(f'<div class="keyword-tag">{opp["suggested_anchor"]}</div>', unsafe_allow_html=True)
                        
                        # Display HTML code
                        with st.expander("Show HTML Code"):
                            html_code = f'<a href="{opp["target_url"]}" title="{opp["target_title"]}">{opp["suggested_anchor"]}</a>'
                            st.markdown(f'<div class="html-code">{html_code}</div>', unsafe_allow_html=True)
                            st.code(html_code, language='html')
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("No links from pillar pages needed.")
        else:
            st.info("No topic cluster link opportunities found.")
        
        st.markdown('</div>', unsafe_allow_html=True)
