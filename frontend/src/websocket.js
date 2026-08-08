// Handles the connection to the FastAPI backend and incoming translation results.

// DOM elements this file needs (defined in index.html)
const statusEl = document.getElementById("status");
const statusDotEl = document.getElementById("status-dot");
const footerStatusEl = document.getElementById("footer-status");
const wordEl = document.getElementById("predicted-word");
const confidenceEl = document.getElementById("confidence-score");
const confidenceFillEl = document.getElementById("confidence-fill");

// Tracks the last spoken word so we don't replay audio for the same sign repeatedly
let lastSpokenWord = "";

// 1. Establish WebSocket connection to FastAPI backend
const ws = new WebSocket("ws://localhost:8000/ws/translate");

ws.onopen = () => {
    statusEl.innerText = "Connected & active";
    statusDotEl.classList.remove("is-error");
    statusDotEl.classList.add("is-live");
    if (footerStatusEl) footerStatusEl.innerText = "Connected";
};

ws.onclose = () => {
    statusEl.innerText = "Disconnected";
    statusDotEl.classList.remove("is-live");
    statusDotEl.classList.add("is-error");
    if (footerStatusEl) footerStatusEl.innerText = "Disconnected";
};

ws.onerror = (error) => {
    console.error("WebSocket Error:", error);
    statusEl.innerText = "Connection error";
    statusDotEl.classList.remove("is-live");
    statusDotEl.classList.add("is-error");
    if (footerStatusEl) footerStatusEl.innerText = "Connection error";
};

// Handle incoming prediction JSON from FastAPI backend
ws.onmessage = (event) => {
    const response = JSON.parse(event.data);

    // Update screen text immediately
    wordEl.innerText = response.text;
    const confidencePct = (response.confidence * 100).toFixed(1);
    confidenceEl.innerText = `${confidencePct}%`;
    if (confidenceFillEl) confidenceFillEl.style.width = `${confidencePct}%`;

    // Play audio ONLY when a new distinct word is detected
    if (
        response.audio &&
        response.text !== lastSpokenWord &&
        response.text !== "No Hand Detected" &&
        response.text !== "Unknown Gesture"
    ) {
        lastSpokenWord = response.text; // Update last spoken word

        const audioSource = "data:audio/mp3;base64," + response.audio;
        const audio = new Audio(audioSource);

        audio.play().catch((error) => {
            console.error("Audio playback error:", error);
        });
    }
};

// Helper so webcam.js can send landmark data without reaching into ws directly
function sendLandmarks(landmarks) {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ landmarks: landmarks }));
    }
}

// Helper so webcam.js can reset the spoken-word guard when the hand leaves frame
function resetLastSpokenWord() {
    lastSpokenWord = "";
}