import os
import logging
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from services.task_service import TaskService
from services.storage_service import StorageService

# TODO: Ray Integration and System Improvements
# 1. Ray Connectivity
#    - Add RAY_ADDRESS environment variable to Cloud Run deployment
#    - Implement retry mechanism for Ray connection attempts
#    - Add detailed error logging for Ray initialization failures
#
# 2. Degraded Mode Functionality
#    - Define and implement features that should work without Ray
#    - Add fallback mechanisms for critical functions
#    - Create graceful degradation strategy
#
# 3. Monitoring and Alerts
#    - Set up structured logging for Ray connection status
#    - Configure alerts for Ray disconnection events
#    - Add metrics collection for Ray-related operations
#
# 4. Security
#    - Review and secure Ray cluster communication
#    - Implement proper access control for Ray resources
#    - Add authentication for Ray client connections
#
# 5. Testing
#    - Add unit tests for Ray connection scenarios
#    - Create integration tests for degraded mode
#    - Implement health check tests

# Re-enable Ray
try:
    import ray
    ray_import_success = True
except ImportError:
    ray_import_success = False
    logging.error("Failed to import Ray package")

from services.storage_service import StorageService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# This should appear in logs if our changes are being applied
print("CLOUDLESS SERVER STARTING - VERSION 2025-04-18-with-ray", file=sys.stderr)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Ray safely
ray_initialized = False
ray_address = os.getenv('RAY_ADDRESS')

if ray_import_success and ray_address:
    try:
        logger.info(f"Initializing Ray with address: {ray_address}")
        ray.init(address=ray_address)
        ray_initialized = True
        logger.info("Ray initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Ray: {str(e)}")
        # Don't raise the exception, let the app start without Ray
else:
    logger.warning("Ray not initialized - either import failed or RAY_ADDRESS not set")

# Initialize services
storage_service = StorageService()
task_service = TaskService()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            "status": "healthy",
            "ray": "connected" if ray_initialized else "disconnected",
            "version": "2025-04-18-with-ray"
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route('/api/upload-url', methods=['POST'])
def get_upload_url():
    """Get a signed URL for direct upload to GCS"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        file_type = data.get('type')
        
        if not filename or not file_type:
            return jsonify({'error': 'Missing filename or type'}), 400
            
        result = storage_service.get_upload_url(filename)
        if result['status'] == 'error':
            return jsonify({'error': result['message']}), 500
            
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error getting upload URL: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def submit_task():
    """Submit a new task for execution"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['script_path', 'data_path', 'requirements']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
                
        # Submit task using TaskService
        result = task_service.submit_task(
            script_path=data['script_path'],
            data_path=data['data_path'],
            requirements=data['requirements']
        )
        
        return jsonify(result), 201
        
    except Exception as e:
        logger.error(f"Error submitting task: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """Get the status of a specific task"""
    try:
        status = task_service.get_task_status(task_id)
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks/<task_id>/cancel', methods=['POST'])
def cancel_task(task_id):
    """Cancel a running task"""
    try:
        result = task_service.cancel_task(task_id)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error cancelling task: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    host = os.environ.get('HOST', '0.0.0.0')
    logger.info(f"Starting server on port {port}")
    logger.info(f"Environment variables: {os.environ}")
    app.run(host=host, port=port) 