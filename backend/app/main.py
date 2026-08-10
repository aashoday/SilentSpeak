import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.connection import manager
from app.services.model_service import predict_gesture
from app.services.tts_service import generate_audio_base64

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
            # 1. Receive JSON payload from frontend
            data = await websocket.receive_json()

            # 2. Extract the actual landmarks array from the dictionary
            landmarks = data.get("landmarks", [])

            # 3. Get prediction from Model Service using the landmarks list
            prediction = await predict_gesture(landmarks)
            predicted_text = prediction["text"]
            confidence = prediction["confidence"]

            # 4. Generate audio from TTS service (only when a valid word is detected)
            audio_base64 = await generate_audio_base64(predicted_text)

            # 5. Build payload response
            response_payload = {
                "text": predicted_text,
                "confidence": confidence,
                "audio": audio_base64 or "",
                "status": "success",
            }

            # 6. Stream response back over the open WebSocket
            await manager.send_json(response_payload, websocket)

            # Prevent CPU hogging in high-frequency socket loop
            await asyncio.sleep(0.01)

    except WebSocketDisconnect:
        # Handle client disconnects cleanly without crashing the server
        manager.disconnect(websocket)
    except Exception as e:
        print(f"⚠️ [WS Endpoint Error]: {e}")
        manager.disconnect(websocket)
