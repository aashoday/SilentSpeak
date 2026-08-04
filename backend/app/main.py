import asyncio
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.connection import manager
from app.services.tts_service import generate_audio_base64
from app.services.model_service import predict_gesture

app = FastAPI(title="SilentSpeak Backend MVP")


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

            # 2. Get prediction from Model Service 
            prediction = await predict_gesture(data)
            predicted_text = prediction["text"]
            confidence = prediction["confidence"]
            
            
            # 3. Generate matching audio from TTS service 
            audio_base64 = await generate_audio_base64(predicted_text)

            # 4. Generate mock payload response
            response_payload = {
                "text": predicted_text,
                "confidence": confidence,
                "audio": audio_base64,
                "status": "success",
            }

            # 5. Stream response back over the open WebSocket
            await manager.send_json(response_payload, websocket)
            
            await asyncio.sleep(0.01)

    except WebSocketDisconnect:
        # Handle client disconnects cleanly without crashing the server
        manager.disconnect(websocket)
