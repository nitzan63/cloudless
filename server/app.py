from flask import Flask, request, jsonify
from flask_cors import CORS
from services.task_service import TaskService
from db.postgres.postgres_db import PostgresDB
import os
import logging
from config import get_storage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize storage service
storage_service = get_storage()
pg_db = PostgresDB()
task_service = TaskService(pg_db)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload any file"""
    logger.info("Upload endpoint hit")
    logger.info(f"Request files: {request.files}")
    logger.info(f"Request form: {request.form}")
    try:
        if 'file' not in request.files:
            logger.error("No file in request.files")
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if not file.filename:
            logger.error("No filename in file object")
            return jsonify({'error': 'No file selected'}), 400
            
        # Read file content
        file_content = file.read()
        logger.info(f"File content read, size: {len(file_content)} bytes")
        
        # Upload to GCS
        result = storage_service.upload_file(file_content, file.filename)
        logger.info(f"Upload result: {result}")
        
        if result['status'] == 'error':
            logger.error(f"Upload error: {result['message']}")
            return jsonify({'error': result['message']}), 500
            
        return jsonify(result), 201
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def submit_task():
    """Submit a new task for execution"""
    try:
        data = request.get_json()
            
        # Use service to create task
        task = task_service.create_task(**data)
        return jsonify({
            "message": "Task received successfully",
            "task": task
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get a task by its ID"""
    try:
        task = task_service.get_task(task_id)
        if task:
            return jsonify(task), 200
        else:
            return jsonify({"error": "Task not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @app.route('/api/tasks/<task_id>', methods=['GET'])
# def get_task_status(task_id):
#     """Get the status of a specific task"""
#     try:
#         task_status = TaskService.get_task_status(task_id)
#         return jsonify(task_status), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True) 