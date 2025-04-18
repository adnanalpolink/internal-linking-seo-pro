// suggestionEngine.js - Link suggestion engine for Internal Linking SEO Pro

import indexDBManager from './indexDB.js';
import contentAnalyzer from './analyzer.js';

class SuggestionEngine {
  constructor() {
    this.currentPageUrl = '';
    this.currentPageTopics = [];
    this.siteIndex = [];
  }

  // Initialize the suggestion engine
  async init() {
    // Initialize IndexedDB
    await indexDBManager.init();
  }

  // Generate link suggestions for the current page
  async generateSuggestions(pageUrl, pageContent, options = {}) {
    try {
      this.currentPageUrl = pageUrl;

      // Get domain from URL
      const domain = this.extractDomain(pageUrl);

      // Analyze page content
      this.currentPageTopics = contentAnalyzer.analyzeContent(pageContent, {
        maxTopics: options.maxTopics || 15,
        minWordLength: options.minWordLength || 3,
        minFrequency: options.minFrequency || 2
      });

      // Get pages from the site index
      this.siteIndex = await indexDBManager.getPagesByDomain(domain);

      // Generate suggestions
      const suggestions = this.matchTopicsToPages();

      // Sort by relevance
      suggestions.sort((a, b) => b.relevanceScore - a.relevanceScore);

      return suggestions;
    } catch (error) {
      console.error('Error generating suggestions:', error);
      throw error;
    }
  }

  // Match topics to pages in the site index
  matchTopicsToPages() {
    const suggestions = [];
    const currentUrl = this.currentPageUrl;

    // For each topic, find matching pages
    this.currentPageTopics.forEach(topic => {
      const term = topic.term;

      // Find pages that contain this topic
      const matchingPages = this.siteIndex.filter(page => {
        // Skip the current page
        if (page.url === currentUrl) {
          return false;
        }

        // Check if page topics include this term
        return page.topics && page.topics.some(pageTopic => {
          return pageTopic.toLowerCase().includes(term.toLowerCase()) ||
                 term.toLowerCase().includes(pageTopic.toLowerCase());
        });
      });

      // For each matching page, create a suggestion
      matchingPages.forEach(page => {
        // Calculate relevance score
        const relevanceScore = this.calculateRelevanceScore(topic, page);

        // Find matching topic from the page
        const matchingTopic = page.topics.find(pageTopic =>
          pageTopic.toLowerCase().includes(term.toLowerCase()) ||
          term.toLowerCase().includes(pageTopic.toLowerCase())
        );

        suggestions.push({
          keyword: term,
          targetPage: page,
          relevanceScore,
          topicMatch: matchingTopic || term
        });
      });
    });

    // Remove duplicates (same target page)
    const uniqueSuggestions = [];
    const seenUrls = new Set();

    suggestions.forEach(suggestion => {
      if (!seenUrls.has(suggestion.targetPage.url)) {
        seenUrls.add(suggestion.targetPage.url);
        uniqueSuggestions.push(suggestion);
      }
    });

    return uniqueSuggestions;
  }

  // Calculate relevance score between a topic and a page
  calculateRelevanceScore(topic, page) {
    // Base score from topic score
    let score = topic.score;

    // Adjust based on exact match vs partial match
    const exactMatch = page.topics.includes(topic.term);
    if (exactMatch) {
      score *= 1.2; // Boost for exact match
    }

    // Adjust based on page title match
    if (page.title && page.title.toLowerCase().includes(topic.term.toLowerCase())) {
      score *= 1.1; // Boost for title match
    }

    // Normalize to 0-1 range
    return Math.min(1, Math.max(0, score));
  }

  // Extract domain from URL
  extractDomain(url) {
    try {
      const urlObj = new URL(url);
      return urlObj.hostname;
    } catch (error) {
      console.error('Error extracting domain:', error);
      return '';
    }
  }

  // Get orphaned content recommendations
  async getOrphanedContentRecommendations(domain) {
    try {
      // Get orphaned pages
      const orphanedPages = await indexDBManager.getOrphanedPages(domain);

      // Get all pages
      const allPages = await indexDBManager.getPagesByDomain(domain);

      // Generate recommendations
      const recommendations = [];

      orphanedPages.forEach(orphanedPage => {
        // Find potential linking pages
        const potentialLinkingPages = allPages.filter(page => {
          // Skip the orphaned page itself
          if (page.url === orphanedPage.url) {
            return false;
          }

          // Check for topic overlap
          return page.topics && orphanedPage.topics &&
                 page.topics.some(topic => orphanedPage.topics.includes(topic));
        });

        // Sort by topic relevance
        potentialLinkingPages.sort((a, b) => {
          const aOverlap = a.topics.filter(topic => orphanedPage.topics.includes(topic)).length;
          const bOverlap = b.topics.filter(topic => orphanedPage.topics.includes(topic)).length;
          return bOverlap - aOverlap;
        });

        // Take top 3 recommendations
        const topRecommendations = potentialLinkingPages.slice(0, 3);

        recommendations.push({
          orphanedPage,
          recommendedLinkingPages: topRecommendations
        });
      });

      return recommendations;
    } catch (error) {
      console.error('Error getting orphaned content recommendations:', error);
      throw error;
    }
  }

  // Get topic cluster recommendations
  async getTopicClusterRecommendations() {
    try {
      // Get topic clusters
      const clusters = await indexDBManager.getTopicClusters();

      // Generate recommendations
      const recommendations = [];

      clusters.forEach(cluster => {
        const { pillar, pages } = cluster;

        // Check links from cluster pages to pillar
        const linksToPillar = [];
        const linksFromPillar = [];

        // In a real implementation, we would check actual links
        // For now, we'll simulate this

        // Generate recommendations for missing links
        const missingLinksToPillar = pages.filter(page => !linksToPillar.includes(page.url));
        const missingLinksFromPillar = pages.filter(page => !linksFromPillar.includes(page.url));

        recommendations.push({
          pillar,
          clusterPages: pages,
          missingLinksToPillar,
          missingLinksFromPillar
        });
      });

      return recommendations;
    } catch (error) {
      console.error('Error getting topic cluster recommendations:', error);
      throw error;
    }
  }
}

// Create and export the instance
const suggestionEngine = new SuggestionEngine();
export default suggestionEngine;
