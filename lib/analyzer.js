// analyzer.js - Content analysis module for Internal Linking SEO Pro

class ContentAnalyzer {
  constructor() {
    // Common stop words to filter out
    this.stopWords = new Set([
      'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'was', 'were',
      'be', 'been', 'being', 'in', 'on', 'at', 'to', 'for', 'with', 'by',
      'about', 'against', 'between', 'into', 'through', 'during', 'before',
      'after', 'above', 'below', 'from', 'up', 'down', 'of', 'off', 'over',
      'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
      'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more',
      'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
      'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just', 'should',
      'now', 'this', 'that', 'these', 'those'
    ]);
  }

  // Analyze page content and extract topics
  analyzeContent(content, options = {}) {
    const {
      maxTopics = 10,
      minWordLength = 3,
      minFrequency = 2,
      includeNgrams = true
    } = options;

    // Clean and tokenize the content
    const text = this.cleanText(content);
    const words = this.tokenize(text);

    // Count word frequencies
    const wordFrequency = this.countFrequency(words, minWordLength);

    // Extract n-grams if enabled
    let ngrams = {};
    if (includeNgrams) {
      const bigrams = this.extractNgrams(words, 2);
      const trigrams = this.extractNgrams(words, 3);
      ngrams = { ...bigrams, ...trigrams };
    }

    // Combine single words and n-grams
    const allTerms = { ...wordFrequency, ...ngrams };

    // Sort by frequency and get top terms
    const sortedTerms = Object.entries(allTerms)
      .filter(([term, count]) => count >= minFrequency)
      .sort((a, b) => b[1] - a[1])
      .slice(0, maxTopics);

    // Convert to topics array
    const topics = sortedTerms.map(([term, count]) => ({
      term,
      count,
      score: this.calculateTopicScore(term, count, sortedTerms)
    }));

    return topics;
  }

  // Clean text by removing HTML tags, special characters, etc.
  cleanText(text) {
    // Remove HTML tags
    let cleanedText = text.replace(/<[^>]*>/g, ' ');

    // Replace special characters with spaces
    cleanedText = cleanedText.replace(/[^a-zA-Z0-9 ]/g, ' ');

    // Replace multiple spaces with a single space
    cleanedText = cleanedText.replace(/\\s+/g, ' ');

    // Convert to lowercase
    cleanedText = cleanedText.toLowerCase();

    return cleanedText.trim();
  }

  // Tokenize text into words
  tokenize(text) {
    return text.split(' ')
      .filter(word => word.length > 0 && !this.stopWords.has(word));
  }

  // Count word frequencies
  countFrequency(words, minLength) {
    const frequency = {};

    words.forEach(word => {
      if (word.length >= minLength) {
        frequency[word] = (frequency[word] || 0) + 1;
      }
    });

    return frequency;
  }

  // Extract n-grams from words
  extractNgrams(words, n) {
    const ngrams = {};

    for (let i = 0; i <= words.length - n; i++) {
      const ngram = words.slice(i, i + n).join(' ');
      ngrams[ngram] = (ngrams[ngram] || 0) + 1;
    }

    return ngrams;
  }

  // Calculate topic score based on frequency and position
  calculateTopicScore(term, count, allTerms) {
    // Base score from frequency
    const maxCount = allTerms[0][1];
    const frequencyScore = count / maxCount;

    // Adjust score based on term length (longer terms often more specific)
    const lengthFactor = Math.min(1, term.length / 20);

    // Calculate final score (0-1 range)
    const score = (frequencyScore * 0.7) + (lengthFactor * 0.3);

    return Math.round(score * 100) / 100;
  }

  // Find potential link opportunities in text
  findLinkOpportunities(text, topics, existingLinks = []) {
    const opportunities = [];
    const cleanedText = this.cleanText(text);

    // Create a set of existing link texts (lowercase)
    const existingLinkTexts = new Set(
      existingLinks.map(link => link.text.toLowerCase())
    );

    // For each topic, find occurrences in the text
    topics.forEach(topic => {
      const term = topic.term;

      // Skip if this term is already linked
      if (existingLinkTexts.has(term)) {
        return;
      }

      // Find all occurrences of the term in the text
      const regex = new RegExp(`\\b${this.escapeRegExp(term)}\\b`, 'gi');
      let match;

      while ((match = regex.exec(cleanedText)) !== null) {
        opportunities.push({
          term,
          position: match.index,
          length: term.length,
          score: topic.score
        });
      }
    });

    // Sort by position
    opportunities.sort((a, b) => a.position - b.position);

    return opportunities;
  }

  // Escape special characters in string for use in regex
  escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');
  }

  // Extract entities (people, places, organizations) from text
  // This is a simplified version - in a real implementation, you would use an NLP library
  extractEntities(text) {
    // Placeholder for entity extraction
    // In a real implementation, this would use a proper NLP library
    return [];
  }

  // Find semantic relationships between topics
  findSemanticRelationships(topics) {
    const relationships = [];

    // Compare each pair of topics
    for (let i = 0; i < topics.length; i++) {
      for (let j = i + 1; j < topics.length; j++) {
        const topic1 = topics[i];
        const topic2 = topics[j];

        // Check if topics share words
        const words1 = topic1.term.split(' ');
        const words2 = topic2.term.split(' ');

        const sharedWords = words1.filter(word => words2.includes(word));

        if (sharedWords.length > 0) {
          relationships.push({
            topic1: topic1.term,
            topic2: topic2.term,
            relationship: 'related',
            strength: sharedWords.length / Math.max(words1.length, words2.length)
          });
        }
      }
    }

    return relationships;
  }
}

// Create and export the instance
const contentAnalyzer = new ContentAnalyzer();
export default contentAnalyzer;
