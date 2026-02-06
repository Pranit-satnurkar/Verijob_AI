// content.js - VeriJob AI

console.log("VeriJob AI Extension Loaded");

// Helper to create the badge element
function createBadge(score, status) {
    const badge = document.createElement("div");
    badge.className = "verijob-badge";

    const isVerified = status === 'Verified' || score > 70;
    badge.style.backgroundColor = isVerified ? "#22c55e" : "#ef4444"; // Green or Red

    badge.innerHTML = `
    <span style="font-weight:bold;">${isVerified ? "✅ Verified" : "⚠️ Suspicious"}</span>
    <span style="margin-left:5px; opacity:0.9;">${score}%</span>
  `;

    // Add tooltip or click handler later
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

// Observer to handle Single Page App navigation (LinkedIn loves to reload content without refreshing)
const observer = new MutationObserver((mutations) => {
    // Debounce or just simply try to process if we see relevant changes
    processLinkedInJob();
});

observer.observe(document.body, { childList: true, subtree: true });

// Initial run
setTimeout(processLinkedInJob, 2000);
