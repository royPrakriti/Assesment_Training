from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class Product(BaseModel):
    id: int
    title: str
    status: str

app = FastAPI()

task_day = [
    {"id":1, "title": "Learn FastAPI","status":"Pending"},
    {"id":2, "title": "Practice pytest","status":"Completed"},
    {"id":3, "title": "Test API","status":"Pending"},
]

@app.get("/tasks")
def get_tasks():
    return task_day

@app.post("/tasks")
def create_task(task: Product):
    task_data = task.model_dump()
    task_day.append(task_data)
    return task_data
    return {"message": "Task added successfully"}

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in task_day:
        if task["id"] == task_id:
            return task

    raise HTTPException(status_code=404, detail="Task not found")

@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: Product):
    for task in task_day:
        if task["id"] == task_id:
            task["title"] = updated_task.title
            task["status"] = updated_task.status

            return {
                "message": "Task updated successfully",
                "task": task
            }

    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    for task in task_day:
        if task["id"] == task_id:
            task_day.remove(task)
            return {"message": "Task deleted successfully"}

    return {"message": "Task not found"}