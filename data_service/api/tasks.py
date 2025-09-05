from fastapi import APIRouter, HTTPException
from services.task_service import TaskService
import json

router = APIRouter()
task_service = TaskService()

@router.post("/")
def create_task(payload: dict):
    try:
        task_id = task_service.create_task(**payload)
        return {"status": "success", "task_id": task_id}
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{task_id}")
def get_task(task_id: str):
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/exec/{task_id}")
def get_task_to_execute(task_id: str):
    print("TASKS:", task_id)
    file_data = task_service.get_task_to_execute(task_id)
    if not file_data:
        raise HTTPException(status_code=404, detail="Task not found")
    return file_data

@router.patch("/{task_id}")
def update_task(task_id: str, payload: dict):
    updated = task_service.update_task(task_id, **payload)
    return {"status": "updated" if updated else "not modified"}

@router.delete("/{task_id}")
def delete_task(task_id: str):
    task_service.delete_task(task_id)
    return {"status": "deleted"}

@router.get("/")
def list_tasks():
    return task_service.list_tasks()

@router.get("/not-finished/all")
def get_tasks_not_finished():
    return task_service.get_tasks_not_finished()

@router.get("/{task_id}/logs")
def get_task_logs(task_id: str):
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # If logs are stored in the database, return them
    if task.get('logs'):
        try:
            return {"logs": json.loads(task['logs'])}
        except (json.JSONDecodeError, TypeError):
            return {"logs": task['logs']}
    
    # If no logs in database, try to fetch from Livy if batch_job_id exists
    if task.get('batch_job_id'):
        try:
            from services.livy_service import LivyService
            livy_service = LivyService("http://wireguard:8998")  # Livy shares network with wireguard
            logs_response = livy_service.get_batch_logs(task['batch_job_id'], verbose=False)
            if logs_response.status_code == 200:
                logs_data = logs_response.json()
                # Store logs in database for future use
                task_service.update_task(task_id, {"logs": json.dumps(logs_data)})
                return {"logs": logs_data}
        except Exception as e:
            print(f"Error fetching logs from Livy: {e}")
    
    return {"logs": None, "message": "No logs available"}
