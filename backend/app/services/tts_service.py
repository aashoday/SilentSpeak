import base64
import io
import edge_tts

# Define a default neural voice (e.g., en-US-AriaNeural)
DEFAULT_VOICE = "mr-IN-AarohiNeural"


async def generate_audio_base64(text: str, voice: str = DEFAULT_VOICE) -> str | None:
    """Converts a text string into a Base64-encoded audio string using edge-tts.

    Returns None if text is empty.
    """
    if not text.strip():
        return None

    # 1. Initialize the edge-tts communicator
    communicate = edge_tts.Communicate(text, voice)

    # 2. Create an in-memory byte buffer (RAM storage)
    audio_buffer = io.BytesIO()

    # 3. Stream audio chunk by chunk from edge-tts into our buffer
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_buffer.write(chunk["data"])

    # 4. Get all raw audio bytes from the buffer
    raw_audio_bytes = audio_buffer.getvalue()

    # 5. Convert raw audio bytes into a Base64 text string
    base64_audio = base64.b64encode(raw_audio_bytes).decode("utf-8")

    return base64_audio
