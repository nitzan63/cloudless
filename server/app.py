from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from services.task_service import TaskService
from services.storage_service import StorageService
from services.rabbitmq_service import RabbitMQService
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize storage service
storage_service = StorageService(os.environ.get('DATA_SERVICE_URL', "http://localhost:8002"))
task_service = TaskService(os.environ.get('DATA_SERVICE_URL', "http://localhost:8002"))
rabbitmq_service = RabbitMQService()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/api/tasks', methods=['POST'])
def submit_task():
    """
    Submit a new task for execution

    This endpoint accepts a POST request with a file and form data. The file is uploaded to a storage service, and the form data is used to create a new task in the task service. The task is then sent to a message queue for processing.

    :param file: The file to be uploaded and associated with the task. python script.
    :param created_by: The user who created the task. always will be "admin" # TODO: change to the actual user when we have a user service
    :param requested_workers_amount: The number of workers requested for the task. default is 1. TODO: change to the actual number of workers 
    :param status: The initial status of the task. always will be "submitted"
    # TODO: think about adding a URL for the dataset as a parameter
    :return: A JSON response indicating the success or failure of the task submission, including the task details.
    """
    try:
        data = request.form.to_dict()

        # File save
        if 'file' not in request.files:
            logger.error("No file in request.files")
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if not file.filename:
            logger.error("No filename in file object")
            return jsonify({'error': 'No file selected'}), 400
        
        # Upload to GCS
        result = storage_service.upload_file(file)
        logger.info(f"Upload result: {result}")
        
        if result['status'] == 'error':
            logger.error(f"Upload error: {result['message']}")
            return jsonify({'error': result['message']}), 500
            
        # Use service to create task
        task = task_service.create_task(
            {
                **{key: val for key, val in data.items() if key in ['created_by', 'requested_workers_amount']},
                **{key: val for key, val in result.items() if key in ['file_path', 'file_name']}
            }
        )

        rabbitmq_service.send_message(task['task_id'])

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


@app.route('/api/tasks', methods=['GET'])
def get_all_tasks():
    """Get all tasks"""
    try:
        tasks = task_service.list_tasks()
        if tasks:
            return jsonify(tasks), 200
        else:
            return jsonify({"error": "No tasks"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)