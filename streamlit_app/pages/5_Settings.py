import streamlit as st
import pandas as pd
import os
import json
import sys
import shutil
from datetime import datetime

# Add the parent directory to the path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set page configuration
st.set_page_config(
    page_title="Settings - Internal Linking SEO Pro",
    page_icon="⚙️",
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
    .settings-section {
        margin-bottom: 2rem;
    }
    .settings-title {
        font-size: 1.25rem;
        font-weight: bold;
        color: #202124;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Data paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
SETTINGS_PATH = os.path.join(DATA_DIR, "settings.json")

# Initialize session state variables if they don't exist
if 'settings' not in st.session_state:
    # Default settings
    st.session_state.settings = {
        'crawl': {
            'max_pages': 50,
            'max_depth': 3,
            'respect_robots': True,
            'crawl_delay': 1.0
        },
        'analysis': {
            'min_incoming_links': 3,
            'similarity_threshold': 0.3,
            'max_keywords': 10,
            'max_suggestions': 5
        },
        'display': {
            'dark_mode': False,
            'show_advanced_metrics': False
        }
    }

# Load settings if available
def load_settings():
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, 'r') as f:
            return json.load(f)
    return st.session_state.settings

# Save settings
def save_settings(settings):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SETTINGS_PATH, 'w') as f:
        json.dump(settings, f)

# Load settings if not already in session state
if 'settings' not in st.session_state:
    st.session_state.settings = load_settings()

# Main header
st.markdown('<h1 class="main-header">Settings</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Configure the application settings</p>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Crawl Settings", "Analysis Settings", "Display Settings", "Data Management"])

with tab1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.markdown('<div class="settings-title">Crawl Configuration</div>', unsafe_allow_html=True)
    
    # Crawl settings
    max_pages = st.slider(
        "Maximum Pages to Crawl",
        min_value=10,
        max_value=1000,
        value=st.session_state.settings['crawl']['max_pages'],
        step=10
    )
    
    max_depth = st.slider(
        "Maximum Crawl Depth",
        min_value=1,
        max_value=10,
        value=st.session_state.settings['crawl']['max_depth'],
        step=1
    )
    
    respect_robots = st.checkbox(
        "Respect robots.txt",
        value=st.session_state.settings['crawl']['respect_robots']
    )
    
    crawl_delay = st.slider(
        "Crawl Delay (seconds)",
        min_value=0.1,
        max_value=5.0,
        value=st.session_state.settings['crawl']['crawl_delay'],
        step=0.1
    )
    
    # Update settings
    st.session_state.settings['crawl']['max_pages'] = max_pages
    st.session_state.settings['crawl']['max_depth'] = max_depth
    st.session_state.settings['crawl']['respect_robots'] = respect_robots
    st.session_state.settings['crawl']['crawl_delay'] = crawl_delay
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.markdown('<div class="settings-title">Content Analysis Configuration</div>', unsafe_allow_html=True)
    
    # Analysis settings
    min_incoming_links = st.slider(
        "Minimum Incoming Links (for orphaned content)",
        min_value=1,
        max_value=10,
        value=st.session_state.settings['analysis']['min_incoming_links'],
        step=1
    )
    
    similarity_threshold = st.slider(
        "Content Similarity Threshold",
        min_value=0.1,
        max_value=0.9,
        value=st.session_state.settings['analysis']['similarity_threshold'],
        step=0.1
    )
    
    max_keywords = st.slider(
        "Maximum Keywords per Page",
        min_value=5,
        max_value=30,
        value=st.session_state.settings['analysis']['max_keywords'],
        step=5
    )
    
    max_suggestions = st.slider(
        "Maximum Link Suggestions per Page",
        min_value=3,
        max_value=20,
        value=st.session_state.settings['analysis']['max_suggestions'],
        step=1
    )
    
    # Update settings
    st.session_state.settings['analysis']['min_incoming_links'] = min_incoming_links
    st.session_state.settings['analysis']['similarity_threshold'] = similarity_threshold
    st.session_state.settings['analysis']['max_keywords'] = max_keywords
    st.session_state.settings['analysis']['max_suggestions'] = max_suggestions
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.markdown('<div class="settings-title">Display Settings</div>', unsafe_allow_html=True)
    
    # Display settings
    dark_mode = st.checkbox(
        "Dark Mode",
        value=st.session_state.settings['display']['dark_mode'],
        help="Enable dark mode for the application (requires restart)"
    )
    
    show_advanced_metrics = st.checkbox(
        "Show Advanced Metrics",
        value=st.session_state.settings['display']['show_advanced_metrics'],
        help="Display additional advanced metrics in the analysis"
    )
    
    # Update settings
    st.session_state.settings['display']['dark_mode'] = dark_mode
    st.session_state.settings['display']['show_advanced_metrics'] = show_advanced_metrics
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="settings-section">', unsafe_allow_html=True)
    st.markdown('<div class="settings-title">Data Management</div>', unsafe_allow_html=True)
    
    # Data management
    st.write("Manage your application data and settings.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Reset Settings to Default", use_container_width=True):
            # Confirm reset
            st.warning("Are you sure you want to reset all settings to default?")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("Yes, Reset Settings", key="confirm_reset_settings"):
                    # Reset settings to default
                    st.session_state.settings = {
                        'crawl': {
                            'max_pages': 50,
                            'max_depth': 3,
                            'respect_robots': True,
                            'crawl_delay': 1.0
                        },
                        'analysis': {
                            'min_incoming_links': 3,
                            'similarity_threshold': 0.3,
                            'max_keywords': 10,
                            'max_suggestions': 5
                        },
                        'display': {
                            'dark_mode': False,
                            'show_advanced_metrics': False
                        }
                    }
                    
                    # Save settings
                    save_settings(st.session_state.settings)
                    
                    st.success("Settings reset to default.")
                    st.rerun()
            
            with col_b:
                if st.button("Cancel", key="cancel_reset_settings"):
                    st.info("Reset cancelled.")
    
    with col2:
        if st.button("Clear All Data", use_container_width=True):
            # Confirm clear
            st.warning("Are you sure you want to clear all data? This will delete all crawled pages, links, and analysis results.")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("Yes, Clear All Data", key="confirm_clear_data"):
                    # Clear all data
                    if os.path.exists(DATA_DIR):
                        # Delete all files except settings.json
                        for file in os.listdir(DATA_DIR):
                            if file != "settings.json":
                                file_path = os.path.join(DATA_DIR, file)
                                if os.path.isfile(file_path):
                                    os.remove(file_path)
                    
                    # Reset session state
                    if 'pages_df' in st.session_state:
                        del st.session_state.pages_df
                    
                    if 'links_df' in st.session_state:
                        del st.session_state.links_df
                    
                    if 'crawl_results' in st.session_state:
                        del st.session_state.crawl_results
                    
                    if 'crawled_sites' in st.session_state:
                        st.session_state.crawled_sites = []
                    
                    if 'last_crawl_date' in st.session_state:
                        st.session_state.last_crawl_date = None
                    
                    if 'site_stats' in st.session_state:
                        st.session_state.site_stats = {
                            'pages_indexed': 0,
                            'orphaned_pages': 0,
                            'internal_links': 0,
                            'topic_clusters': 0
                        }
                    
                    st.success("All data cleared successfully.")
                    st.rerun()
            
            with col_b:
                if st.button("Cancel", key="cancel_clear_data"):
                    st.info("Clear cancelled.")
    
    # Export/Import settings
    st.markdown('<div class="settings-title">Export/Import Settings</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export Settings", use_container_width=True):
            # Export settings as JSON
            settings_json = json.dumps(st.session_state.settings, indent=2)
            
            st.download_button(
                "Download Settings JSON",
                data=settings_json,
                file_name="internal_linking_seo_pro_settings.json",
                mime="application/json",
                use_container_width=True
            )
    
    with col2:
        uploaded_file = st.file_uploader("Import Settings", type="json")
        
        if uploaded_file is not None:
            try:
                # Load settings from uploaded file
                imported_settings = json.load(uploaded_file)
                
                # Validate settings structure
                required_keys = ['crawl', 'analysis', 'display']
                if all(key in imported_settings for key in required_keys):
                    # Update settings
                    st.session_state.settings = imported_settings
                    
                    # Save settings
                    save_settings(st.session_state.settings)
                    
                    st.success("Settings imported successfully.")
                    st.rerun()
                else:
                    st.error("Invalid settings file. Please upload a valid settings JSON file.")
            except Exception as e:
                st.error(f"Error importing settings: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Save settings button
if st.button("Save Settings", use_container_width=True):
    # Save settings
    save_settings(st.session_state.settings)
    
    st.success("Settings saved successfully.")
    
    # Add a button to return to home
    if st.button("Return to Home"):
        st.switch_page("Home.py")
