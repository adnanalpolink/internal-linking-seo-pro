// options.js - Settings page script for Internal Linking SEO Pro

document.addEventListener('DOMContentLoaded', async function() {
  // Get DOM elements
  const domainInput = document.getElementById('domainInput');
  const addDomainBtn = document.getElementById('addDomainBtn');
  const domainList = document.getElementById('domainList');
  const crawlFrequency = document.getElementById('crawlFrequency');
  const crawlDepth = document.getElementById('crawlDepth');
  const minInternalLinks = document.getElementById('minInternalLinks');
  const pillarUrlInput = document.getElementById('pillarUrlInput');
  const pillarTopicInput = document.getElementById('pillarTopicInput');
  const addPillarBtn = document.getElementById('addPillarBtn');
  const pillarPagesList = document.getElementById('pillarPagesList');
  const resetBtn = document.getElementById('resetBtn');
  const saveBtn = document.getElementById('saveBtn');
  const statusMessage = document.getElementById('statusMessage');

  // Load settings
  await loadSettings();

  // Add event listeners
  addDomainBtn.addEventListener('click', addDomain);
  addPillarBtn.addEventListener('click', addPillarPage);
  resetBtn.addEventListener('click', resetSettings);
  saveBtn.addEventListener('click', saveSettings);

  // Function to load settings
  async function loadSettings() {
    try {
      // Get settings from storage
      const settings = await chrome.storage.local.get([
        'domainWhitelist',
        'crawlFrequency',
        'crawlDepth',
        'minInternalLinks',
        'pillarPages'
      ]);

      // Update UI
      if (settings.domainWhitelist) {
        renderDomainList(settings.domainWhitelist);
      }

      if (settings.crawlFrequency) {
        crawlFrequency.value = settings.crawlFrequency;
      }

      if (settings.crawlDepth) {
        crawlDepth.value = settings.crawlDepth;
      }

      if (settings.minInternalLinks) {
        minInternalLinks.value = settings.minInternalLinks;
      }

      if (settings.pillarPages) {
        renderPillarPages(settings.pillarPages);
      }
    } catch (error) {
      console.error('Error loading settings:', error);
      showStatus('Error loading settings: ' + error.message, 'error');
    }
  }

  // Function to render domain list
  function renderDomainList(domains) {
    domainList.innerHTML = '';

    if (domains.length === 0) {
      domainList.innerHTML = '<div style="color: #5f6368; padding: 10px;">No domains added yet.</div>';
      return;
    }

    domains.forEach(domain => {
      const domainItem = document.createElement('div');
      domainItem.className = 'domain-item';

      domainItem.innerHTML = `
        <span>${domain}</span>
        <button class="remove-domain" data-domain="${domain}">Remove</button>
      `;

      domainList.appendChild(domainItem);
    });

    // Add event listeners to remove buttons
    document.querySelectorAll('.remove-domain').forEach(button => {
      button.addEventListener('click', function() {
        removeDomain(this.getAttribute('data-domain'));
      });
    });
  }

  // Function to render pillar pages
  function renderPillarPages(pillarPages) {
    pillarPagesList.innerHTML = '';

    if (pillarPages.length === 0) {
      pillarPagesList.innerHTML = '<div style="color: #5f6368; padding: 10px;">No pillar pages added yet.</div>';
      return;
    }

    pillarPages.forEach(page => {
      const pillarItem = document.createElement('div');
      pillarItem.className = 'pillar-item';

      pillarItem.innerHTML = `
        <span class="url">${page.url}</span>
        <span class="topic">${page.topic}</span>
        <button class="remove-pillar" data-url="${page.url}">Remove</button>
      `;

      pillarPagesList.appendChild(pillarItem);
    });

    // Add event listeners to remove buttons
    document.querySelectorAll('.remove-pillar').forEach(button => {
      button.addEventListener('click', function() {
        removePillarPage(this.getAttribute('data-url'));
      });
    });
  }

  // Function to add domain
  async function addDomain() {
    try {
      const domain = domainInput.value.trim();

      if (!domain) {
        showStatus('Please enter a domain', 'error');
        return;
      }

      // Validate domain format
      if (!isValidDomain(domain)) {
        showStatus('Please enter a valid domain (e.g., example.com)', 'error');
        return;
      }

      // Get current domains
      const { domainWhitelist = [] } = await chrome.storage.local.get('domainWhitelist');

      // Check if domain already exists
      if (domainWhitelist.includes(domain)) {
        showStatus('Domain already exists', 'error');
        return;
      }

      // Add domain
      const newDomainList = [...domainWhitelist, domain];
      await chrome.storage.local.set({ domainWhitelist: newDomainList });

      // Update UI
      renderDomainList(newDomainList);
      domainInput.value = '';

      showStatus('Domain added successfully', 'success');
    } catch (error) {
      console.error('Error adding domain:', error);
      showStatus('Error adding domain: ' + error.message, 'error');
    }
  }

  // Function to remove domain
  async function removeDomain(domain) {
    try {
      // Get current domains
      const { domainWhitelist = [] } = await chrome.storage.local.get('domainWhitelist');

      // Remove domain
      const newDomainList = domainWhitelist.filter(d => d !== domain);
      await chrome.storage.local.set({ domainWhitelist: newDomainList });

      // Update UI
      renderDomainList(newDomainList);

      showStatus('Domain removed successfully', 'success');
    } catch (error) {
      console.error('Error removing domain:', error);
      showStatus('Error removing domain: ' + error.message, 'error');
    }
  }

  // Function to add pillar page
  async function addPillarPage() {
    try {
      const url = pillarUrlInput.value.trim();
      const topic = pillarTopicInput.value.trim();

      if (!url || !topic) {
        showStatus('Please enter both URL and topic', 'error');
        return;
      }

      // Validate URL format
      if (!isValidUrl(url)) {
        showStatus('Please enter a valid URL', 'error');
        return;
      }

      // Get current pillar pages
      const { pillarPages = [] } = await chrome.storage.local.get('pillarPages');

      // Check if URL already exists
      if (pillarPages.some(page => page.url === url)) {
        showStatus('Pillar page with this URL already exists', 'error');
        return;
      }

      // Add pillar page
      const newPillarPages = [...pillarPages, { url, topic }];
      await chrome.storage.local.set({ pillarPages: newPillarPages });

      // Update UI
      renderPillarPages(newPillarPages);
      pillarUrlInput.value = '';
      pillarTopicInput.value = '';

      showStatus('Pillar page added successfully', 'success');
    } catch (error) {
      console.error('Error adding pillar page:', error);
      showStatus('Error adding pillar page: ' + error.message, 'error');
    }
  }

  // Function to remove pillar page
  async function removePillarPage(url) {
    try {
      // Get current pillar pages
      const { pillarPages = [] } = await chrome.storage.local.get('pillarPages');

      // Remove pillar page
      const newPillarPages = pillarPages.filter(page => page.url !== url);
      await chrome.storage.local.set({ pillarPages: newPillarPages });

      // Update UI
      renderPillarPages(newPillarPages);

      showStatus('Pillar page removed successfully', 'success');
    } catch (error) {
      console.error('Error removing pillar page:', error);
      showStatus('Error removing pillar page: ' + error.message, 'error');
    }
  }

  // Function to save settings
  async function saveSettings() {
    try {
      // Get values from UI
      const frequency = crawlFrequency.value;
      const depth = parseInt(crawlDepth.value);
      const minLinks = parseInt(minInternalLinks.value);

      // Validate inputs
      if (isNaN(depth) || depth < 1 || depth > 10) {
        showStatus('Crawl depth must be between 1 and 10', 'error');
        return;
      }

      if (isNaN(minLinks) || minLinks < 1 || minLinks > 10) {
        showStatus('Minimum internal links must be between 1 and 10', 'error');
        return;
      }

      // Save settings
      await chrome.storage.local.set({
        crawlFrequency: frequency,
        crawlDepth: depth,
        minInternalLinks: minLinks
      });

      showStatus('Settings saved successfully', 'success');
    } catch (error) {
      console.error('Error saving settings:', error);
      showStatus('Error saving settings: ' + error.message, 'error');
    }
  }

  // Function to reset settings
  async function resetSettings() {
    if (!confirm('Are you sure you want to reset all settings to defaults?')) {
      return;
    }

    try {
      // Set default settings
      await chrome.storage.local.set({
        domainWhitelist: [],
        crawlFrequency: 'weekly',
        crawlDepth: 3,
        minInternalLinks: 3,
        pillarPages: []
      });

      // Reload settings
      await loadSettings();

      showStatus('Settings reset to defaults', 'success');
    } catch (error) {
      console.error('Error resetting settings:', error);
      showStatus('Error resetting settings: ' + error.message, 'error');
    }
  }

  // Function to show status message
  function showStatus(message, type) {
    statusMessage.textContent = message;
    statusMessage.className = 'status ' + type;
    statusMessage.style.display = 'block';

    // Hide after 3 seconds
    setTimeout(() => {
      statusMessage.style.display = 'none';
    }, 3000);
  }

  // Function to validate domain
  function isValidDomain(domain) {
    // More permissive regex that accepts all TLDs and subdomains
    const domainRegex = /^([a-zA-Z0-9]([a-zA-Z0-9\\-]{0,61}[a-zA-Z0-9])?\\.)+[a-zA-Z0-9][a-zA-Z0-9\\-]{0,61}[a-zA-Z0-9]$/;

    // Also accept localhost for testing
    if (domain === 'localhost') {
      return true;
    }

    return domainRegex.test(domain);
  }

  // Function to validate URL
  function isValidUrl(url) {
    try {
      new URL(url);
      return true;
    } catch (error) {
      return false;
    }
  }
});
