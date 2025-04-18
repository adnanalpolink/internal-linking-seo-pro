// content.js - Content script for Internal Linking SEO Pro

// Main state for the content script
const state = {
  isEnabled: false,
  sidebarVisible: false,
  pageContent: null,
  analyzedTopics: [],
  linkSuggestions: [],
  siteIndex: [],
  domainWhitelist: []
};

// Initialize when the content script loads
async function initialize() {
  console.log('Internal Linking SEO Pro content script initialized');

  // Get settings from storage
  const settings = await chrome.storage.local.get([
    'isEnabled',
    'domainWhitelist',
    'minInternalLinks'
  ]);

  state.isEnabled = settings.isEnabled !== false;
  state.domainWhitelist = settings.domainWhitelist || [];

  // Check if current domain is in whitelist
  const currentDomain = window.location.hostname;

  // For testing purposes, always allow localhost and file URLs
  const isLocalOrTestEnvironment = currentDomain === 'localhost' ||
                                  window.location.protocol === 'file:' ||
                                  !currentDomain;

  if (isLocalOrTestEnvironment || state.domainWhitelist.includes(currentDomain)) {
    // Get site index from background script
    await getSiteIndex();

    // Analyze current page content
    analyzePageContent();

    // Create UI elements
    createUI();
  }

  // Listen for messages from popup
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'analyzeCurrentPage') {
      console.log('Received analyzeCurrentPage message');

      // Force sidebar to be visible
      const sidebar = document.getElementById('ilsp-sidebar');
      if (sidebar) {
        state.sidebarVisible = true;
        sidebar.style.display = 'block';
      } else {
        // If sidebar doesn't exist yet, create it
        getSiteIndex()
          .then(() => {
            analyzePageContent();
            createUI();

            // Make sure sidebar is visible
            const newSidebar = document.getElementById('ilsp-sidebar');
            if (newSidebar) {
              state.sidebarVisible = true;
              newSidebar.style.display = 'block';
            }
          });
      }

      return true;
    }

    if (message.action === 'toggleExtension') {
      state.isEnabled = message.isEnabled;
      return true;
    }
  });
}

// Function to get site index from background script
async function getSiteIndex() {
  try {
    const response = await chrome.runtime.sendMessage({
      action: 'getPageIndex'
    });

    if (response.success) {
      state.siteIndex = response.data;
      console.log('Retrieved site index:', state.siteIndex);
    } else {
      console.error('Failed to get site index:', response.error);
    }
  } catch (error) {
    console.error('Error getting site index:', error);
  }
}

// Function to analyze page content using NLP techniques
function analyzePageContent() {
  console.log('Analyzing page content...');

  // Get main content (this is a simplified approach)
  const mainContent = document.body.innerText;
  state.pageContent = mainContent;

  // In a real implementation, we would use NLP libraries
  // For now, we'll use a simple keyword extraction approach
  const words = mainContent.toLowerCase().split(/\\W+/);
  const wordFrequency = {};

  words.forEach(word => {
    if (word.length > 3) {
      wordFrequency[word] = (wordFrequency[word] || 0) + 1;
    }
  });

  // Sort by frequency and get top keywords
  state.analyzedTopics = Object.entries(wordFrequency)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([word]) => word);

  console.log('Extracted topics:', state.analyzedTopics);

  // Generate link suggestions based on topics and site index
  generateLinkSuggestions();
}

// Function to generate link suggestions
function generateLinkSuggestions() {
  console.log('Generating link suggestions...');

  state.linkSuggestions = [];

  // Match topics with pages in the site index
  state.analyzedTopics.forEach(topic => {
    state.siteIndex.forEach(page => {
      if (page.topics.includes(topic) && !window.location.href.includes(page.url)) {
        // Calculate relevance score (simplified)
        const relevanceScore = 0.7 + (Math.random() * 0.3);

        state.linkSuggestions.push({
          keyword: topic,
          targetPage: page,
          relevanceScore: relevanceScore,
          topicMatch: topic
        });
      }
    });
  });

  // Sort by relevance score
  state.linkSuggestions.sort((a, b) => b.relevanceScore - a.relevanceScore);

  console.log('Generated suggestions:', state.linkSuggestions);
}

// Function to create UI elements
function createUI() {
  if (!state.isEnabled) return;

  console.log('Creating UI elements...');

  // Create sidebar
  createSidebar();

  // Add toggle button
  createToggleButton();

  // Highlight potential link opportunities
  highlightLinkOpportunities();
}

// Function to create sidebar
function createSidebar() {
  // Create sidebar container
  const sidebar = document.createElement('div');
  sidebar.id = 'ilsp-sidebar';
  sidebar.className = 'ilsp-sidebar';

  // Create sidebar header
  const header = document.createElement('div');
  header.className = 'ilsp-sidebar-header';
  header.innerHTML = '<h3>Internal Linking SEO Pro</h3>';

  // Create close button
  const closeButton = document.createElement('button');
  closeButton.className = 'ilsp-close-button';
  closeButton.innerHTML = '&times;';
  closeButton.addEventListener('click', toggleSidebar);
  header.appendChild(closeButton);

  // Create content container
  const content = document.createElement('div');
  content.className = 'ilsp-sidebar-content';

  // Add suggestions to content
  if (state.linkSuggestions.length > 0) {
    const suggestionsList = document.createElement('div');
    suggestionsList.className = 'ilsp-suggestions-list';

    state.linkSuggestions.forEach(suggestion => {
      const suggestionItem = document.createElement('div');
      suggestionItem.className = 'ilsp-suggestion-item';

      suggestionItem.innerHTML = `
        <div class="ilsp-suggestion-title">${suggestion.targetPage.title}</div>
        <div class="ilsp-suggestion-url">${suggestion.targetPage.url}</div>
        <div class="ilsp-suggestion-relevance">
          Relevance: <span class="ilsp-score">${Math.round(suggestion.relevanceScore * 100)}%</span>
        </div>
        <div class="ilsp-suggestion-match">
          Topic match: <span class="ilsp-match">${suggestion.topicMatch}</span>
        </div>
        <button class="ilsp-insert-link" data-url="${suggestion.targetPage.url}" data-title="${suggestion.targetPage.title}">
          Insert Link
        </button>
      `;

      suggestionsList.appendChild(suggestionItem);
    });

    content.appendChild(suggestionsList);
  } else {
    content.innerHTML = '<p>No link suggestions found for this page.</p>';
  }

  // Assemble sidebar
  sidebar.appendChild(header);
  sidebar.appendChild(content);

  // Add to page
  document.body.appendChild(sidebar);

  // Add event listeners for insert link buttons
  document.querySelectorAll('.ilsp-insert-link').forEach(button => {
    button.addEventListener('click', function() {
      const url = this.getAttribute('data-url');
      const title = this.getAttribute('data-title');
      insertLink(url, title);
    });
  });

  // Initially hide sidebar
  sidebar.style.display = 'none';
  state.sidebarVisible = false;
}

// Function to create toggle button
function createToggleButton() {
  const toggleButton = document.createElement('button');
  toggleButton.id = 'ilsp-toggle-button';
  toggleButton.className = 'ilsp-toggle-button';
  toggleButton.innerHTML = 'SEO';
  toggleButton.addEventListener('click', toggleSidebar);

  document.body.appendChild(toggleButton);
}

// Function to toggle sidebar visibility
function toggleSidebar() {
  const sidebar = document.getElementById('ilsp-sidebar');
  if (!sidebar) return;

  state.sidebarVisible = !state.sidebarVisible;
  sidebar.style.display = state.sidebarVisible ? 'block' : 'none';
}

// Function to highlight link opportunities in the page
function highlightLinkOpportunities() {
  if (state.linkSuggestions.length === 0) return;

  // Get all text nodes in the body
  const textNodes = [];
  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode: function(node) {
        // Skip nodes in our own UI elements
        if (node.parentElement &&
            (node.parentElement.id === 'ilsp-sidebar' ||
             node.parentElement.id === 'ilsp-toggle-button')) {
          return NodeFilter.FILTER_REJECT;
        }

        // Skip empty nodes or nodes with just whitespace
        if (node.nodeValue.trim() === '') {
          return NodeFilter.FILTER_REJECT;
        }

        return NodeFilter.FILTER_ACCEPT;
      }
    }
  );

  while (walker.nextNode()) {
    textNodes.push(walker.currentNode);
  }

  // For each suggestion, find and highlight matching text
  state.linkSuggestions.forEach(suggestion => {
    const keyword = suggestion.keyword;
    const regex = new RegExp(`\\b${keyword}\\b`, 'gi');

    textNodes.forEach(textNode => {
      const text = textNode.nodeValue;
      if (regex.test(text)) {
        // Reset regex
        regex.lastIndex = 0;

        // Split text by keyword
        const fragments = text.split(regex);
        if (fragments.length === 1) return; // No match found

        // Create a document fragment to hold the new nodes
        const fragment = document.createDocumentFragment();

        // Rebuild the text with highlights
        for (let i = 0; i < fragments.length; i++) {
          // Add text fragment
          fragment.appendChild(document.createTextNode(fragments[i]));

          // Add highlighted keyword (except after the last fragment)
          if (i < fragments.length - 1) {
            const match = text.match(regex)[i];
            regex.lastIndex = 0; // Reset regex

            const highlight = document.createElement('span');
            highlight.className = 'ilsp-highlight';
            highlight.textContent = match;
            highlight.dataset.url = suggestion.targetPage.url;
            highlight.dataset.title = suggestion.targetPage.title;
            highlight.dataset.relevance = suggestion.relevanceScore;

            // Add click event to insert link
            highlight.addEventListener('click', function() {
              insertLink(this.dataset.url, this.dataset.title, this);
            });

            fragment.appendChild(highlight);
          }
        }

        // Replace the original text node with the fragment
        textNode.parentNode.replaceChild(fragment, textNode);
      }
    });
  });
}

// Function to insert a link
function insertLink(url, title, element) {
  if (!element) {
    // If no element is provided, use the currently selected text
    const selection = window.getSelection();
    if (!selection.rangeCount) return;

    const range = selection.getRangeAt(0);
    const link = document.createElement('a');
    link.href = url;
    link.title = title;
    link.className = 'ilsp-inserted-link';

    try {
      range.surroundContents(link);
      selection.removeAllRanges();
    } catch (e) {
      console.error('Could not insert link:', e);
    }
  } else {
    // If an element is provided (from highlight click)
    const link = document.createElement('a');
    link.href = url;
    link.title = title;
    link.className = 'ilsp-inserted-link';
    link.textContent = element.textContent;

    element.parentNode.replaceChild(link, element);
  }
}

// Initialize the content script
initialize();
