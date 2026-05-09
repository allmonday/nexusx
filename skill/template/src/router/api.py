"""Phase 3: REST router — calls UseCaseService methods."""
from fastapi import APIRouter, HTTPException

from src.service.sprint.service import SprintService
from src.service.task.service import TaskService

route = APIRouter(prefix="/api")


@route.get("/tasks", tags=[TaskService.get_tag_name()])
async def get_tasks():
    return await TaskService.list_tasks()


@route.get("/tasks/by-sprint/{sprint_id}", tags=[TaskService.get_tag_name()])
async def get_tasks_by_sprint(sprint_id: int):
    return await TaskService.get_tasks_by_sprint(sprint_id=sprint_id)


@route.get("/sprints", tags=[SprintService.get_tag_name()])
async def get_sprints():
    return await SprintService.list_sprints()


@route.get("/sprints/{sprint_id}", tags=[SprintService.get_tag_name()])
async def get_sprint(sprint_id: int):
    result = await SprintService.get_sprint(sprint_id=sprint_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return result
