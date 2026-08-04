# app/services/model_service.py
import random
from typing import List, Dict, Any  # noqa: UP035

# Mock words to return until the ML model weights file is integrated
MOCK_PREDICTIONS = ["Hello", "Thank You", "Yes", "No", "Help", "Please"]

async def predict_gesture(landmarks: List[Any]) -> Dict[str, Any]:  # noqa: UP006
    """
    Simulates ML model inference on incoming landmark coordinates.
    
    Args:
        landmarks: Raw coordinate data received from frontend WebSockets.
        
    Returns:
        Dict containing predicted text label and confidence score.
    """
    # For now, pick a random gesture word to mock the model's output
    predicted_word = random.choice(MOCK_PREDICTIONS)
    confidence = round(random.uniform(0.85, 0.99), 2)
    
    return {
        "text": predicted_word,
        "confidence": confidence
    }
