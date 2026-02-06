document.addEventListener('DOMContentLoaded', async () => {
    const statusSpan = document.getElementById('backend-status');
    try {
        const res = await fetch('http://localhost:8000/docs'); // Simple check
        if (res.ok) {
            statusSpan.innerText = "Online 🟢";
            statusSpan.style.color = "#4ade80";
        } else {
            statusSpan.innerText = "Error 🔴";
        }
    } catch (e) {
        statusSpan.innerText = "Offline 🔴";
    }
});
