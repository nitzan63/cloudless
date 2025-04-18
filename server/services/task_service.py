import ray
import logging
from services.script_processor import ScriptProcessor
from services.storage_service import StorageService
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class TaskService:
    """Handles all task-related business logic"""
    
    def __init__(self):
        """Initialize the task service"""
        self.script_processor = ScriptProcessor()
        self.storage_service = StorageService()
        
    def get_upload_urls(self, script_filename: str, data_filename: str) -> dict:
        """
        Get signed URLs for uploading script and data files directly to GCS.
        
        Args:
            script_filename: Name of the Python script file
            data_filename: Name of the data file
            
        Returns:
            dict: Contains upload URLs and file paths
        """
        try:
            # Get upload URLs for both files
            script_upload = self.storage_service.get_upload_url(script_filename)
            data_upload = self.storage_service.get_upload_url(data_filename)
            
            return {
                "script": {
                    "upload_url": script_upload['url'],
                    "file_path": script_upload['file_path']
                },
                "data": {
                    "upload_url": data_upload['url'],
                    "file_path": data_upload['file_path']
                }
            }
        except Exception as e:
            logger.error(f"Error getting upload URLs: {str(e)}")
            raise

    def submit_task(self, script_path: str, data_path: str, requirements: Dict) -> Dict:
        """
        Submit a task for execution.
        
        Args:
            script_path: GCS path to the Python script
            data_path: GCS path to the data file
            requirements: Dictionary of resource requirements
            
        Returns:
            Dict containing task_id and status
        """
        try:
            # 1. Download the script
            script_content: str = self.storage_service.download_file(script_path)
            if not script_content or not isinstance(script_content, str):
                raise ValueError(f"Failed to download script from {script_path} or invalid content type")
                
            # 2. Wrap the script (includes validation)
            execute_func = self.script_processor.wrap_script(script_content)
            logger.info("Script wrapped successfully")
            
            # 3. Submit to Ray
            task_ref = execute_func.remote(data_path, **requirements)
            
            # Return task information
            return {
                "task_id": task_ref.task_id().hex(),
                "status": "submitted",
                "script_path": script_path,
                "data_path": data_path
            }
            
        except Exception as e:
            logger.error(f"Error submitting task: {str(e)}")
            raise

    def get_task_status(self, task_id: str) -> Dict:
        """
        Get the status of a specific task.
        
        Args:
            task_id: The ID of the task to check
            
        Returns:
            Dict containing task status and result if completed
        """
        try:
            # Get the task reference
            task_ref = ray.get_runtime_context().get_task_ref(task_id)
            
            # Check if the task is done
            if ray.get(task_ref.done()):
                # Get the result
                result = ray.get(task_ref)
                return {
                    "task_id": task_id,
                    "status": "completed",
                    "result": result
                }
            else:
                return {
                    "task_id": task_id,
                    "status": "running"
                }
                
        except Exception as e:
            logger.error(f"Error getting task status: {str(e)}")
            return {
                "task_id": task_id,
                "status": "error",
                "error": str(e)
            }

    def cancel_task(self, task_id: str) -> Dict:
        """
        Cancel a running task.
        
        Args:
            task_id: The ID of the task to cancel
            
        Returns:
            Dict containing cancellation status
        """
        try:
            task_ref = ray.get_runtime_context().get_task_ref(task_id)
            ray.cancel(task_ref)
            return {
                "task_id": task_id,
                "status": "cancelled"
            }
        except Exception as e:
            logger.error(f"Error cancelling task: {str(e)}")
            return {
                "task_id": task_id,
                "status": "error",
                "error": str(e)
            }

    @staticmethod
    def validate_task_data(task_data):
        """Validate task submission data"""
        required_fields = ['task_type', 'resource_requirements']
        for field in required_fields:
            if field not in task_data:
                return False, f"Missing required field: {field}"
        return True, None

    @staticmethod
    def create_task(task_data):
        """Create a new task with the given data"""
        # TODO: Implement actual task creation logic
        # For now, just return a mock task
        return {
            "task_id": "sample-task-id",
            "status": "queued",
            "task_type": task_data['task_type'],
            "resource_requirements": task_data['resource_requirements']
        } 