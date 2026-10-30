/**
 * URL Shortener Frontend Controller
 * Decoupled Client for First-Principles URL Shortener Backend
 */

(function () {
  "use strict";

  // State Management
  const STORAGE_KEY_API_URL = "shortener_api_url";
  const STORAGE_KEY_HISTORY = "shortener_history_v1";

  let apiBaseUrl = localStorage.getItem(STORAGE_KEY_API_URL) || "http://localhost:8000";
  // Strip trailing slashes
  apiBaseUrl = apiBaseUrl.replace(/\/+$/, "");

  // DOM Elements
  const statusDot = document.getElementById("statusDot");
  const statusText = document.getElementById("statusText");
  const configToggleBtn = document.getElementById("configToggleBtn");
  const configDrawer = document.getElementById("configDrawer");
  const apiUrlInput = document.getElementById("apiUrlInput");
  const saveApiUrlBtn = document.getElementById("saveApiUrlBtn");
  const aliasPrefix = document.getElementById("aliasPrefix");
  const notification = document.getElementById("notification");

  // Tab Navigation
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  // Shorten Form Elements
  const shortenForm = document.getElementById("shortenForm");
  const longUrlInput = document.getElementById("longUrlInput");
  const aliasInput = document.getElementById("aliasInput");
  const pasteBtn = document.getElementById("pasteBtn");
  const shortenSubmitBtn = document.getElementById("shortenSubmitBtn");
  const shortenResult = document.getElementById("shortenResult");
  const resultShortUrl = document.getElementById("resultShortUrl");
  const copyShortUrlBtn = document.getElementById("copyShortUrlBtn");
  const visitShortUrlBtn = document.getElementById("visitShortUrlBtn");
  const resultOriginalUrl = document.getElementById("resultOriginalUrl");
  const resultShortKey = document.getElementById("resultShortKey");
  const resultCreatedAt = document.getElementById("resultCreatedAt");
  const viewCreatedStatsBtn = document.getElementById("viewCreatedStatsBtn");

  // History Elements
  const historyTableBody = document.getElementById("historyTableBody");
  const emptyHistory = document.getElementById("emptyHistory");
  const clearHistoryBtn = document.getElementById("clearHistoryBtn");

  // Analytics Elements
  const statsLookupForm = document.getElementById("statsLookupForm");
  const statsKeyInput = document.getElementById("statsKeyInput");
  const statsResultsContainer = document.getElementById("statsResultsContainer");
  const statsClickCount = document.getElementById("statsClickCount");
  const statsKeyDisplay = document.getElementById("statsKeyDisplay");
  const statsCreatedDisplay = document.getElementById("statsCreatedDisplay");
  const statsTargetUrl = document.getElementById("statsTargetUrl");
  const eventsTableBody = document.getElementById("eventsTableBody");
  const noEventsState = document.getElementById("noEventsState");
  const refreshStatsBtn = document.getElementById("refreshStatsBtn");

  // Health Elements
  const healthStatusText = document.getElementById("healthStatusText");
  const healthServiceName = document.getElementById("healthServiceName");
  const healthCacheCount = document.getElementById("healthCacheCount");
  const healthLatency = document.getElementById("healthLatency");

  let activeStatsKey = null;

  // Initialize
  function init() {
    apiUrlInput.value = apiBaseUrl;
    updateAliasPrefix();
    setupEventListeners();
    renderHistory();
    checkBackendHealth();

    // Check health every 15 seconds
    setInterval(checkBackendHealth, 15000);
  }

  function updateAliasPrefix() {
    aliasPrefix.textContent = `${apiBaseUrl}/`;
  }

  // Event Listeners
  function setupEventListeners() {
    // Config drawer toggle
    configToggleBtn.addEventListener("click", () => {
      configDrawer.classList.toggle("hidden");
    });

    // Save API Base URL
    saveApiUrlBtn.addEventListener("click", () => {
      let newUrl = apiUrlInput.value.trim().replace(/\/+$/, "");
      if (!newUrl) {
        showNotification("Please provide a valid URL", "error");
        return;
      }
      apiBaseUrl = newUrl;
      localStorage.setItem(STORAGE_KEY_API_URL, apiBaseUrl);
      updateAliasPrefix();
      configDrawer.classList.add("hidden");
      showNotification(`API connected to: ${apiBaseUrl}`, "info");
      checkBackendHealth();
    });

    // Tab Navigation
    tabBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        const targetTabId = btn.getAttribute("data-tab");
        switchTab(targetTabId);
      });
    });

    // Paste button
    pasteBtn.addEventListener("click", async () => {
      try {
        const text = await navigator.clipboard.readText();
        longUrlInput.value = text.trim();
        longUrlInput.focus();
      } catch (err) {
        showNotification("Please paste manually using Ctrl+V or Cmd+V.", "info");
      }
    });

    // Shorten Form Submit
    shortenForm.addEventListener("submit", handleShortenSubmit);

    // Copy Button for newly created link
    copyShortUrlBtn.addEventListener("click", () => {
      copyToClipboard(resultShortUrl.value, copyShortUrlBtn);
    });

    // Jump to stats for newly created link
    viewCreatedStatsBtn.addEventListener("click", () => {
      const key = resultShortKey.textContent;
      if (key) {
        switchTab("analyticsTab");
        statsKeyInput.value = key;
        fetchAndDisplayStats(key);
      }
    });

    // Clear History Button
    clearHistoryBtn.addEventListener("click", () => {
      if (confirm("Are you sure you want to clear your local link history?")) {
        localStorage.removeItem(STORAGE_KEY_HISTORY);
        renderHistory();
        showNotification("Local history cleared.", "info");
      }
    });

    // Analytics Search Form Submit
    statsLookupForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const rawInput = statsKeyInput.value.trim();
      if (!rawInput) return;
      const key = extractKey(rawInput);
      fetchAndDisplayStats(key);
    });

    // Refresh Stats Button
    refreshStatsBtn.addEventListener("click", () => {
      if (activeStatsKey) {
        fetchAndDisplayStats(activeStatsKey);
      }
    });
  }

  // Switch Tabs helper
  function switchTab(tabId) {
    tabBtns.forEach((btn) => {
      btn.classList.toggle("active", btn.getAttribute("data-tab") === tabId);
    });
    tabContents.forEach((content) => {
      content.classList.toggle("active", content.id === tabId);
    });
  }

  // Extract key if user entered full URL
  function extractKey(input) {
    try {
      if (input.startsWith("http://") || input.startsWith("https://")) {
        const parsed = new URL(input);
        const segments = parsed.pathname.split("/").filter(Boolean);
        return segments[segments.length - 1] || input;
      }
    } catch (_) {
      // Fallback to raw string
    }
    return input.replace(/^\/+|\/+$/g, "");
  }

  // Check Backend Health
  async function checkBackendHealth() {
    const startTime = performance.now();
    try {
      const res = await fetch(`${apiBaseUrl}/`, {
        method: "GET",
        headers: { Accept: "application/json" },
      });

      const elapsed = Math.round(performance.now() - startTime);

      if (res.ok) {
        const data = await res.json();
        statusDot.className = "status-dot online";
        statusText.textContent = "Backend: Online";

        healthStatusText.className = "badge badge-success";
        healthStatusText.textContent = "Healthy (200 OK)";
        healthServiceName.textContent = data.service || "First-Principles URL Shortener";
        healthCacheCount.textContent = `${data.cached_keys_count ?? 0} keys in memory`;
        healthLatency.textContent = `${elapsed} ms`;
      } else {
        throw new Error(`HTTP ${res.status}`);
      }
    } catch (err) {
      statusDot.className = "status-dot offline";
      statusText.textContent = "Backend: Offline";

      healthStatusText.className = "badge badge-danger";
      healthStatusText.textContent = "Offline / Unreachable";
      healthServiceName.textContent = "-";
      healthCacheCount.textContent = "-";
      healthLatency.textContent = "-";
    }
  }

  // Shorten Submit Handler
  async function handleShortenSubmit(e) {
    e.preventDefault();
    const url = longUrlInput.value.trim();
    const customAlias = aliasInput.value.trim();

    if (!url) return;

    // Loading state
    setShortenLoading(true);
    shortenResult.classList.add("hidden");

    const payload = { url: url };
    if (customAlias) {
      payload.custom_alias = customAlias;
    }

    try {
      const res = await fetch(`${apiBaseUrl}/api/shorten`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (!res.ok) {
        const message = data.detail || "Failed to shorten URL.";
        showNotification(message, "error");
        return;
      }

      // Display Result
      resultShortUrl.value = data.short_url;
      visitShortUrlBtn.href = data.short_url;
      resultOriginalUrl.href = data.original_url;
      resultOriginalUrl.textContent = data.original_url;
      resultShortKey.textContent = data.short_key;
      resultCreatedAt.textContent = formatTimestamp(data.created_at);

      shortenResult.classList.remove("hidden");
      showNotification("Short URL generated successfully!", "success");

      // Save to History
      saveToHistory({
        short_url: data.short_url,
        short_key: data.short_key,
        original_url: data.original_url,
        created_at: data.created_at,
      });

      // Clear input fields
      aliasInput.value = "";
    } catch (err) {
      showNotification(
        `Connection failed. Ensure FastAPI is running on ${apiBaseUrl} (e.g. 'python main.py')`,
        "error"
      );
    } finally {
      setShortenLoading(false);
    }
  }

  function setShortenLoading(isLoading) {
    const btnText = shortenSubmitBtn.querySelector(".btn-text");
    const spinner = shortenSubmitBtn.querySelector(".btn-spinner");

    if (isLoading) {
      shortenSubmitBtn.disabled = true;
      btnText.textContent = "Shortening...";
      spinner.classList.remove("hidden");
    } else {
      shortenSubmitBtn.disabled = false;
      btnText.textContent = "Shorten URL";
      spinner.classList.add("hidden");
    }
  }

  // Fetch & Display Analytics
  async function fetchAndDisplayStats(key) {
    if (!key) return;
    activeStatsKey = key;

    try {
      statsResultsContainer.classList.add("hidden");
      const res = await fetch(`${apiBaseUrl}/api/stats/${encodeURIComponent(key)}`);
      const data = await res.json();

      if (!res.ok) {
        showNotification(data.detail || `Short key '${key}' not found.`, "error");
        return;
      }

      statsClickCount.textContent = Number(data.total_clicks).toLocaleString();
      statsKeyDisplay.textContent = data.short_key;
      statsCreatedDisplay.textContent = formatTimestamp(data.created_at);
      statsTargetUrl.href = data.original_url;
      statsTargetUrl.textContent = data.original_url;

      renderClickEvents(data.recent_events || []);
      statsResultsContainer.classList.remove("hidden");
      showNotification(`Loaded analytics for key: ${key}`, "success");
    } catch (err) {
      showNotification(`Unable to retrieve stats: ${err.message}`, "error");
    }
  }

  // Render Click Events Table
  function renderClickEvents(events) {
    eventsTableBody.innerHTML = "";
    if (!events || events.length === 0) {
      noEventsState.classList.remove("hidden");
      return;
    }

    noEventsState.classList.add("hidden");
    // Sort events descending (newest first)
    const sorted = [...events].sort((a, b) => b.clicked_at - a.clicked_at);

    sorted.forEach((event) => {
      const row = document.createElement("tr");

      const timeTd = document.createElement("td");
      timeTd.textContent = formatTimestamp(event.clicked_at);

      const refTd = document.createElement("td");
      refTd.textContent = event.referrer || "(Direct / None)";

      const uaTd = document.createElement("td");
      uaTd.textContent = simplifyUserAgent(event.user_agent);
      uaTd.title = event.user_agent || "";

      row.appendChild(timeTd);
      row.appendChild(refTd);
      row.appendChild(uaTd);
      eventsTableBody.appendChild(row);
    });
  }

  function simplifyUserAgent(ua) {
    if (!ua) return "(Unknown)";
    if (ua.includes("Chrome") && !ua.includes("Edg")) return "Chrome";
    if (ua.includes("Edg")) return "Edge";
    if (ua.includes("Firefox")) return "Firefox";
    if (ua.includes("Safari") && !ua.includes("Chrome")) return "Safari";
    if (ua.includes("curl")) return "curl CLI";
    if (ua.includes("python-requests") || ua.includes("python")) return "Python Script";
    return ua.slice(0, 45) + (ua.length > 45 ? "..." : "");
  }

  // Local Storage History
  function getHistory() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY_HISTORY);
      return stored ? JSON.parse(stored) : [];
    } catch (_) {
      return [];
    }
  }

  function saveToHistory(item) {
    let history = getHistory();
    // Prevent duplicate entries for same key
    history = history.filter((h) => h.short_key !== item.short_key);
    history.unshift(item); // Prepend to beginning
    if (history.length > 50) history.pop(); // Keep last 50
    localStorage.setItem(STORAGE_KEY_HISTORY, JSON.stringify(history));
    renderHistory();
  }

  function renderHistory() {
    const history = getHistory();
    historyTableBody.innerHTML = "";

    if (history.length === 0) {
      emptyHistory.classList.remove("hidden");
      clearHistoryBtn.classList.add("hidden");
      return;
    }

    emptyHistory.classList.add("hidden");
    clearHistoryBtn.classList.remove("hidden");

    history.forEach((item) => {
      const row = document.createElement("tr");

      // Short Link
      const shortLinkTd = document.createElement("td");
      const shortLinkA = document.createElement("a");
      shortLinkA.href = item.short_url;
      shortLinkA.target = "_blank";
      shortLinkA.className = "table-key";
      shortLinkA.textContent = item.short_key;
      shortLinkTd.appendChild(shortLinkA);

      // Original URL
      const origUrlTd = document.createElement("td");
      const origSpan = document.createElement("span");
      origSpan.className = "table-url";
      origSpan.title = item.original_url;
      origSpan.textContent = item.original_url;
      origUrlTd.appendChild(origSpan);

      // Date
      const dateTd = document.createElement("td");
      dateTd.textContent = formatTimestamp(item.created_at);

      // Action Buttons
      const actionsTd = document.createElement("td");
      actionsTd.className = "text-right";

      const copyBtn = document.createElement("button");
      copyBtn.className = "btn-subtle";
      copyBtn.textContent = "Copy";
      copyBtn.style.marginRight = "6px";
      copyBtn.addEventListener("click", () => copyToClipboard(item.short_url, copyBtn));

      const statsBtn = document.createElement("button");
      statsBtn.className = "btn-subtle";
      statsBtn.textContent = "Stats";
      statsBtn.addEventListener("click", () => {
        switchTab("analyticsTab");
        statsKeyInput.value = item.short_key;
        fetchAndDisplayStats(item.short_key);
      });

      actionsTd.appendChild(copyBtn);
      actionsTd.appendChild(statsBtn);

      row.appendChild(shortLinkTd);
      row.appendChild(origUrlTd);
      row.appendChild(dateTd);
      row.appendChild(actionsTd);

      historyTableBody.appendChild(row);
    });
  }

  // Copy with fallback for file:// or non-secure contexts
  function copyToClipboard(text, btnElement) {
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard
        .writeText(text)
        .then(() => showCopiedFeedback(btnElement))
        .catch(() => fallbackCopy(text, btnElement));
    } else {
      fallbackCopy(text, btnElement);
    }
  }

  function fallbackCopy(text, btnElement) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.position = "fixed";
    textArea.style.opacity = "0";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
      document.execCommand("copy");
      showCopiedFeedback(btnElement);
    } catch (_) {
      showNotification("Could not auto-copy. Please copy manually.", "error");
    } finally {
      document.body.removeChild(textArea);
    }
  }

  function showCopiedFeedback(btnElement) {
    if (!btnElement) return;
    const originalText = btnElement.textContent;
    btnElement.textContent = "Copied! ✓";
    btnElement.style.color = "var(--success)";
    setTimeout(() => {
      btnElement.textContent = originalText;
      btnElement.style.color = "";
    }, 1800);
  }

  // Format Unix timestamp
  function formatTimestamp(timestamp) {
    if (!timestamp) return "-";
    const date = new Date(timestamp * 1000);
    return date.toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  }

  // Notification Banner
  let notificationTimeout = null;
  function showNotification(message, type = "info") {
    clearTimeout(notificationTimeout);
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.classList.remove("hidden");

    notificationTimeout = setTimeout(() => {
      notification.classList.add("hidden");
    }, 4500);
  }

  // Run on load
  document.addEventListener("DOMContentLoaded", init);
})();

