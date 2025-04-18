import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
import sys
from datetime import datetime
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Add the parent directory to the path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.analyzer import ContentAnalyzer
from utils.suggestion_engine import SuggestionEngine

# Set page configuration
st.set_page_config(
    page_title="Topic Clusters - Internal Linking SEO Pro",
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
        color: #aaa;
        margin-bottom: 1rem;
    }
    .card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #1e1e1e;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.2);
        margin-bottom: 1rem;
        border: 1px solid #333;
    }
    .keyword-tag {
        display: inline-block;
        background-color: #2c3e50;
        color: #4285f4;
        padding: 0.25rem 0.5rem;
        border-radius: 1rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        font-size: 0.875rem;
    }
    .cluster-card {
        border: 1px solid #444;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: #2d2d2d;
    }
    .cluster-title {
        font-size: 1.25rem;
        font-weight: bold;
        color: #eee;
        margin-bottom: 0.5rem;
    }
    .pillar-badge {
        display: inline-block;
        background-color: #4285f4;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
        margin-right: 0.5rem;
    }
    .cluster-badge {
        display: inline-block;
        background-color: #34a853;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
        margin-right: 0.5rem;
    }
    .health-score {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .health-good {
        background-color: #1e3a2b;
        color: #34a853;
    }
    .health-medium {
        background-color: #3d3523;
        color: #fbbc04;
    }
    .health-poor {
        background-color: #3b1e1c;
        color: #ea4335;
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

# Initialize session state variables if they don't exist
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = ContentAnalyzer()

if 'suggestion_engine' not in st.session_state:
    st.session_state.suggestion_engine = SuggestionEngine(st.session_state.analyzer)

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

        # Set data for suggestion engine
        st.session_state.suggestion_engine.set_data(pages_df, links_df)

# Main header
st.markdown('<h1 class="main-header">Topic Clusters</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Analyze and optimize your topic clusters for better SEO</p>', unsafe_allow_html=True)

# Check if data is available
if st.session_state.pages_df is None or st.session_state.links_df is None:
    st.warning("No data available. Please crawl your website first.")
    if st.button("Go to Site Crawler"):
        st.switch_page("pages/1_Site_Crawler.py")
else:
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Topic Cluster Overview", "Cluster Visualization", "Cluster Management"])

    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Topic Clusters Overview")

        # Get topic clusters
        topic_clusters = st.session_state.analyzer.identify_topic_clusters()

        if topic_clusters:
            # Display summary
            st.write(f"Found {len(topic_clusters)} topic clusters across your website.")

            # Create metrics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Clusters", len(topic_clusters))

            with col2:
                # Calculate average cluster size
                avg_size = sum(len(cluster['cluster_pages']) for cluster in topic_clusters) / len(topic_clusters)
                st.metric("Avg. Cluster Size", f"{avg_size:.1f} pages")

            with col3:
                # Calculate total pages in clusters
                total_cluster_pages = sum(len(cluster['cluster_pages']) for cluster in topic_clusters) + len(topic_clusters)  # Add pillar pages
                st.metric("Pages in Clusters", total_cluster_pages)

            with col4:
                # Calculate percentage of pages in clusters
                percentage = (total_cluster_pages / len(st.session_state.pages_df)) * 100
                st.metric("% of Site in Clusters", f"{percentage:.1f}%")

            # Create a bar chart of cluster sizes
            cluster_sizes = [len(cluster['cluster_pages']) + 1 for cluster in topic_clusters]  # +1 for pillar page
            cluster_names = [cluster['pillar_page']['title'][:20] + "..." for cluster in topic_clusters]

            cluster_size_df = pd.DataFrame({
                'Cluster': cluster_names,
                'Size': cluster_sizes
            })

            fig = px.bar(
                cluster_size_df,
                x='Cluster',
                y='Size',
                title='Topic Cluster Sizes',
                color='Size',
                color_continuous_scale='Blues'
            )

            fig.update_layout(
                xaxis_title="Cluster",
                yaxis_title="Number of Pages",
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No topic clusters identified. Try adjusting the similarity threshold or adding more content to your site.")

        st.markdown('</div>', unsafe_allow_html=True)

        # Cluster details
        if topic_clusters:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Cluster Details")

            for i, cluster in enumerate(topic_clusters):
                st.markdown(f'<div class="cluster-card">', unsafe_allow_html=True)

                # Calculate cluster health score
                # This is a simplified score based on:
                # 1. Number of pages in the cluster
                # 2. Average similarity score
                # 3. Percentage of bidirectional links

                cluster_size = len(cluster['cluster_pages']) + 1  # +1 for pillar page
                avg_similarity = sum(page['similarity_score'] for page in cluster['cluster_pages']) / len(cluster['cluster_pages']) if cluster['cluster_pages'] else 0

                # Simulate bidirectional link percentage
                bidirectional_percentage = np.random.uniform(0.3, 0.9)

                # Calculate health score (0-100)
                health_score = (
                    (min(cluster_size, 10) / 10) * 0.4 +  # Size component (max 10 pages)
                    avg_similarity * 0.3 +                # Similarity component
                    bidirectional_percentage * 0.3        # Bidirectional links component
                ) * 100

                # Determine health category
                health_category = "good" if health_score >= 70 else "medium" if health_score >= 40 else "poor"

                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f'<div class="cluster-title">Cluster {i+1}: {cluster["pillar_page"]["title"]}</div>', unsafe_allow_html=True)
                    st.write(f"**Pillar Page:** {cluster['pillar_page']['url']}")

                    # Display pillar page keywords
                    keywords_html = ""
                    for keyword in cluster['pillar_page']['keywords']:
                        keywords_html += f'<span class="keyword-tag">{keyword}</span>'

                    st.markdown(keywords_html, unsafe_allow_html=True)

                with col2:
                    # Display health score
                    st.markdown(f'<div class="health-score health-{health_category}">{health_score:.0f}% Health</div>', unsafe_allow_html=True)

                    st.write(f"**Pages:** {cluster_size}")
                    st.write(f"**Avg. Similarity:** {avg_similarity:.2f}")
                    st.write(f"**Bidirectional Links:** {bidirectional_percentage:.0%}")

                # Display cluster pages
                with st.expander(f"View {len(cluster['cluster_pages'])} cluster pages"):
                    for page in cluster['cluster_pages']:
                        st.write(f"**{page['title']}**")
                        st.write(f"URL: {page['url']}")
                        st.write(f"Similarity to Pillar: {page['similarity_score']:.2f}")

                        # Display page keywords
                        keywords_html = ""
                        for keyword in page['keywords']:
                            keywords_html += f'<span class="keyword-tag">{keyword}</span>'

                        st.markdown(keywords_html, unsafe_allow_html=True)

                        st.markdown("<hr>", unsafe_allow_html=True)

                # Add button to view link suggestions for this cluster
                if st.button("View Link Suggestions", key=f"cluster_{i}"):
                    # Store the selected cluster for link suggestions
                    st.session_state.selected_cluster = i
                    st.switch_page("pages/3_Link_Suggestions.py")

                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Topic Cluster Visualization")

        # Get topic clusters
        topic_clusters = st.session_state.analyzer.identify_topic_clusters()

        if topic_clusters:
            # Create a network graph of all clusters
            G = nx.Graph()

            # Add all nodes and edges
            for i, cluster in enumerate(topic_clusters):
                # Add pillar page
                pillar_url = cluster['pillar_page']['url']
                G.add_node(pillar_url,
                           title=cluster['pillar_page']['title'],
                           is_pillar=True,
                           cluster=i)

                # Add cluster pages and edges
                for page in cluster['cluster_pages']:
                    page_url = page['url']
                    G.add_node(page_url,
                               title=page['title'],
                               is_pillar=False,
                               cluster=i)
                    G.add_edge(pillar_url, page_url, weight=page['similarity_score'])

            # Create positions using a spring layout
            pos = nx.spring_layout(G, seed=42)

            # Create a Plotly figure
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=0.5, color='#888'),
                hoverinfo='none',
                mode='lines')

            # Create node traces for pillar pages and cluster pages
            pillar_nodes = [node for node, attrs in G.nodes(data=True) if attrs.get('is_pillar', False)]
            cluster_nodes = [node for node, attrs in G.nodes(data=True) if not attrs.get('is_pillar', False)]

            # Create a color map for clusters
            cluster_colors = px.colors.qualitative.Plotly

            # Pillar node trace
            pillar_node_x = [pos[node][0] for node in pillar_nodes]
            pillar_node_y = [pos[node][1] for node in pillar_nodes]
            pillar_node_colors = [cluster_colors[G.nodes[node]['cluster'] % len(cluster_colors)] for node in pillar_nodes]

            pillar_node_trace = go.Scatter(
                x=pillar_node_x, y=pillar_node_y,
                mode='markers',
                hoverinfo='text',
                marker=dict(
                    size=15,
                    color=pillar_node_colors,
                    line_width=2,
                    line=dict(color='white')
                ),
                text=[G.nodes[node]['title'] for node in pillar_nodes],
                name='Pillar Pages'
            )

            # Cluster node trace
            cluster_node_x = [pos[node][0] for node in cluster_nodes]
            cluster_node_y = [pos[node][1] for node in cluster_nodes]
            cluster_node_colors = [cluster_colors[G.nodes[node]['cluster'] % len(cluster_colors)] for node in cluster_nodes]

            cluster_node_trace = go.Scatter(
                x=cluster_node_x, y=cluster_node_y,
                mode='markers',
                hoverinfo='text',
                marker=dict(
                    size=10,
                    color=cluster_node_colors,
                    line_width=1,
                    line=dict(color='white')
                ),
                text=[G.nodes[node]['title'] for node in cluster_nodes],
                name='Cluster Pages'
            )

            # Create figure
            fig = go.Figure(data=[edge_trace, pillar_node_trace, cluster_node_trace],
                            layout=go.Layout(
                                title='Topic Clusters Network',
                                titlefont_size=16,
                                showlegend=True,
                                hovermode='closest',
                                margin=dict(b=20, l=5, r=5, t=40),
                                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                height=600,
                                legend=dict(
                                    yanchor="top",
                                    y=0.99,
                                    xanchor="left",
                                    x=0.01
                                )
                            ))

            st.plotly_chart(fig, use_container_width=True)

            # Add legend
            st.write("**Legend:**")
            legend_html = ""
            for i, cluster in enumerate(topic_clusters):
                color = cluster_colors[i % len(cluster_colors)]
                legend_html += f'<span style="color: {color}; font-weight: bold; margin-right: 10px;">●</span> Cluster {i+1}: {cluster["pillar_page"]["title"][:30]}...<br>'

            st.markdown(legend_html, unsafe_allow_html=True)
        else:
            st.info("No topic clusters identified. Try adjusting the similarity threshold or adding more content to your site.")

        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Cluster Management")

        # Get topic clusters
        topic_clusters = st.session_state.analyzer.identify_topic_clusters()

        if topic_clusters:
            # Create a form to designate pillar pages
            st.write("**Designate Pillar Pages**")
            st.write("Select pages to designate as pillar pages for your topic clusters.")

            with st.form("pillar_page_form"):
                # Get all pages that are not already pillar pages
                existing_pillar_urls = [cluster['pillar_page']['url'] for cluster in topic_clusters]
                potential_pillar_pages = st.session_state.pages_df[~st.session_state.pages_df['url'].isin(existing_pillar_urls)]

                # Select a page
                selected_page = st.selectbox(
                    "Select a page to designate as a pillar page:",
                    options=potential_pillar_pages['url'].tolist(),
                    format_func=lambda x: potential_pillar_pages[potential_pillar_pages['url'] == x]['title'].iloc[0] if len(potential_pillar_pages[potential_pillar_pages['url'] == x]) > 0 else x
                )

                # Enter main topic
                main_topic = st.text_input("Main Topic for this Pillar Page:")

                # Submit button
                submit_button = st.form_submit_button("Designate as Pillar Page")

                if submit_button:
                    if main_topic:
                        st.success(f"Page designated as a pillar page for topic: {main_topic}")
                        st.info("In a real application, this would create a new topic cluster with this page as the pillar.")
                    else:
                        st.error("Please enter a main topic for the pillar page.")

            # Topic cluster management
            st.write("**Manage Existing Clusters**")

            for i, cluster in enumerate(topic_clusters):
                with st.expander(f"Cluster {i+1}: {cluster['pillar_page']['title']}"):
                    st.write(f"**Pillar Page:** {cluster['pillar_page']['url']}")

                    # Display cluster pages
                    st.write(f"**Cluster Pages ({len(cluster['cluster_pages'])}):**")

                    for j, page in enumerate(cluster['cluster_pages']):
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.write(f"{j+1}. **{page['title']}**")
                            st.write(f"   URL: {page['url']}")

                        with col2:
                            # Add a button to remove from cluster
                            if st.button("Remove from Cluster", key=f"remove_{i}_{j}"):
                                st.info(f"Page would be removed from cluster {i+1}.")
                                st.info("In a real application, this would update the cluster structure.")

                    # Add a button to delete the cluster
                    if st.button("Delete Cluster", key=f"delete_{i}"):
                        st.warning(f"Are you sure you want to delete cluster {i+1}?")

                        col1, col2 = st.columns(2)

                        with col1:
                            if st.button("Yes, Delete", key=f"confirm_delete_{i}"):
                                st.success(f"Cluster {i+1} deleted.")
                                st.info("In a real application, this would remove the cluster structure.")

                        with col2:
                            if st.button("Cancel", key=f"cancel_delete_{i}"):
                                st.info("Deletion cancelled.")
        else:
            st.info("No topic clusters identified. Try adjusting the similarity threshold or adding more content to your site.")

        st.markdown('</div>', unsafe_allow_html=True)
