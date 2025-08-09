from flask import Flask, request, jsonify, send_file, Response
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
DATA_SERVICE_URL = os.environ.get('DATA_SERVICE_URL', "http://localhost:8002")

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
    :param dataset: Optional dataset file to be used by the script.
    :param created_by: The user who created the task. always will be "admin" # TODO: change to the actual user when we have a user service
    :param requested_workers_amount: The number of workers requested for the task. default is 1. TODO: change to the actual number of workers 
    :param status: The initial status of the task. always will be "submitted"
    :return: A JSON response indicating the success or failure of the task submission, including the task details.
    """
    try:
        data = request.form.to_dict()

        # Check for script file
        if 'file' not in request.files:
            logger.error("No file in request.files")
            return jsonify({'error': 'No file provided'}), 400
            
        file = request.files['file']
        if not file.filename:
            logger.error("No filename in file object")
            return jsonify({'error': 'No file selected'}), 400
        
        # Upload script
        script_upload = storage_service.upload_file(file)
        logger.info(f"Script upload result: {script_upload}")
        if script_upload['status'] == 'error':
            logger.error(f"Upload error: {script_upload['message']}")
            return jsonify({'error': script_upload['message']}), 500

        # Optional: dataset upload
        dataset_upload = None
        if 'dataset' in request.files and request.files['dataset'].filename:
            dataset_file = request.files['dataset']
            dataset_upload = storage_service.upload_file(dataset_file)
            logger.info(f"Dataset upload result: {dataset_upload}")
            if dataset_upload['status'] == 'error':
                logger.error(f"Dataset upload error: {dataset_upload['message']}")
                return jsonify({'error': dataset_upload['message']}), 500
            
        # Create task payload
        payload = {
            **{key: val for key, val in data.items() if key in ['created_by', 'requested_workers_amount']},
            'file_path': script_upload.get('file_path'),
            'file_name': script_upload.get('file_name'),
        }
        # Include dataset path if provided
        if dataset_upload and dataset_upload.get('file_path'):
            payload['dataset_path'] = dataset_upload.get('file_path')

        task = task_service.create_task(payload)

        # Enqueue for processing
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


@app.route('/api/tasks/<task_id>/results', methods=['GET'])
def download_results(task_id: str):
    """Stream task results file to the client if available."""
    try:
        task = task_service.get_task(task_id)
        results_path = task.get('results_path') if task else None
        if not task or not results_path:
            return jsonify({"error": "Results not available"}), 404

        # proxy stream from data-service
        import requests
        ds_url = f"{DATA_SERVICE_URL}/storage/get-file"
        r = requests.get(ds_url, params={"file_path": results_path}, stream=True)
        if not r.ok:
            return jsonify({"error": "Failed to fetch results"}), r.status_code

        # Derive filename from path
        filename = os.path.basename(results_path)
        headers = {
            'Content-Disposition': f'attachment; filename={filename}'
        }
        return Response(r.iter_content(chunk_size=8192), headers=headers, content_type='application/octet-stream')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True) 