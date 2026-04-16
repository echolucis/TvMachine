/**
 * IPTV/EPG Frontend Application
 * Main entry point - handles channel list, EPG display, and video playback
 */

import Hls from 'hls.js';

const API_BASE = 'http://localhost:8000/api';

// State
let channels = [];
let selectedChannelId = null;
let currentProgramme = null;
let hls = null;

// DOM Elements
const channelListEl = document.getElementById('channelList');
const programmeListEl = document.getElementById('programmeList');
const timeAxisEl = document.getElementById('timeAxis');
const videoPlayer = document.getElementById('videoPlayer');
const playerInfoEl = document.getElementById('playerInfo');
const currentShowEl = document.getElementById('currentShow');
const searchInput = document.getElementById('searchInput');
const searchResultsEl = document.getElementById('searchResults');
const healthStatusEl = document.getElementById('healthStatus');

// Initialize application
async function init() {
  try {
    await loadHealth();
    await loadChannels();
    setupSearch();
    renderTimeAxis();
  } catch (error) {
    console.error('Failed to initialize:', error);
    channelListEl.innerHTML = '<div class="no-channel">Failed to load channels. Is the backend running?</div>';
  }
}

// Load health status
async function loadHealth() {
  try {
    const response = await fetch(`${API_BASE}/health`);
    const data = await response.json();
    
    if (data.status === 'healthy') {
      healthStatusEl.textContent = `✓ ${data.channels_active}/${data.channels_total} channels`;
      healthStatusEl.classList.add('ok');
    } else {
      healthStatusEl.textContent = '⚠ Service degraded';
    }
  } catch (error) {
    healthStatusEl.textContent = '✗ Backend offline';
  }
}

// Load channels
async function loadChannels() {
  try {
    const response = await fetch(`${API_BASE}/channels?limit=500&status=active`);
    const data = await response.json();
    channels = data.channels || [];
    
    renderChannelList();
  } catch (error) {
    console.error('Failed to load channels:', error);
    throw error;
  }
}

// Render channel list
function renderChannelList() {
  if (channels.length === 0) {
    channelListEl.innerHTML = '<div class="no-channel">No channels available</div>';
    return;
  }

  channelListEl.innerHTML = channels.map(channel => `
    <div class="channel-item ${channel.id === selectedChannelId ? 'active' : ''}" 
         data-channel-id="${channel.id}">
      <div class="channel-logo">
        ${channel.logo 
          ? `<img src="${channel.logo}" alt="${channel.name}" onerror="this.style.display='none';this.parentElement.textContent='${channel.name.charAt(0)}'">`
          : channel.name.charAt(0).toUpperCase()
        }
      </div>
      <div class="channel-info">
        <div class="channel-name">${escapeHtml(channel.name)}</div>
        <div class="channel-group">${escapeHtml(channel.group || 'General')}</div>
      </div>
      <div class="channel-status ${channel.status || 'unknown'}"></div>
    </div>
  `).join('');

  // Add click handlers
  channelListEl.querySelectorAll('.channel-item').forEach(item => {
    item.addEventListener('click', () => {
      const channelId = item.dataset.channelId;
      selectChannel(channelId);
    });
  });
}

// Select a channel
async function selectChannel(channelId) {
  selectedChannelId = channelId;
  
  // Update UI
  channelListEl.querySelectorAll('.channel-item').forEach(item => {
    item.classList.toggle('active', item.dataset.channelId === channelId);
  });

  // Load channel details
  try {
    const response = await fetch(`${API_BASE}/channel/${channelId}`);
    const data = await response.json();
    
    // Load stream
    loadStream(data.channel);
    
    // Load EPG
    await loadGuide(channelId);
    
    // Update player info
    if (data.current_programme) {
      currentShowEl.textContent = data.current_programme.title;
      playerInfoEl.style.display = 'block';
      currentProgramme = data.current_programme;
    } else {
      playerInfoEl.style.display = 'none';
    }
  } catch (error) {
    console.error('Failed to load channel:', error);
  }
}

// Load stream
function loadStream(channel) {
  const streamUrl = channel.url;
  
  if (!streamUrl) {
    console.warn('No stream URL for channel');
    return;
  }

  // Destroy existing HLS instance
  if (hls) {
    hls.destroy();
    hls = null;
  }

  // Check if HLS
  if (streamUrl.includes('.m3u8')) {
    if (Hls.isSupported()) {
      hls = new Hls();
      hls.loadSource(streamUrl);
      hls.attachMedia(videoPlayer);
      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        videoPlayer.play().catch(e => console.log('Autoplay prevented'));
      });
    } else if (videoPlayer.canPlayType('application/vnd.apple.mpegurl')) {
      // Native HLS support (Safari)
      videoPlayer.src = streamUrl;
      videoPlayer.play().catch(e => console.log('Autoplay prevented'));
    }
  } else {
    // Direct stream
    videoPlayer.src = streamUrl;
    videoPlayer.play().catch(e => console.log('Autoplay prevented'));
  }
}

// Load EPG guide
async function loadGuide(channelId) {
  try {
    const now = new Date();
    const tomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000);
    
    const response = await fetch(
      `${API_BASE}/guide?channel_id=${channelId}&start=${now.toISOString()}&end=${tomorrow.toISOString()}`
    );
    const data = await response.json();
    
    renderProgrammes(data.programmes || []);
  } catch (error) {
    console.error('Failed to load guide:', error);
    programmeListEl.innerHTML = '<div class="no-channel">Failed to load programme guide</div>';
  }
}

// Render programmes
function renderProgrammes(programmes) {
  if (programmes.length === 0) {
    programmeListEl.innerHTML = '<div class="no-channel">No programme information available</div>';
    return;
  }

  const now = new Date().toISOString();
  
  programmeListEl.innerHTML = programmes.map(prog => {
    const isCurrent = prog.start_utc <= now && prog.end_utc > now;
    
    return `
      <div class="programme-item ${isCurrent ? 'current' : ''}">
        <div class="programme-time">
          ${formatTime(prog.start_utc)} - ${formatTime(prog.end_utc)}
        </div>
        <div class="programme-title">${escapeHtml(prog.title)}</div>
        ${prog.description 
          ? `<div class="programme-description">${escapeHtml(prog.description)}</div>`
          : ''
        }
      </div>
    `;
  }).join('');
}

// Render time axis
function renderTimeAxis() {
  const hours = [];
  const now = new Date();
  
  for (let i = 0; i < 12; i++) {
    const hour = new Date(now.getTime() + i * 60 * 60 * 1000);
    hours.push(formatHour(hour));
  }
  
  timeAxisEl.innerHTML = hours.join('');
}

// Setup search
function setupSearch() {
  let debounceTimer;
  
  searchInput.addEventListener('input', (e) => {
    clearTimeout(debounceTimer);
    const query = e.target.value.trim();
    
    if (query.length < 2) {
      searchResultsEl.classList.remove('visible');
      return;
    }
    
    debounceTimer = setTimeout(() => {
      performSearch(query);
    }, 300);
  });

  // Close search results on outside click
  document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !searchResultsEl.contains(e.target)) {
      searchResultsEl.classList.remove('visible');
    }
  });
}

// Perform search
async function performSearch(query) {
  try {
    const response = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query)}&limit=20`);
    const data = await response.json();
    
    renderSearchResults(data.results || []);
  } catch (error) {
    console.error('Search failed:', error);
  }
}

// Render search results
function renderSearchResults(results) {
  if (results.length === 0) {
    searchResultsEl.innerHTML = '<div class="search-result-item">No results found</div>';
    searchResultsEl.classList.add('visible');
    return;
  }

  searchResultsEl.innerHTML = results.map(result => `
    <div class="search-result-item" data-channel-id="${result.channel_id}">
      <div class="search-result-title">${escapeHtml(result.title)}</div>
      <div class="search-result-channel">${formatTime(result.start_utc)} • Channel ${result.channel_id}</div>
    </div>
  `).join('');

  // Add click handlers
  searchResultsEl.querySelectorAll('.search-result-item').forEach(item => {
    item.addEventListener('click', () => {
      const channelId = item.dataset.channelId;
      searchResultsEl.classList.remove('visible');
      searchInput.value = '';
      
      // Find and select channel
      const channel = channels.find(ch => ch.id === channelId || ch.tvg_id === channelId);
      if (channel) {
        selectChannel(channel.id);
      }
    });
  });

  searchResultsEl.classList.add('visible');
}

// Utility functions
function formatTime(isoString) {
  const date = new Date(isoString);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function formatHour(date) {
  return date.toLocaleTimeString([], { hour: '2-digit' });
}

function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Keyboard navigation
document.addEventListener('keydown', (e) => {
  if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
    e.preventDefault();
    const currentIndex = channels.findIndex(ch => ch.id === selectedChannelId);
    
    if (e.key === 'ArrowUp' && currentIndex > 0) {
      selectChannel(channels[currentIndex - 1].id);
    } else if (e.key === 'ArrowDown' && currentIndex < channels.length - 1) {
      selectChannel(channels[currentIndex + 1].id);
    }
  }
});

// Initialize on load
init();
