import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
from datetime import datetime
import time
import sys
import re

# Add the parent directory to the path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.crawler import WebCrawler
from utils.analyzer import ContentAnalyzer
from utils.suggestion_engine import SuggestionEngine

# Set page configuration
st.set_page_config(
    page_title="Site Crawler - Internal Linking SEO Pro",
    page_icon="🔍",
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
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #4285f4;
    }
    .metric-label {
        font-size: 1rem;
        color: #5f6368;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'crawler' not in st.session_state:
    st.session_state.crawler = WebCrawler()

if 'analyzer' not in st.session_state:
    st.session_state.analyzer = ContentAnalyzer()

if 'suggestion_engine' not in st.session_state:
    st.session_state.suggestion_engine = SuggestionEngine(st.session_state.analyzer)

if 'crawl_results' not in st.session_state:
    st.session_state.crawl_results = None

if 'pages_df' not in st.session_state:
    st.session_state.pages_df = None

if 'links_df' not in st.session_state:
    st.session_state.links_df = None

if 'crawled_sites' not in st.session_state:
    st.session_state.crawled_sites = []

if 'last_crawl_date' not in st.session_state:
    st.session_state.last_crawl_date = None

if 'site_stats' not in st.session_state:
    st.session_state.site_stats = {
        'pages_indexed': 0,
        'orphaned_pages': 0,
        'internal_links': 0,
        'topic_clusters': 0
    }

# Data paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
PAGES_DATA_PATH = os.path.join(DATA_DIR, "pages_data.csv")
LINKS_DATA_PATH = os.path.join(DATA_DIR, "links_data.csv")

# Main header
st.markdown('<h1 class="main-header">Site Crawler</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Crawl your website to analyze internal linking structure</p>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3 = st.tabs(["Crawl Settings", "Crawl Results", "Data Explorer"])

with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # Crawl settings form
    st.subheader("Crawl Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        url = st.text_input("Website URL", placeholder="https://example.com")
        
        # Validate URL
        is_valid_url = False
        if url:
            # Simple URL validation
            url_pattern = re.compile(r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
            if url_pattern.match(url):
                is_valid_url = True
            else:
                st.warning("Please enter a valid URL starting with http:// or https://")
    
    with col2:
        max_pages = st.number_input("Maximum Pages to Crawl", min_value=10, max_value=1000, value=50, step=10)
        max_depth = st.number_input("Maximum Crawl Depth", min_value=1, max_value=10, value=3, step=1)
    
    col3, col4 = st.columns(2)
    
    with col3:
        respect_robots = st.checkbox("Respect robots.txt", value=True)
        
    with col4:
        crawl_delay = st.slider("Crawl Delay (seconds)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
    
    # Crawl button
    crawl_col1, crawl_col2, crawl_col3 = st.columns([1, 1, 1])
    
    with crawl_col2:
        if st.button("Start Crawl", disabled=not is_valid_url, use_container_width=True):
            # Initialize crawler
            st.session_state.crawler = WebCrawler(
                respect_robots=respect_robots,
                delay=crawl_delay,
                max_pages=max_pages,
                max_depth=max_depth
            )
            
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Start crawl
            status_text.text("Starting crawl...")
            
            try:
                # For demo purposes, use simulate_crawl instead of actual crawl
                # In a real app, you would use: crawl_results = st.session_state.crawler.crawl(url)
                domain = re.sub(r'^https?://', '', url)
                domain = domain.split('/')[0]  # Extract domain from URL
                
                # Simulate crawl with progress updates
                for i in range(10):
                    progress_bar.progress((i + 1) / 10)
                    status_text.text(f"Crawling... ({i + 1}/10)")
                    time.sleep(0.5)  # Simulate crawl time
                
                crawl_results = st.session_state.crawler.simulate_crawl(domain, num_pages=max_pages)
                
                # Get pages and links DataFrames
                pages_df = st.session_state.crawler.get_pages_df()
                links_df = st.session_state.crawler.get_links_df()
                
                # Store results in session state
                st.session_state.crawl_results = crawl_results
                st.session_state.pages_df = pages_df
                st.session_state.links_df = links_df
                
                # Update last crawl date
                st.session_state.last_crawl_date = datetime.now().isoformat()
                
                # Add to crawled sites
                st.session_state.crawled_sites.append(crawl_results)
                
                # Analyze content
                status_text.text("Analyzing content...")
                progress_bar.progress(0.7)
                
                # Simulate content analysis
                st.session_state.analyzer.simulate_analysis(pages_df, links_df)
                progress_bar.progress(0.8)
                
                # Generate link suggestions
                status_text.text("Generating link suggestions...")
                st.session_state.suggestion_engine.set_data(pages_df, links_df)
                suggestions = st.session_state.suggestion_engine.simulate_suggestions(pages_df, links_df)
                progress_bar.progress(0.9)
                
                # Update site stats
                st.session_state.site_stats = st.session_state.suggestion_engine.get_site_stats()
                
                # Save data
                os.makedirs(DATA_DIR, exist_ok=True)
                pages_df.to_csv(PAGES_DATA_PATH, index=False)
                links_df.to_csv(LINKS_DATA_PATH, index=False)
                
                progress_bar.progress(1.0)
                status_text.text("Crawl completed successfully!")
                
                # Switch to results tab
                time.sleep(1)
                status_text.empty()
                progress_bar.empty()
                st.rerun()
                
            except Exception as e:
                status_text.error(f"Error during crawl: {str(e)}")
                progress_bar.empty()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Crawl history
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Crawl History")
    
    if st.session_state.crawled_sites:
        history_df = pd.DataFrame([
            {
                "Domain": site.get('domain', 'N/A'),
                "Date": site.get('date', 'N/A'),
                "Pages": site.get('pages_indexed', 0),
                "Duration (s)": round(site.get('duration', 0), 2)
            }
            for site in st.session_state.crawled_sites
        ])
        
        st.dataframe(history_df, use_container_width=True)
    else:
        st.info("No crawl history available.")
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    if st.session_state.crawl_results:
        # Crawl results overview
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Crawl Results Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f'<div class="metric-value">{st.session_state.crawl_results["pages_indexed"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Pages Indexed</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'<div class="metric-value">{st.session_state.site_stats["orphaned_pages"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Orphaned Pages</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown(f'<div class="metric-value">{st.session_state.site_stats["internal_links"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Internal Links</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown(f'<div class="metric-value">{st.session_state.site_stats["topic_clusters"]}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Topic Clusters</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Visualizations
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Crawl Visualizations")
        
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            # Create a pie chart of page depths
            if st.session_state.pages_df is not None:
                depth_counts = st.session_state.pages_df['depth'].value_counts().reset_index()
                depth_counts.columns = ['Depth', 'Count']
                
                fig1 = px.pie(
                    depth_counts, 
                    values='Count', 
                    names='Depth',
                    title='Pages by Crawl Depth',
                    color_discrete_sequence=px.colors.sequential.Blues_r,
                    hole=0.4
                )
                
                fig1.update_layout(
                    margin=dict(l=20, r=20, t=40, b=20),
                    height=300
                )
                
                st.plotly_chart(fig1, use_container_width=True)
        
        with viz_col2:
            # Create a bar chart of outgoing links distribution
            if st.session_state.pages_df is not None:
                # Create bins for outgoing links
                bins = [0, 1, 5, 10, 20, float('inf')]
                labels = ['0', '1-5', '6-10', '11-20', '21+']
                
                st.session_state.pages_df['outgoing_links_bin'] = pd.cut(
                    st.session_state.pages_df['outgoing_links'], 
                    bins=bins, 
                    labels=labels
                )
                
                outgoing_counts = st.session_state.pages_df['outgoing_links_bin'].value_counts().reset_index()
                outgoing_counts.columns = ['Links', 'Count']
                
                # Sort by bin order
                outgoing_counts['Links'] = pd.Categorical(
                    outgoing_counts['Links'],
                    categories=labels,
                    ordered=True
                )
                outgoing_counts = outgoing_counts.sort_values('Links')
                
                fig2 = px.bar(
                    outgoing_counts,
                    x='Links',
                    y='Count',
                    title='Pages by Outgoing Links',
                    color='Count',
                    color_continuous_scale='Blues'
                )
                
                fig2.update_layout(
                    margin=dict(l=20, r=20, t=40, b=20),
                    height=300
                )
                
                st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Next steps
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Next Steps")
        
        next_col1, next_col2, next_col3 = st.columns(3)
        
        with next_col1:
            if st.button("View Content Analysis", use_container_width=True):
                st.switch_page("pages/2_Content_Analysis.py")
        
        with next_col2:
            if st.button("View Link Suggestions", use_container_width=True):
                st.switch_page("pages/3_Link_Suggestions.py")
        
        with next_col3:
            if st.button("View Topic Clusters", use_container_width=True):
                st.switch_page("pages/4_Topic_Clusters.py")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No crawl results available. Start a crawl in the 'Crawl Settings' tab.")

with tab3:
    if st.session_state.pages_df is not None and st.session_state.links_df is not None:
        # Data explorer
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Pages Data")
        
        # Show pages data
        st.dataframe(st.session_state.pages_df, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Links Data")
        
        # Show links data
        st.dataframe(st.session_state.links_df, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Export options
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Export Data")
        
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            if st.download_button(
                "Download Pages Data (CSV)",
                data=st.session_state.pages_df.to_csv(index=False),
                file_name="pages_data.csv",
                mime="text/csv",
                use_container_width=True
            ):
                st.success("Pages data downloaded successfully!")
        
        with export_col2:
            if st.download_button(
                "Download Links Data (CSV)",
                data=st.session_state.links_df.to_csv(index=False),
                file_name="links_data.csv",
                mime="text/csv",
                use_container_width=True
            ):
                st.success("Links data downloaded successfully!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No data available. Start a crawl in the 'Crawl Settings' tab.")
