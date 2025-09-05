from fastapi import APIRouter, HTTPException
from services.task_service import TaskService

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

