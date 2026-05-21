# UseCase + FastAPI

Using the same UseCaseService class in FastAPI — routes are thin wrappers, business logic stays in the service.

## Route Definitions

```python
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/api/sprints", tags=[SprintService.get_tag_name()])
async def get_sprints():
    return await SprintService.list_sprints()

@app.get("/api/sprints/{sprint_id}", tags=[SprintService.get_tag_name()])
async def get_sprint(sprint_id: int):
    result = await SprintService.get_sprint(sprint_id=sprint_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return result
```

## OpenAPI Grouping

`get_tag_name()` returns the class name as an OpenAPI-compatible tag name:

```python
SprintService.get_tag_name()  # → "SprintService"
TaskService.get_tag_name()    # → "TaskService"
```

FastAPI's `/docs` page automatically groups routes by service tags.

## Architecture Benefits

```
UseCaseService subclass ──┬── MCP server (AI agents)
                         └── FastAPI routes (REST API)
```

- **Single definition of business logic**: Changes only need to be made in one place
- **Thin route wrappers**: FastAPI routes only handle parameter passing and exception handling
- **Type safety**: The same DTO types are reused across both modes
- **Auto-generated OpenAPI**: FastAPI automatically generates openapi.json, usable for TypeScript SDK generation

## Complete Example

```python
from fastapi import FastAPI
from nexusx.use_case import UseCaseService, UseCaseAppConfig, create_use_case_mcp_server

# Service definition
class SprintService(UseCaseService):
    @classmethod
    async def list_sprints(cls) -> list[SprintSummary]:
        ...

    @classmethod
    async def get_sprint(cls, sprint_id: int) -> SprintSummary | None:
        ...

# MCP mode
mcp = create_use_case_mcp_server(
    apps=[
        UseCaseAppConfig(name="project", services=[SprintService]),
    ],
    name="Sprint API",
)

# FastAPI mode
app = FastAPI()

@app.get("/api/sprints", tags=[SprintService.get_tag_name()])
async def get_sprints():
    return await SprintService.list_sprints()

@app.get("/api/sprints/{sprint_id}", tags=[SprintService.get_tag_name()])
async def get_sprint(sprint_id: int):
    result = await SprintService.get_sprint(sprint_id=sprint_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Sprint not found")
    return result
```

## Next Steps

- [UseCase Service](./use_case_service.md) — Complete UseCaseService definition
- [Core API Mode](../guide/core_api.md) — DTO definition and resolve patterns
