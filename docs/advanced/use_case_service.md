# UseCase Service

UseCaseService lets you define business logic as service classes that serve both MCP and web frameworks — one definition, two presentations.

> **Prerequisites**: [Core API Mode](../guide/core_api.md) — ErManager + DefineSubset + Resolver. UseCaseService wraps Core API DTOs into business methods.
>
> **Live demo**: See [`demo/use_case/mcp_server.py`](https://github.com/allmonday/sqlmodel-nexus/blob/master/demo/use_case/mcp_server.py) for a working MCP server — and [`demo/use_case/fastapi.py`](https://github.com/allmonday/sqlmodel-nexus/blob/master/demo/use_case/fastapi.py) for the same services exposed as REST.

## Design Philosophy

```
UseCaseService subclass ──┬── MCP server (AI agents, four-layer progressive discovery)
                         └── FastAPI routes (REST API, OpenAPI docs)
```

## Defining a UseCaseService

`UseCaseService` subclasses declare `async classmethod` methods. The metaclass auto-discovers public methods:

```python
from sqlmodel_nexus.use_case import UseCaseService

class SprintService(UseCaseService):
    """Sprint management service."""

    @classmethod
    async def list_sprints(cls) -> list[SprintSummary]:
        """Get all sprints with their task counts."""
        stmt = build_dto_select(SprintSummary)
        async with async_session() as session:
            rows = (await session.exec(stmt)).all()
        dtos = [SprintSummary(**dict(row._mapping)) for row in rows]
        return await Resolver().resolve(dtos)

    @classmethod
    async def get_sprint(cls, sprint_id: int) -> SprintSummary | None:
        """Get a sprint by ID."""
        stmt = build_dto_select(SprintSummary, where=Sprint.id == sprint_id)
        async with async_session() as session:
            rows = (await session.exec(stmt)).all()
        if not rows:
            return None
        dto = SprintSummary(**dict(rows[0]._mapping))
        return await Resolver().resolve(dto)
```

## Exposing to MCP

Four-layer progressive discovery: app discovery → service list → method details → execution.

```python
from sqlmodel_nexus.use_case import UseCaseAppConfig, create_use_case_mcp_server

mcp = create_use_case_mcp_server(
    apps=[
        UseCaseAppConfig(
            name="project",
            services=[SprintService, TaskService],
            description="Project management",
        ),
    ],
    name="Project UseCase API",
)
mcp.run()  # stdio mode
```

### MCP Tools

| Tool | Purpose |
|------|---------|
| `list_apps()` | Discover available apps |
| `list_services(app_name)` | List services and method counts in an app |
| `describe_service(app_name, service_name)` | Method signatures (SDL format) + DTO type definitions |
| `call_use_case(app_name, service_name, method_name, params)` | Execute method |

### describe_service Output

```json
{
  "name": "SprintService",
  "methods": [
    {"name": "list_sprints", "signature_sdl": "list_sprints(): [SprintSummary!]!"},
    {"name": "get_sprint", "signature_sdl": "get_sprint(sprint_id: Int!): SprintSummary"}
  ],
  "types": "type SprintSummary {\n  id: Int\n  name: String!\n  tasks: [TaskSummary!]!\n}"
}
```

## Next Steps

- [UseCase + FastAPI](./use_case_fastapi.md) — Embed the same service class into FastAPI
- [MCP Service](./mcp_service.md) — Pure MCP integration (GraphQL mode)
