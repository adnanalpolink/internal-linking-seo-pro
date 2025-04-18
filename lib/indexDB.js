// indexDB.js - IndexedDB management for Internal Linking SEO Pro

class IndexDBManager {
  constructor() {
    this.dbName = 'InternalLinkingSEOPro';
    this.dbVersion = 1;
    this.db = null;
  }

  // Initialize the database
  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);

      request.onerror = event => {
        console.error('IndexedDB error:', event.target.error);
        reject(event.target.error);
      };

      request.onsuccess = event => {
        this.db = event.target.result;
        console.log('IndexedDB connected successfully');
        resolve();
      };

      request.onupgradeneeded = event => {
        const db = event.target.result;

        // Create pages store
        if (!db.objectStoreNames.contains('pages')) {
          const pagesStore = db.createObjectStore('pages', { keyPath: 'url' });
          pagesStore.createIndex('domain', 'domain', { unique: false });
          pagesStore.createIndex('lastUpdated', 'lastUpdated', { unique: false });
        }

        // Create topics store
        if (!db.objectStoreNames.contains('topics')) {
          const topicsStore = db.createObjectStore('topics', { keyPath: 'id', autoIncrement: true });
          topicsStore.createIndex('name', 'name', { unique: true });
        }

        // Create links store
        if (!db.objectStoreNames.contains('links')) {
          const linksStore = db.createObjectStore('links', { keyPath: 'id', autoIncrement: true });
          linksStore.createIndex('sourceUrl', 'sourceUrl', { unique: false });
          linksStore.createIndex('targetUrl', 'targetUrl', { unique: false });
        }
      };
    });
  }

  // Add or update a page
  async savePage(page) {
    return new Promise((resolve, reject) => {
      if (!this.db) {
        reject(new Error('Database not initialized'));
        return;
      }

      const transaction = this.db.transaction(['pages'], 'readwrite');
      const store = transaction.objectStore('pages');

      // Add timestamp
      page.lastUpdated = new Date().toISOString();

      const request = store.put(page);

      request.onerror = event => {
        console.error('Error saving page:', event.target.error);
        reject(event.target.error);
      };

      request.onsuccess = event => {
        resolve(event.target.result);
      };
    });
  }

  // Get a page by URL
  async getPage(url) {
    return new Promise((resolve, reject) => {
      if (!this.db) {
        reject(new Error('Database not initialized'));
        return;
      }

      const transaction = this.db.transaction(['pages'], 'readonly');
      const store = transaction.objectStore('pages');
      const request = store.get(url);

      request.onerror = event => {
        console.error('Error getting page:', event.target.error);
        reject(event.target.error);
      };

      request.onsuccess = event => {
        resolve(event.target.result);
      };
    });
  }

  // Get all pages for a domain
  async getPagesByDomain(domain) {
    return new Promise((resolve, reject) => {
      if (!this.db) {
        reject(new Error('Database not initialized'));
        return;
      }

      const transaction = this.db.transaction(['pages'], 'readonly');
      const store = transaction.objectStore('pages');
      const index = store.index('domain');
      const request = index.getAll(domain);

      request.onerror = event => {
        console.error('Error getting pages by domain:', event.target.error);
        reject(event.target.error);
      };

      request.onsuccess = event => {
        resolve(event.target.result);
      };
    });
  }

  // Delete a page
  async deletePage(url) {
    return new Promise((resolve, reject) => {
      if (!this.db) {
        reject(new Error('Database not initialized'));
        return;
      }

      const transaction = this.db.transaction(['pages'], 'readwrite');
      const store = transaction.objectStore('pages');
      const request = store.delete(url);

      request.onerror = event => {
        console.error('Error deleting page:', event.target.error);
        reject(event.target.error);
      };

      request.onsuccess = event => {
        resolve();
      };
    });
  }

  // Add a link
  async saveLink(link) {
    return new Promise((resolve, reject) => {
      if (!this.db) {
        reject(new Error('Database not initialized'));
        return;
      }

      const transaction = this.db.transaction(['links'], 'readwrite');
      const store = transaction.objectStore('links');

      // Add timestamp
      link.createdAt = new Date().toISOString();

      const request = store.add(link);

      request.onerror = event => {
        console.error('Error saving link:', event.target.error);
        reject(event.target.error);
      };

      request.onsuccess = event => {
        resolve(event.target.result);
      };
    });
  }

  // Get all links for a source URL
  async getLinksBySource(sourceUrl) {
    return new Promise((resolve, reject) => {
      if (!this.db) {
        reject(new Error('Database not initialized'));
        return;
      }

      const transaction = this.db.transaction(['links'], 'readonly');
      const store = transaction.objectStore('links');
      const index = store.index('sourceUrl');
      const request = index.getAll(sourceUrl);

      request.onerror = event => {
        console.error('Error getting links by source:', event.target.error);
        reject(event.target.error);
      };

      request.onsuccess = event => {
        resolve(event.target.result);
      };
    });
  }

  // Get all links for a target URL
  async getLinksByTarget(targetUrl) {
    return new Promise((resolve, reject) => {
      if (!this.db) {
        reject(new Error('Database not initialized'));
        return;
      }

      const transaction = this.db.transaction(['links'], 'readonly');
      const store = transaction.objectStore('links');
      const index = store.index('targetUrl');
      const request = index.getAll(targetUrl);

      request.onerror = event => {
        console.error('Error getting links by target:', event.target.error);
        reject(event.target.error);
      };

      request.onsuccess = event => {
        resolve(event.target.result);
      };
    });
  }

  // Get orphaned pages (pages with fewer than minLinks incoming links)
  async getOrphanedPages(domain, minLinks = 3) {
    try {
      // Get all pages for the domain
      const pages = await this.getPagesByDomain(domain);
      const orphanedPages = [];

      // For each page, count incoming links
      for (const page of pages) {
        const incomingLinks = await this.getLinksByTarget(page.url);

        if (incomingLinks.length < minLinks) {
          orphanedPages.push({
            ...page,
            incomingLinksCount: incomingLinks.length
          });
        }
      }

      return orphanedPages;
    } catch (error) {
      console.error('Error getting orphaned pages:', error);
      throw error;
    }
  }

  // Get topic clusters
  async getTopicClusters() {
    try {
      // Get pillar pages from storage
      const { pillarPages = [] } = await chrome.storage.local.get('pillarPages');
      const clusters = [];

      // For each pillar page, find related pages
      for (const pillar of pillarPages) {
        const transaction = this.db.transaction(['pages'], 'readonly');
        const store = transaction.objectStore('pages');
        const allPages = await new Promise((resolve, reject) => {
          const request = store.getAll();
          request.onerror = event => reject(event.target.error);
          request.onsuccess = event => resolve(event.target.result);
        });

        // Filter pages that match the pillar topic
        const clusterPages = allPages.filter(page => {
          return page.topics && page.topics.includes(pillar.topic) && page.url !== pillar.url;
        });

        clusters.push({
          pillar,
          pages: clusterPages
        });
      }

      return clusters;
    } catch (error) {
      console.error('Error getting topic clusters:', error);
      throw error;
    }
  }

  // Clear all data
  async clearAll() {
    return new Promise((resolve, reject) => {
      if (!this.db) {
        reject(new Error('Database not initialized'));
        return;
      }

      const transaction = this.db.transaction(['pages', 'topics', 'links'], 'readwrite');
      const pagesStore = transaction.objectStore('pages');
      const topicsStore = transaction.objectStore('topics');
      const linksStore = transaction.objectStore('links');

      pagesStore.clear();
      topicsStore.clear();
      linksStore.clear();

      transaction.oncomplete = () => {
        console.log('Database cleared successfully');
        resolve();
      };

      transaction.onerror = event => {
        console.error('Error clearing database:', event.target.error);
        reject(event.target.error);
      };
    });
  }
}

// Create and export the instance
const indexDBManager = new IndexDBManager();
export default indexDBManager;
