import asyncio
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.connection import manager
from app.services.tts_service import generate_audio_base64

app = FastAPI(title="SilentSpeak Backend MVP")

# Mock dictionary for rapid testing before ML integration
MOCK_WORDS = ["Hello", "Thank You", "Yes", "No", "Help", "Please"]


@app.get("/")
def read_root():
    return {"status": "SilentSpeak API is active"}


@app.websocket("/ws/translate")
async def websocket_translate(websocket: WebSocket):
    # Pass connection handling off to ConnectionManager
    await manager.connect(websocket)

    try:
        while True:
            # 1. Receive MediaPipe coordinates from frontend
            data = await websocket.receive_json()

            # 2. Simulate processing latency (~50ms)
            await asyncio.sleep(0.05)
            
            predicted_text = random.choice(MOCK_WORDS)
            
            audio_base64 = await generate_audio_base64(predicted_text)

            # 3. Generate mock payload response
            response_payload = {
                "text": predicted_text,
                "confidence": round(random.uniform(0.85, 0.99), 2),
                "audio": audio_base64,
                "status": "success",
            }

            # 4. Stream response back over the open WebSocket
            await manager.send_json(response_payload, websocket)

    except WebSocketDisconnect:
        # Handle client disconnects cleanly without crashing the server
        manager.disconnect(websocket)
