// webcam.js
// Handles the camera feed and MediaPipe Hands landmark detection.
// Depends on websocket.js being loaded first (uses sendLandmarks / resetLastSpokenWord).

// DOM elements this file needs (defined in index.html)
const videoElement = document.getElementById("webcam");
const canvasElement = document.getElementById("output_canvas");
const canvasCtx = canvasElement.getContext("2d");

// 1. Configure MediaPipe Hands Engine
const hands = new Hands({
    locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`,
});

hands.setOptions({
    maxNumHands: 1, // Track 1 hand for simplicity
    modelComplexity: 1, // Balanced accuracy & performance
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5,
});

// 2. Callback function executed whenever MediaPipe processes a video frame
hands.onResults((results) => {
    // Draw current camera frame onto the canvas
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);

    // If a hand is visible in the frame
    if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
        const landmarks = results.multiHandLandmarks[0];

        // A. Draw skeleton connectors and landmark dots on canvas
        drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS, { color: "#7C7AED", lineWidth: 2 });
        drawLandmarks(canvasCtx, landmarks, { color: "#F5F4FF", lineWidth: 1 });

        // B. Transmit keypoint coordinate array over WebSocket if open
        sendLandmarks(landmarks);
    } else {
        // Reset last spoken word when hand leaves screen so signing it again re-triggers audio
        resetLastSpokenWord();
    }

    canvasCtx.restore();
});

// 3. Start Camera Request Loop using MediaPipe Camera Helper
const camera = new Camera(videoElement, {
    onFrame: async () => {
        await hands.send({ image: videoElement });
    },
    width: 640,
    height: 480,
});

camera.start();