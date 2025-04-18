// popup.js - Popup script for Internal Linking SEO Pro

document.addEventListener('DOMContentLoaded', async function() {
  // Get DOM elements
  const enableToggle = document.getElementById('enableToggle');
  const startCrawlBtn = document.getElementById('startCrawlBtn');
  const analyzePageBtn = document.getElementById('analyzePageBtn');
  const settingsBtn = document.getElementById('settingsBtn');
  const pagesIndexedEl = document.getElementById('pagesIndexed');
  const orphanedPagesEl = document.getElementById('orphanedPages');
  const lastCrawlDateEl = document.getElementById('lastCrawlDate');
  const loadingEl = document.getElementById('loading');
  const mainContentEl = document.getElementById('mainContent');

  // Load settings and stats
  await loadData();

  // Add event listeners
  enableToggle.addEventListener('change', toggleExtension);
  startCrawlBtn.addEventListener('click', startCrawl);
  analyzePageBtn.addEventListener('click', analyzeCurrentPage);
  settingsBtn.addEventListener('click', openSettings);

  // Function to load data
  async function loadData() {
    try {
      // Get settings and stats from storage
      const data = await chrome.storage.local.get([
        'isEnabled',
        'lastCrawlDate',
        'siteStats'
      ]);

      // Update UI
      enableToggle.checked = data.isEnabled !== false;

      if (data.lastCrawlDate) {
        const date = new Date(data.lastCrawlDate);
        lastCrawlDateEl.textContent = date.toLocaleString();
      } else {
        lastCrawlDateEl.textContent = 'Never';
      }

      if (data.siteStats) {
        pagesIndexedEl.textContent = data.siteStats.pagesIndexed || 0;
        orphanedPagesEl.textContent = data.siteStats.orphanedPages || 0;
      }

      // Hide loading, show content
      loadingEl.style.display = 'none';
      mainContentEl.style.display = 'block';
    } catch (error) {
      console.error('Error loading data:', error);
    }
  }

  // Function to toggle extension
  async function toggleExtension() {
    try {
      await chrome.storage.local.set({ isEnabled: enableToggle.checked });

      // Notify content script about the change
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tab) {
        chrome.tabs.sendMessage(tab.id, { action: 'toggleExtension', isEnabled: enableToggle.checked });
      }
    } catch (error) {
      console.error('Error toggling extension:', error);
    }
  }

  // Function to start crawl
  async function startCrawl() {
    try {
      startCrawlBtn.disabled = true;
      startCrawlBtn.textContent = 'Crawling...';

      // Get current domain
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab) {
        throw new Error('No active tab found');
      }

      const url = new URL(tab.url);
      const domain = url.hostname;

      // Get crawl depth from settings
      const { crawlDepth } = await chrome.storage.local.get('crawlDepth');

      // Send message to background script
      const response = await chrome.runtime.sendMessage({
        action: 'startCrawl',
        domain: domain,
        depth: crawlDepth || 3
      });

      if (response.success) {
        // Update UI with new data
        await loadData();
      } else {
        console.error('Crawl failed:', response.error);
      }
    } catch (error) {
      console.error('Error starting crawl:', error);
    } finally {
      startCrawlBtn.disabled = false;
      startCrawlBtn.textContent = 'Start Site Crawl';
    }
  }

  // Function to analyze current page
  async function analyzeCurrentPage() {
    try {
      // Show loading state
      analyzePageBtn.disabled = true;
      analyzePageBtn.textContent = 'Analyzing...';

      // Get current tab
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab) {
        throw new Error('No active tab found');
      }

      // Send message to content script
      chrome.tabs.sendMessage(tab.id, { action: 'analyzeCurrentPage' }, response => {
        // Handle response if needed
        if (chrome.runtime.lastError) {
          console.warn('Could not send message to content script:', chrome.runtime.lastError);

          // The content script might not be loaded yet, so inject it
          chrome.scripting.executeScript({
            target: { tabId: tab.id },
            files: ['content.js']
          }).then(() => {
            // Try sending the message again after a short delay
            setTimeout(() => {
              chrome.tabs.sendMessage(tab.id, { action: 'analyzeCurrentPage' });
              // Close popup
              window.close();
            }, 500);
          }).catch(err => {
            console.error('Error injecting content script:', err);
            analyzePageBtn.disabled = false;
            analyzePageBtn.textContent = 'Analyze Current Page';
          });
          return;
        }

        // Close popup if message was sent successfully
        window.close();
      });
    } catch (error) {
      console.error('Error analyzing page:', error);
      analyzePageBtn.disabled = false;
      analyzePageBtn.textContent = 'Analyze Current Page';
    }
  }

  // Function to open settings
  function openSettings() {
    chrome.runtime.openOptionsPage();
  }
});
