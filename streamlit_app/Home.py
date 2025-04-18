import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Internal Linking SEO Pro",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4285f4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #5f6368;
        margin-bottom: 2rem;
    }
    .card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #1e1e1e;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.2);
        margin-bottom: 1rem;
        border: 1px solid #333;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4285f4;
    }
    .metric-label {
        font-size: 1rem;
        color: #aaa;
    }
    .info-text {
        font-size: 1rem;
        color: #aaa;
    }
    /* Hide Streamlit's default elements that create white space */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    /* Make info messages match dark theme */
    .stAlert {
        background-color: #2d2d2d !important;
        color: #aaa !important;
        border: 1px solid #444 !important;
    }
    /* Fix button styling */
    .stButton button {
        background-color: #4285f4;
        color: white;
        border: none;
    }
    .stButton button:hover {
        background-color: #5c9aff;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
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
DATA_DIR = "data"
CRAWL_DATA_PATH = os.path.join(DATA_DIR, "crawl_data.json")
STATS_DATA_PATH = os.path.join(DATA_DIR, "site_stats.json")

# Load data if exists
def load_data():
    if os.path.exists(CRAWL_DATA_PATH):
        with open(CRAWL_DATA_PATH, 'r') as f:
            st.session_state.crawled_sites = json.load(f)

    if os.path.exists(STATS_DATA_PATH):
        with open(STATS_DATA_PATH, 'r') as f:
            stats = json.load(f)
            st.session_state.site_stats = stats
            if 'last_crawl_date' in stats:
                st.session_state.last_crawl_date = stats['last_crawl_date']

# Save data
def save_data():
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(CRAWL_DATA_PATH, 'w') as f:
        json.dump(st.session_state.crawled_sites, f)

    stats = st.session_state.site_stats.copy()
    stats['last_crawl_date'] = st.session_state.last_crawl_date

    with open(STATS_DATA_PATH, 'w') as f:
        json.dump(stats, f)

# Load data on app start
load_data()

# Main header
st.markdown('<h1 class="main-header">Internal Linking SEO Pro</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Advanced internal linking optimization tool for SEO professionals</p>', unsafe_allow_html=True)

# Dashboard layout
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    # Site overview
    st.subheader("Site Overview")

    if st.session_state.crawled_sites:
        latest_site = st.session_state.crawled_sites[-1]
        st.write(f"**Current site:** {latest_site.get('domain', 'N/A')}")

        if st.session_state.last_crawl_date:
            try:
                last_crawl = datetime.fromisoformat(st.session_state.last_crawl_date)
                st.write(f"**Last crawl:** {last_crawl.strftime('%Y-%m-%d %H:%M')}")
            except:
                st.write("**Last crawl:** N/A")

        # Quick actions
        st.subheader("Quick Actions")
        col_a, col_b = st.columns(2)

        with col_a:
            if st.button("🔍 Start New Crawl", use_container_width=True):
                st.switch_page("pages/1_Site_Crawler.py")

        with col_b:
            if st.button("🔗 View Link Suggestions", use_container_width=True):
                st.switch_page("pages/3_Link_Suggestions.py")
    else:
        st.info("No sites have been crawled yet. Start by crawling a site in the Site Crawler page.")

        if st.button("🔍 Start First Crawl", use_container_width=True):
            st.switch_page("pages/1_Site_Crawler.py")

    st.markdown('</div>', unsafe_allow_html=True)

    # Recent activity
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Recent Activity")

    if st.session_state.crawled_sites:
        activity_data = []

        for site in st.session_state.crawled_sites[-5:]:
            activity_data.append({
                "Domain": site.get('domain', 'N/A'),
                "Date": site.get('date', 'N/A'),
                "Pages": site.get('pages_indexed', 0)
            })

        if activity_data:
            activity_df = pd.DataFrame(activity_data)
            st.dataframe(activity_df, use_container_width=True)
    else:
        st.info("No recent activity to display.")

    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Key metrics
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Key Metrics")

    metric_col1, metric_col2 = st.columns(2)

    with metric_col1:
        st.markdown(f'<div class="metric-value">{st.session_state.site_stats["pages_indexed"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Pages Indexed</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="metric-value">{st.session_state.site_stats["orphaned_pages"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Orphaned Pages</div>', unsafe_allow_html=True)

    with metric_col2:
        st.markdown(f'<div class="metric-value">{st.session_state.site_stats["internal_links"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Internal Links</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="metric-value">{st.session_state.site_stats["topic_clusters"]}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Topic Clusters</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Visualization
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Link Distribution")

    if st.session_state.site_stats["pages_indexed"] > 0:
        # Create sample data for visualization
        link_data = {
            "Category": ["0-1 links", "2-5 links", "6-10 links", "11+ links"],
            "Count": [
                st.session_state.site_stats["orphaned_pages"],
                int(st.session_state.site_stats["pages_indexed"] * 0.4),
                int(st.session_state.site_stats["pages_indexed"] * 0.3),
                int(st.session_state.site_stats["pages_indexed"] * 0.3 - st.session_state.site_stats["orphaned_pages"])
            ]
        }

        link_df = pd.DataFrame(link_data)

        # Create pie chart
        fig = px.pie(
            link_df,
            values="Count",
            names="Category",
            color_discrete_sequence=px.colors.sequential.Blues_r,
            hole=0.4
        )

        fig.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            height=300
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for visualization.")

    st.markdown('</div>', unsafe_allow_html=True)

# App information
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("About Internal Linking SEO Pro")

st.markdown("""
<p class="info-text">
Internal Linking SEO Pro is a powerful tool designed to help SEO professionals optimize their website's internal linking structure.
The tool analyzes your website content, identifies opportunities for internal linking, and provides actionable recommendations to improve your site's SEO performance.
</p>

<p class="info-text">
Key features include:
</p>

<ul class="info-text">
    <li>Website crawling and content indexing</li>
    <li>NLP-based content analysis</li>
    <li>Contextual link suggestions</li>
    <li>Content gap analysis</li>
    <li>Topic cluster optimization</li>
</ul>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Save data on app close (this won't work perfectly in Streamlit, but it's a start)
save_data()
