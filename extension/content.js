// content.js - VeriJob AI

console.log("VeriJob AI Extension Loaded");

// Helper to create the badge element
function createBadge(score, status) {
    const badge = document.createElement("div");
    badge.className = "verijob-badge";

    const isVerified = status === 'Verified' || score > 70;

    if (isVerified) {
        badge.style.backgroundColor = "#000000";
        badge.style.borderColor = "#22c55e";
        badge.style.color = "#22c55e";
        badge.innerHTML = `✓ VERIFIED <span style="margin-left:6px; opacity:0.8;">${score}%</span>`;
    } else {
        badge.style.backgroundColor = "#000000";
        badge.style.borderColor = "#ef4444";
        badge.style.color = "#ef4444";
        badge.innerHTML = `⚠ SUSPICIOUS <span style="margin-left:6px; opacity:0.8;">${score}%</span>`;
    }

    badge.title = "Click extension icon for details";
    return badge;
}

// Function to process LinkedIn Job Header
async function processLinkedInJob() {
    // Try multiple selectors common in LinkedIn (Updated for 2025 layouts)
    const selectors = [
        ".job-details-jobs-unified-top-card__job-title",
        ".jobs-unified-top-card__job-title",
        "h1.top-card-layout__title",
        "h1.t-24",
        ".job-view-layout h1",
        ".jobs-details__main-content h1"
    ];

    let titleElement = null;
    for (const sel of selectors) {
        titleElement = document.querySelector(sel);
        if (titleElement) break;
    }

    if (titleElement && !titleElement.querySelector(".verijob-badge")) {
        console.log("Found Job Title:", titleElement.innerText);

        // Construct the current URL specifically for the job
        // Often the window.location is correct, specifically if it has 'currentJobId' or is a /view/ page
        const jobUrl = window.location.href;

        // Visual loading state
        const loadingBadge = document.createElement("span");
        loadingBadge.className = "verijob-badge verijob-loading";
        loadingBadge.innerText = "Verifying...";
        loadingBadge.style.backgroundColor = "#6366f1"; // Indigo
        titleElement.appendChild(loadingBadge);

        try {
            const pageContent = document.body.innerText; // Capture text

            // Send message to background script to handle the fetch (bypasses CORS/CSP)
            chrome.runtime.sendMessage({
                action: "verifyJob",
                data: {
                    url: jobUrl,
                    content: pageContent
                }
            }, (response) => {
                if (chrome.runtime.lastError) {
                    console.error("Runtime Error:", chrome.runtime.lastError);
                    throw new Error(chrome.runtime.lastError.message);
                }

                if (response && response.success) {
                    // Remove loader
                    loadingBadge.remove();

                    // Append result badge
                    const resultBadge = createBadge(response.data.score, response.data.status);
                    titleElement.appendChild(resultBadge);
                } else {
                    throw new Error(response.error || "Unknown error from background script");
                }
            });

        } catch (error) {
            console.error("VeriJob Error Details:", error);
            loadingBadge.innerText = "Error";
            loadingBadge.title = error.message; // Show error on hover
            loadingBadge.style.backgroundColor = "#71717a";
        }
    }
}

// Function to process Naukri Job Header
async function processNaukriJob() {
    // Naukri Selectors (2025)
    // Try multiple possible title selectors
    const selectors = [
        "header.styles_jd-header__kv1aP h1",
        ".jd-header-title",
        ".job-desc h1",
        ".job-title"
    ];

    let titleElement = null;
    for (const sel of selectors) {
        titleElement = document.querySelector(sel);
        if (titleElement) break;
    }

    if (titleElement && !titleElement.querySelector(".verijob-badge")) {
        console.log("Found Naukri Job Title:", titleElement.innerText);
        const jobUrl = window.location.href;

        // Visual loading state
        const loadingBadge = document.createElement("span");
        loadingBadge.className = "verijob-badge verijob-loading";
        loadingBadge.innerText = "Verifying...";
        loadingBadge.style.backgroundColor = "#6366f1"; // Indigo
        loadingBadge.style.marginLeft = "10px";
        loadingBadge.style.fontSize = "12px";

        titleElement.appendChild(loadingBadge);

        try {
            // Naukri specific content extraction
            let pageContent = "";
            const descElem = document.querySelector(".styles_job-desc-container__txpYf") || document.querySelector(".job-desc");
            if (descElem) {
                pageContent = descElem.innerText;
            } else {
                pageContent = document.body.innerText; // Fallback
            }

            // Send message to background script
            chrome.runtime.sendMessage({
                action: "verifyJob",
                data: {
                    url: jobUrl,
                    content: pageContent
                }
            }, (response) => {
                if (chrome.runtime.lastError) {
                    console.error("Runtime Error:", chrome.runtime.lastError);
                    throw new Error(chrome.runtime.lastError.message);
                }

                if (response && response.success) {
                    loadingBadge.remove();
                    const resultBadge = createBadge(response.data.score, response.data.status);
                    resultBadge.style.marginLeft = "10px";
                    resultBadge.style.display = "inline-block";
                    titleElement.appendChild(resultBadge);
                } else {
                    throw new Error(response.error || "Unknown error from background script");
                }
            });

        } catch (error) {
            console.error("VeriJob Error Details:", error);
            loadingBadge.innerText = "Error";
            loadingBadge.title = error.message;
            loadingBadge.style.backgroundColor = "#71717a";
        }
    }
}

// Function to process Naukri Job Pages
async function processNaukriJob() {
    // Naukri job page selectors (2025 layout)
    const selectors = [
        ".styles_jd-header__kv1aP h1",
        "h1.jd-header-title",
        ".job-header h1",
        "header h1"
    ];

    let titleElement = null;
    for (const sel of selectors) {
        titleElement = document.querySelector(sel);
        if (titleElement) break;
    }

    if (titleElement && !titleElement.querySelector(".verijob-badge")) {
        console.log("Found Naukri Job Title:", titleElement.innerText);
        const jobUrl = window.location.href;

        const loadingBadge = document.createElement("span");
        loadingBadge.className = "verijob-badge verijob-loading";
        loadingBadge.innerText = "Analyzing...";
        loadingBadge.style.marginLeft = "10px";
        titleElement.appendChild(loadingBadge);

        try {
            chrome.runtime.sendMessage(
                { action: "verifyJob", url: jobUrl },
                (response) => {
                    loadingBadge.remove();
                    if (response && response.score !== undefined) {
                        const resultBadge = createBadge(response.score, response.status);
                        resultBadge.style.marginLeft = "10px";
                        resultBadge.style.display = "inline-block";
                        titleElement.appendChild(resultBadge);
                    }
                }
            );
        } catch (error) {
            console.error("VeriJob Naukri Error:", error);
            loadingBadge.innerText = "Error";
            loadingBadge.style.backgroundColor = "#71717a";
        }
    }
}

// Function to process Indeed Job Pages
async function processIndeedJob() {
    const selectors = [
        ".jobsearch-JobInfoHeader-title",
        "h1.jobsearch-JobInfoHeader-title",
        ".jobTitle h1",
        "h1[data-testid='job-title']"
    ];

    let titleElement = null;
    for (const sel of selectors) {
        titleElement = document.querySelector(sel);
        if (titleElement) break;
    }

    if (titleElement && !titleElement.querySelector(".verijob-badge")) {
        console.log("Found Indeed Job Title:", titleElement.innerText);
        const jobUrl = window.location.href;

        const loadingBadge = document.createElement("span");
        loadingBadge.className = "verijob-badge verijob-loading";
        loadingBadge.innerText = "Analyzing...";
        loadingBadge.style.marginLeft = "10px";
        titleElement.appendChild(loadingBadge);

        try {
            chrome.runtime.sendMessage(
                { action: "verifyJob", url: jobUrl },
                (response) => {
                    loadingBadge.remove();
                    if (response && response.score !== undefined) {
                        const resultBadge = createBadge(response.score, response.status);
                        resultBadge.style.marginLeft = "10px";
                        resultBadge.style.display = "inline-block";
                        titleElement.appendChild(resultBadge);
                    }
                }
            );
        } catch (error) {
            console.error("VeriJob Indeed Error:", error);
            loadingBadge.innerText = "Error";
            loadingBadge.style.backgroundColor = "#71717a";
        }
    }
}

// Function to process Glassdoor Job Pages (with retry for lazy loading)
async function processGlassdoorJob(retryCount = 0) {
    console.log(`🔍 VeriJob: Attempting to process Glassdoor page... (attempt ${retryCount + 1})`);

    const selectors = [
        '[data-test="job-title"]',
        'h1[class*="jobTitle"]',
        'h1[class*="JobDetails_jobTitle"]',
        'div[data-test="job-details"] h1',
        '.jobTitle',
        'h1', // Generic h1 as last resort
        'h2[class*="jobTitle"]' // Sometimes it's h2
    ];

    let titleElement = null;
    for (const sel of selectors) {
        titleElement = document.querySelector(sel);
        if (titleElement && titleElement.innerText.trim().length > 0) {
            console.log(`✅ VeriJob: Found title with selector: ${sel}`);
            break;
        }
    }

    if (!titleElement || titleElement.innerText.trim().length === 0) {
        const allH1s = document.querySelectorAll('h1');
        console.log(`❌ VeriJob: Could not find job title element on Glassdoor (found ${allH1s.length} h1 elements)`);

        // Retry up to 5 times with increasing delays
        if (retryCount < 5) {
            const delay = 1000 * (retryCount + 1); // 1s, 2s, 3s, 4s, 5s
            console.log(`⏳ VeriJob: Retrying in ${delay}ms...`);
            setTimeout(() => processGlassdoorJob(retryCount + 1), delay);
        } else {
            console.log("⚠️ VeriJob: Gave up after 5 attempts");
        }
        return;
    }

    if (titleElement.querySelector(".verijob-badge")) {
        console.log("⚠️ VeriJob: Badge already exists, skipping");
        return;
    }

    console.log("✅ Found Glassdoor Job Title:", titleElement.innerText);
    const jobUrl = window.location.href;

    const loadingBadge = document.createElement("span");
    loadingBadge.className = "verijob-badge verijob-loading";
    loadingBadge.innerText = "Analyzing...";
    loadingBadge.style.marginLeft = "10px";
    titleElement.appendChild(loadingBadge);

    try {
        chrome.runtime.sendMessage(
            { action: "verifyJob", url: jobUrl },
            (response) => {
                loadingBadge.remove();
                if (response && response.score !== undefined) {
                    const resultBadge = createBadge(response.score, response.status);
                    resultBadge.style.marginLeft = "10px";
                    resultBadge.style.display = "inline-block";
                    titleElement.appendChild(resultBadge);
                }
            }
        );
    } catch (error) {
        console.error("VeriJob Glassdoor Error:", error);
        loadingBadge.innerText = "Error";
        loadingBadge.style.backgroundColor = "#71717a";
    }
}

// Function to process Internshala Job Pages
async function processInternshalaJob() {
    const selectors = [
        "h1.heading_4_5.profile",
        ".heading_4_5.profile",
        "h1.profile-title",
        ".profile_on_detail_page",
        ".detail_header h1",
        ".individual_internship h1"
    ];

    let titleElement = null;
    for (const sel of selectors) {
        titleElement = document.querySelector(sel);
        if (titleElement) break;
    }

    if (titleElement && !titleElement.querySelector(".verijob-badge")) {
        console.log("Found Internshala Job Title:", titleElement.innerText);
        const jobUrl = window.location.href;

        const loadingBadge = document.createElement("span");
        loadingBadge.className = "verijob-badge verijob-loading";
        loadingBadge.innerText = "Analyzing...";
        loadingBadge.style.marginLeft = "10px";
        titleElement.appendChild(loadingBadge);

        try {
            chrome.runtime.sendMessage(
                { action: "verifyJob", url: jobUrl },
                (response) => {
                    loadingBadge.remove();
                    if (response && response.score !== undefined) {
                        const resultBadge = createBadge(response.score, response.status);
                        resultBadge.style.marginLeft = "10px";
                        resultBadge.style.display = "inline-block";
                        titleElement.appendChild(resultBadge);
                    }
                }
            );
        } catch (error) {
            console.error("VeriJob Internshala Error:", error);
            loadingBadge.innerText = "Error";
            loadingBadge.style.backgroundColor = "#71717a";
        }
    }
}

// Observer to handle Single Page App navigation
let processingTimeout = null;

const observer = new MutationObserver((mutations) => {
    // Debounce to avoid processing too frequently
    if (processingTimeout) clearTimeout(processingTimeout);

    processingTimeout = setTimeout(() => {
        if (window.location.hostname.includes("linkedin.com")) {
            processLinkedInJob();
        } else if (window.location.hostname.includes("naukri.com")) {
            processNaukriJob();
        } else if (window.location.hostname.includes("indeed.com")) {
            processIndeedJob();
        } else if (window.location.hostname.includes("glassdoor.com")) {
            processGlassdoorJob();
        } else if (window.location.hostname.includes("internshala.com")) {
            processInternshalaJob();
        }
    }, 500); // Wait 500ms after last change before processing
});

// Start observing with more specific config
observer.observe(document.body, {
    childList: true,
    subtree: true,
    attributes: false // Don't watch attribute changes, only DOM changes
});

// Initial run with delay to let page load
setTimeout(() => {
    console.log("VeriJob AI Extension Loaded");
    console.log("Current hostname:", window.location.hostname);

    if (window.location.hostname.includes("linkedin.com")) {
        processLinkedInJob();
    } else if (window.location.hostname.includes("naukri.com")) {
        processNaukriJob();
    } else if (window.location.hostname.includes("indeed.com")) {
        processIndeedJob();
    } else if (window.location.hostname.includes("glassdoor.com")) {
        console.log("🎯 VeriJob: Detected Glassdoor, will process job listings...");
        processGlassdoorJob();
    } else if (window.location.hostname.includes("internshala.com")) {
        processInternshalaJob();
    }
}, 2000);
