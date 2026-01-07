#!/usr/bin/env python3
"""
People Detection ML Service
Flask API that receives image frames and returns people count using YOLO11.
"""

from flask import Flask, request, jsonify
import cv2
import numpy as np
import base64
from ultralytics import YOLO
from datetime import datetime
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load YOLO model at startup
MODEL_PATH = os.getenv('MODEL_PATH', '/app/yolo11n.pt')
logger.info(f"Loading YOLO model from {MODEL_PATH}...")
try:
    model = YOLO(MODEL_PATH)
    logger.info("YOLO model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load YOLO model: {e}")
    raise


def decode_frame(base64_string):
    """
    Decode base64 string to OpenCV image.
    
    Args:
        base64_string: Base64 encoded image
        
    Returns:
        numpy.ndarray: OpenCV image
    """
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64 to bytes
        img_bytes = base64.b64decode(base64_string)
        
        # Convert to numpy array
        nparr = np.frombuffer(img_bytes, np.uint8)
        
        # Decode to image
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Failed to decode image")
            
        return img
    except Exception as e:
        logger.error(f"Error decoding frame: {e}")
        raise


def detect_people(frame):
    """
    Detect people in a frame using YOLO.
    
    Args:
        frame: OpenCV image (numpy array)
        
    Returns:
        int: Number of people detected
    """
    try:
        # Run YOLO inference
        # class 0 is 'person' in COCO dataset
        # Using same parameters as original camera.py
        results = model(
            frame,
            imgsz=128,
            classes=[0],  # Only detect persons
            conf=0.42,    # Confidence threshold
            verbose=False,
            device="cpu"  # Can be changed to "cuda" if GPU available
        )
        
        # Count detected people
        num_people = len(results[0].boxes)
        
        logger.info(f"Detected {num_people} people")
        return num_people
        
    except Exception as e:
        logger.error(f"Error during detection: {e}")
        raise


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'people_detector',
        'model_loaded': model is not None,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/detect', methods=['POST'])
def detect():
    """
    Main detection endpoint.
    
    Expected JSON:
    {
        "frame": "base64_encoded_image_data"
    }
    
    Returns JSON:
    {
        "people_count": 5,
        "timestamp": "2026-01-07T10:15:00",
        "success": true
    }
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        
        if 'frame' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing "frame" field in request body'
            }), 400
        
        # Decode frame
        logger.info("Decoding frame...")
        frame = decode_frame(data['frame'])
        
        # Detect people
        logger.info("Running people detection...")
        people_count = detect_people(frame)
        
        # Return result
        return jsonify({
            'success': True,
            'people_count': people_count,
            'timestamp': datetime.now().isoformat()
        })
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        logger.error(f"Internal error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with service info."""
    return jsonify({
        'service': 'STEAM People Detection ML Service',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'detect': '/detect (POST)'
        }
    })


if __name__ == '__main__':
    # Run Flask app
    port = int(os.getenv('PORT', 5000))
    logger.info(f"Starting Flask server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
