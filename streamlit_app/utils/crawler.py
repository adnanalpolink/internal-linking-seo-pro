import requests
from bs4 import BeautifulSoup
import time
import re
import urllib.parse
from urllib.robotparser import RobotFileParser
from datetime import datetime
import random
from collections import deque
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebCrawler:
    def __init__(self, respect_robots=True, delay=1, max_pages=100, max_depth=3):
        self.visited_urls = set()
        self.urls_to_visit = deque()
        self.pages = []
        self.respect_robots = respect_robots
        self.delay = delay
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.robot_parsers = {}
        self.headers = {
            'User-Agent': 'InternalLinkingSEOPro/1.0 (+https://example.com/bot)'
        }
        self.start_time = None
        self.end_time = None
        self.domain = None
        
    def is_allowed_by_robots(self, url):
        """Check if the URL is allowed by robots.txt"""
        if not self.respect_robots:
            return True
            
        parsed_url = urllib.parse.urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        if base_url not in self.robot_parsers:
            robots_url = f"{base_url}/robots.txt"
            parser = RobotFileParser()
            parser.set_url(robots_url)
            try:
                parser.read()
                self.robot_parsers[base_url] = parser
            except Exception as e:
                logger.warning(f"Error reading robots.txt for {base_url}: {e}")
                return True
        
        return self.robot_parsers[base_url].can_fetch(self.headers['User-Agent'], url)
    
    def is_valid_url(self, url, base_url):
        """Check if the URL is valid and belongs to the same domain"""
        try:
            # Parse the URL
            parsed = urllib.parse.urlparse(url)
            
            # If it's a relative URL, join it with the base URL
            if not parsed.netloc:
                url = urllib.parse.urljoin(base_url, url)
                parsed = urllib.parse.urlparse(url)
            
            # Check if it's the same domain
            if parsed.netloc != self.domain:
                return False
            
            # Skip URLs with fragments
            if parsed.fragment:
                url = url.split('#')[0]
            
            # Skip certain file types
            if any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip', '.css', '.js']):
                return False
                
            return url
        except Exception as e:
            logger.warning(f"Error validating URL {url}: {e}")
            return False
    
    def extract_links(self, soup, base_url):
        """Extract links from the page"""
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag.get('href', '').strip()
            if href and not href.startswith(('javascript:', 'mailto:', 'tel:')):
                valid_url = self.is_valid_url(href, base_url)
                if valid_url:
                    link_text = a_tag.get_text().strip()
                    links.append({
                        'url': valid_url,
                        'text': link_text if link_text else '[No Text]',
                        'source_url': base_url
                    })
        return links
    
    def extract_content(self, soup):
        """Extract main content from the page"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
        
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        
        # Remove blank lines
        content = '\n'.join(chunk for chunk in chunks if chunk)
        
        return content
    
    def extract_metadata(self, soup, url):
        """Extract metadata from the page"""
        metadata = {
            'url': url,
            'title': '',
            'description': '',
            'h1': '',
            'h2s': []
        }
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text().strip()
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            metadata['description'] = meta_desc.get('content', '').strip()
        
        # Extract H1
        h1_tag = soup.find('h1')
        if h1_tag:
            metadata['h1'] = h1_tag.get_text().strip()
        
        # Extract H2s
        h2_tags = soup.find_all('h2')
        metadata['h2s'] = [h2.get_text().strip() for h2 in h2_tags]
        
        return metadata
    
    def crawl_page(self, url, depth=0):
        """Crawl a single page and extract information"""
        if url in self.visited_urls or depth > self.max_depth:
            return None
        
        if not self.is_allowed_by_robots(url):
            logger.info(f"Skipping {url} (disallowed by robots.txt)")
            return None
        
        self.visited_urls.add(url)
        
        try:
            # Add delay to be respectful
            time.sleep(self.delay)
            
            # Fetch the page
            response = requests.get(url, headers=self.headers, timeout=10)
            
            # Check if the request was successful
            if response.status_code != 200:
                logger.warning(f"Failed to fetch {url}: HTTP {response.status_code}")
                return None
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract links
            links = self.extract_links(soup, url)
            
            # Extract content
            content = self.extract_content(soup)
            
            # Extract metadata
            metadata = self.extract_metadata(soup, url)
            
            # Create page object
            page = {
                'url': url,
                'domain': self.domain,
                'title': metadata['title'],
                'description': metadata['description'],
                'h1': metadata['h1'],
                'h2s': metadata['h2s'],
                'content': content,
                'links': links,
                'depth': depth,
                'crawled_at': datetime.now().isoformat()
            }
            
            # Add page to the list
            self.pages.append(page)
            
            # Add links to the queue
            for link in links:
                link_url = link['url']
                if link_url not in self.visited_urls:
                    self.urls_to_visit.append((link_url, depth + 1))
            
            logger.info(f"Crawled {url} (depth: {depth}, links: {len(links)})")
            return page
            
        except Exception as e:
            logger.error(f"Error crawling {url}: {e}")
            return None
    
    def crawl(self, start_url):
        """Start crawling from the given URL"""
        self.start_time = datetime.now()
        
        # Parse the domain from the start URL
        parsed_url = urllib.parse.urlparse(start_url)
        self.domain = parsed_url.netloc
        
        # Reset state
        self.visited_urls = set()
        self.urls_to_visit = deque([(start_url, 0)])  # (url, depth)
        self.pages = []
        
        logger.info(f"Starting crawl of {start_url}")
        
        # Crawl until we reach the maximum number of pages or run out of URLs
        while self.urls_to_visit and len(self.pages) < self.max_pages:
            url, depth = self.urls_to_visit.popleft()
            self.crawl_page(url, depth)
        
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        logger.info(f"Crawl completed: {len(self.pages)} pages in {duration:.2f} seconds")
        
        # Return crawl results
        return {
            'domain': self.domain,
            'start_url': start_url,
            'pages_indexed': len(self.pages),
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration': duration,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_pages_df(self):
        """Convert pages to a DataFrame"""
        if not self.pages:
            return pd.DataFrame()
        
        # Create a DataFrame with basic page info
        pages_df = pd.DataFrame([
            {
                'url': page['url'],
                'title': page['title'],
                'description': page['description'],
                'h1': page['h1'],
                'depth': page['depth'],
                'outgoing_links': len(page['links']),
                'crawled_at': page['crawled_at']
            }
            for page in self.pages
        ])
        
        return pages_df
    
    def get_links_df(self):
        """Convert links to a DataFrame"""
        if not self.pages:
            return pd.DataFrame()
        
        # Flatten the links from all pages
        all_links = []
        for page in self.pages:
            for link in page['links']:
                all_links.append({
                    'source_url': link['source_url'],
                    'target_url': link['url'],
                    'anchor_text': link['text']
                })
        
        return pd.DataFrame(all_links)
    
    def simulate_crawl(self, domain, num_pages=50):
        """Simulate a crawl for testing purposes"""
        self.start_time = datetime.now()
        self.domain = domain
        
        # Generate random pages
        for i in range(num_pages):
            if i == 0:
                url = f"https://{domain}/"
            else:
                # Create a realistic URL structure
                sections = ['about', 'services', 'blog', 'products', 'contact']
                if i <= len(sections):
                    url = f"https://{domain}/{sections[i-1]}/"
                else:
                    section = random.choice(sections)
                    slug = f"post-{i}" if section == 'blog' else f"item-{i}"
                    url = f"https://{domain}/{section}/{slug}/"
            
            # Generate page title
            if i == 0:
                title = f"Home - {domain}"
            else:
                words = ['SEO', 'Content', 'Marketing', 'Strategy', 'Analysis', 'Internal', 'Linking', 'Optimization']
                title = f"{random.choice(words)} {random.choice(words)} - {domain}"
            
            # Generate links (each page links to 3-8 other pages)
            links = []
            num_links = random.randint(3, 8)
            for j in range(num_links):
                target_index = random.randint(0, num_pages - 1)
                if target_index == 0:
                    target_url = f"https://{domain}/"
                else:
                    target_section = random.choice(sections)
                    target_slug = f"post-{target_index}" if target_section == 'blog' else f"item-{target_index}"
                    target_url = f"https://{domain}/{target_section}/{target_slug}/"
                
                link_text = f"Link to page {target_index}"
                links.append({
                    'url': target_url,
                    'text': link_text,
                    'source_url': url
                })
            
            # Create page object
            page = {
                'url': url,
                'domain': domain,
                'title': title,
                'description': f"This is a description for {url}",
                'h1': title,
                'h2s': [f"Section {j+1}" for j in range(random.randint(2, 5))],
                'content': f"This is the content for {url}. It contains information about {title}.",
                'links': links,
                'depth': min(i, self.max_depth),
                'crawled_at': datetime.now().isoformat()
            }
            
            self.pages.append(page)
            self.visited_urls.add(url)
        
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        # Return crawl results
        return {
            'domain': domain,
            'start_url': f"https://{domain}/",
            'pages_indexed': len(self.pages),
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'duration': duration,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
