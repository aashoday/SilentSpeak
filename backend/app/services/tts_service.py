import base64
import io
import edge_tts

DEFAULT_VOICE = "en-US-AvaNeural"


async def generate_audio_base64(text: str, voice: str = DEFAULT_VOICE) -> str | None:
    """Converts a text string into a Base64-encoded audio string using edge-tts.

    Returns None if text is empty or if synthesis fails (e.g., offline/network error).
    """
    # Guard against empty strings or non-speech fallback labels
    if not text or not text.strip() or text in ["No Hand Detected", "Unknown Gesture", "Invalid Data"]:
        return None

    try:
        # 1. Initialize edge-tts with rate="+15%" to speed up synthesis & delivery
        communicate = edge_tts.Communicate(text, voice, rate="+15%")

        # 2. Create an in-memory byte buffer (RAM storage)
        audio_buffer = io.BytesIO()

        # 3. Stream audio chunk by chunk from edge-tts into our buffer
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                data = chunk.get("data")
                if data is not None:
                    audio_buffer.write(data)

        # 4. Get all raw audio bytes from the buffer
        raw_audio_bytes = audio_buffer.getvalue()

        if not raw_audio_bytes:
            return None

        # 5. Convert raw audio bytes into a Base64 text string
        base64_audio = base64.b64encode(raw_audio_bytes).decode("utf-8")

        return base64_audio

    except Exception as e:
        # Gracefully swallow network/DNS errors so WebSocket stays open
        print(f"⚠️ [TTS Service Warning] Could not generate audio (DNS/Network issue): {e}")
        return None
