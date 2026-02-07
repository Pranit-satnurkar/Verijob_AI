// background.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "verifyJob") {
        // Use localhost for development
        const apiUrl = "http://localhost:8000/verify";

        // Handle both message formats: { data: {...} } and { url: "..." }
        const payload = request.data || { url: request.url, content: request.content || "" };

        fetch(apiUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        })
            .then(response => response.json())
            .then(data => sendResponse({ success: true, score: data.score, status: data.status, data: data }))
            .catch(error => sendResponse({ success: false, error: error.message }));

        return true; // Keep the message channel open for async response
    }
});
