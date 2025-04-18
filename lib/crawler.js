// crawler.js - Site crawling functionality for Internal Linking SEO Pro

import indexDBManager from './indexDB.js';
import contentAnalyzer from './analyzer.js';

class SiteCrawler {
  constructor() {
    this.crawlQueue = [];
    this.visitedUrls = new Set();
    this.domain = '';
    this.maxDepth = 3;
    this.currentDepth = 0;
    this.crawlStats = {
      totalPages: 0,
      successfulPages: 0,
      failedPages: 0,
      startTime: null,
      endTime: null
    };
    this.isCrawling = false;
  }

  // Initialize the crawler
  async init() {
    // Initialize IndexedDB
    await indexDBManager.init();
  }

  // Start crawling a site
  async crawlSite(domain, options = {}) {
    if (this.isCrawling) {
      throw new Error('Crawl already in progress');
    }

    this.isCrawling = true;
    this.domain = domain;
    this.maxDepth = options.maxDepth || 3;
    this.crawlQueue = [];
    this.visitedUrls = new Set();
    this.currentDepth = 0;

    // Reset stats
    this.crawlStats = {
      totalPages: 0,
      successfulPages: 0,
      failedPages: 0,
      startTime: new Date(),
      endTime: null
    };

    try {
      // Start with the homepage
      const startUrl = `https://${domain}`;
      this.crawlQueue.push({ url: startUrl, depth: 0 });

      // Process the queue
      await this.processQueue();

      // Update stats
      this.crawlStats.endTime = new Date();

      // Save crawl stats
      await this.saveCrawlStats();

      this.isCrawling = false;
      return this.crawlStats;
    } catch (error) {
      this.isCrawling = false;
      console.error('Crawl error:', error);
      throw error;
    }
  }

  // Process the crawl queue
  async processQueue() {
    while (this.crawlQueue.length > 0) {
      const { url, depth } = this.crawlQueue.shift();

      // Skip if already visited
      if (this.visitedUrls.has(url)) {
        continue;
      }

      // Skip if beyond max depth
      if (depth > this.maxDepth) {
        continue;
      }

      // Mark as visited
      this.visitedUrls.add(url);

      try {
        // Crawl the page
        const pageData = await this.crawlPage(url);

        // Save page to database
        await indexDBManager.savePage(pageData);

        // Extract links and add to queue
        if (depth < this.maxDepth) {
          pageData.links.forEach(link => {
            // Only add links from the same domain
            if (this.isSameDomain(link.url)) {
              this.crawlQueue.push({ url: link.url, depth: depth + 1 });
            }
          });
        }

        this.crawlStats.successfulPages++;
      } catch (error) {
        console.error(`Error crawling ${url}:`, error);
        this.crawlStats.failedPages++;
      }

      this.crawlStats.totalPages++;

      // Emit progress update
      this.emitProgress();
    }
  }

  // Crawl a single page
  async crawlPage(url) {
    console.log(`Crawling: ${url}`);

    // In a real extension, we would use the Fetch API to get the page content
    // For this example, we'll simulate the crawl

    // Simulate fetch delay
    await new Promise(resolve => setTimeout(resolve, 100));

    // Generate a more realistic page number for the URL
    const pageNumber = this.visitedUrls.size;

    // Create a mock page object
    const pageData = {
      url,
      domain: this.domain,
      title: `${this.getSampleTitle(pageNumber)} - ${this.domain}`,
      description: `This is a page about ${this.getSampleTopic(pageNumber)} with information on SEO best practices.`,
      content: this.getSampleContent(pageNumber),
      links: this.generateMockLinks(url, 5 + Math.floor(Math.random() * 5)),
      topics: this.generateMockTopics(),
      lastCrawled: new Date().toISOString()
    };

    return pageData;
  }

  // Generate sample title based on page number
  getSampleTitle(pageNumber) {
    const titles = [
      'Ultimate Guide to Internal Linking',
      'SEO Best Practices for 2023',
      'How to Improve Your Site Structure',
      'Content Marketing Strategies',
      'Technical SEO Checklist',
      'Link Building Techniques',
      'On-Page SEO Factors',
      'Keyword Research Guide',
      'SEO Audit Process',
      'Mobile Optimization Tips',
      'Local SEO Strategies',
      'E-commerce SEO Guide',
      'Voice Search Optimization',
      'SEO for Beginners',
      'Advanced SEO Techniques'
    ];

    return titles[pageNumber % titles.length];
  }

  // Generate sample topic based on page number
  getSampleTopic(pageNumber) {
    const topics = [
      'internal linking',
      'SEO',
      'site structure',
      'content marketing',
      'technical SEO',
      'link building',
      'on-page optimization',
      'keyword research',
      'SEO audits',
      'mobile optimization'
    ];

    return topics[pageNumber % topics.length];
  }

  // Generate sample content
  getSampleContent(pageNumber) {
    const topic = this.getSampleTopic(pageNumber);
    return `This is a comprehensive guide about ${topic}. It contains detailed information about best practices, strategies, and techniques to improve your website's performance. The page discusses various aspects of ${topic} including implementation, measurement, and optimization. It also covers related topics such as SEO, content marketing, and site structure.`;
  }

  // Generate mock links for simulation
  generateMockLinks(sourceUrl, count) {
    const links = [];

    for (let i = 0; i < count; i++) {
      // Create a more structured approach to generating URLs
      let targetUrl;
      if (i < 3) {
        // Some links to main pages
        const mainPages = ['about', 'services', 'blog', 'contact', 'products'];
        targetUrl = `https://${this.domain}/${mainPages[i % mainPages.length]}`;
      } else {
        // Some links to blog or content pages
        const topics = ['seo', 'marketing', 'content', 'technical', 'guide'];
        const randomTopic = topics[Math.floor(Math.random() * topics.length)];
        const randomNumber = Math.floor(Math.random() * 20);
        targetUrl = `https://${this.domain}/blog/${randomTopic}-tips-${randomNumber}`;
      }

      links.push({
        sourceUrl,
        targetUrl,
        text: `Link to ${targetUrl.split('/').pop().replace(/-/g, ' ')}`,
        isInternal: true
      });
    }

    return links;
  }

  // Generate mock topics for simulation
  generateMockTopics() {
    const allTopics = [
      'seo', 'internal linking', 'content marketing', 'search engine optimization',
      'link building', 'site structure', 'content strategy', 'keyword research',
      'on-page seo', 'technical seo', 'backlinks', 'anchor text'
    ];

    // Randomly select 3-5 topics
    const count = 3 + Math.floor(Math.random() * 3);
    const topics = [];

    for (let i = 0; i < count; i++) {
      const randomIndex = Math.floor(Math.random() * allTopics.length);
      topics.push(allTopics[randomIndex]);
    }

    return [...new Set(topics)]; // Remove duplicates
  }

  // Check if a URL is from the same domain
  isSameDomain(url) {
    try {
      const urlObj = new URL(url);
      return urlObj.hostname === this.domain || urlObj.hostname === `www.${this.domain}`;
    } catch (error) {
      return false;
    }
  }

  // Emit progress update
  emitProgress() {
    // In a real extension, this would emit an event to update the UI
    console.log(`Crawl progress: ${this.crawlStats.totalPages} pages processed`);
  }

  // Save crawl stats
  async saveCrawlStats() {
    try {
      // Calculate duration
      const duration = (this.crawlStats.endTime - this.crawlStats.startTime) / 1000;

      const stats = {
        domain: this.domain,
        totalPages: this.crawlStats.totalPages,
        successfulPages: this.crawlStats.successfulPages,
        failedPages: this.crawlStats.failedPages,
        duration,
        date: new Date().toISOString()
      };

      // Save to storage
      await chrome.storage.local.set({
        lastCrawlDate: stats.date,
        lastCrawlStats: stats
      });

      // Update site stats
      const orphanedPages = await indexDBManager.getOrphanedPages(this.domain);

      await chrome.storage.local.set({
        siteStats: {
          pagesIndexed: this.crawlStats.successfulPages,
          orphanedPages: orphanedPages.length
        }
      });

      console.log('Crawl stats saved:', stats);
    } catch (error) {
      console.error('Error saving crawl stats:', error);
    }
  }

  // Stop the current crawl
  stopCrawl() {
    if (this.isCrawling) {
      this.crawlQueue = [];
      this.isCrawling = false;
      this.crawlStats.endTime = new Date();
      console.log('Crawl stopped manually');
    }
  }
}

// Create and export the instance
const siteCrawler = new SiteCrawler();
export default siteCrawler;
