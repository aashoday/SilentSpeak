from typing import Any, Dict, List  # noqa: UP035


def extract_coordinate(landmark: Any, axis: str = "y") -> float:
    """
    Safely extracts a specific axis coordinate (x, y, or z) from a landmark point,
    handling both dictionary formats {'x': ..., 'y': ...} and fallback list formats.
    """
    if isinstance(landmark, dict):
        return float(landmark.get(axis, 0.0))
    elif isinstance(landmark, (list, tuple)):
        # Mapping index positions for list fallback: x=0, y=1, z=2
        axis_indices = {"x": 0, "y": 1, "z": 2}
        idx = axis_indices.get(axis, 1)
        if len(landmark) > idx:
            return float(landmark[idx])
    return 0.0


async def predict_gesture(landmarks: List[Any]) -> Dict[str, Any]:  # noqa: UP006
    """
    Processes the raw 21 MediaPipe hand landmarks received over WebSockets.

    Args:
        landmarks: List of 21 landmark items directly from MediaPipe JS SDK.

    Returns:
        Dict: Predicted word label and confidence score.
    """
    # 1. Validation Guard: Check if a valid hand was detected (21 keypoints required)
    if not landmarks or len(landmarks) < 21:
        return {"text": "No Hand Detected", "confidence": 0.0}

    try:
        # 2. Extract key finger tip and knuckle Y-coordinates
        # MediaPipe Landmark Index Map:
        # Index Finger:  Tip = 8,  Knuckle = 6
        # Middle Finger: Tip = 12, Knuckle = 10
        # Ring Finger:   Tip = 16, Knuckle = 14
        # Pinky Finger:  Tip = 20, Knuckle = 18

        index_tip_y = extract_coordinate(landmarks[8], "y")
        index_knuckle_y = extract_coordinate(landmarks[6], "y")

        middle_tip_y = extract_coordinate(landmarks[12], "y")
        middle_knuckle_y = extract_coordinate(landmarks[10], "y")

        ring_tip_y = extract_coordinate(landmarks[16], "y")
        ring_knuckle_y = extract_coordinate(landmarks[14], "y")

        pinky_tip_y = extract_coordinate(landmarks[20], "y")
        pinky_knuckle_y = extract_coordinate(landmarks[18], "y")

        # 3. Geometric Rules (In screen coordinates, smaller Y value means higher on screen)
        index_extended = index_tip_y < index_knuckle_y
        middle_extended = middle_tip_y < middle_knuckle_y
        ring_extended = ring_tip_y < ring_knuckle_y
        pinky_extended = pinky_tip_y < pinky_knuckle_y

        # Rule 1: Open Palm ✋ -> "Hello"
        if index_extended and middle_extended and ring_extended and pinky_extended:
            return {"text": "Hello ✋", "confidence": 0.98}

        # Rule 2: Peace Sign ✌️ -> "Peace"
        if (
            index_extended
            and middle_extended
            and not ring_extended
            and not pinky_extended
        ):
            return {"text": "Peace ✌️", "confidence": 0.95}

        # Rule 3: Pointing 👆 -> "One"
        if (
            index_extended
            and not middle_extended
            and not ring_extended
            and not pinky_extended
        ):
            return {"text": "One 👆", "confidence": 0.92}

        # Rule 4: Closed Fist ✊ -> "Stop"
        if (
            not index_extended
            and not middle_extended
            and not ring_extended
            and not pinky_extended
        ):
            return {"text": "Stop ✊", "confidence": 0.90}

        # Default fallback for unrecognized positions
        return {"text": "Unknown Gesture", "confidence": 0.50}

    except Exception as e:
        print(f"⚠️ [Model Service Extractor Error]: {e}")
        return {"text": "Invalid Data", "confidence": 0.0}
