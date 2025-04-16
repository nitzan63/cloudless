from flask import Flask, request, jsonify
from flask_cors import CORS
from services.task_service import TaskService
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/api/tasks', methods=['POST'])
def submit_task():
    """Submit a new task for execution"""
    try:
        data = request.get_json()
        
        # Use service for validation
        is_valid, error_message = TaskService.validate_task_data(data)
        if not is_valid:
            return jsonify({"error": error_message}), 400
            
        # Use service to create task
        task = TaskService.create_task(data)
        return jsonify({
            "message": "Task received successfully",
            "task": task
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Get the status of a specific task"""
    try:
        task_status = TaskService.get_task_status(task_id)
        return jsonify(task_status), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Get port from environment variable
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting server on port {port}")
    logger.info(f"Environment variables: {os.environ}")
    app.run(host='0.0.0.0', port=port, debug=True) 