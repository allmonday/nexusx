# UseCase API Reference

Complete API reference for UseCaseService, UseCaseAppConfig, create_use_case_mcp_server, and create_use_case_voyager.

## UseCaseService

Business service base class. Subclasses declare `async classmethod` methods; the metaclass auto-discovers public methods.

```python
from nexusx.use_case import UseCaseService

class SprintService(UseCaseService):
    """Sprint management service."""

    @classmethod
    async def list_sprints(cls) -> list[SprintSummary]:
        ...

    @classmethod
    async def get_sprint(cls, sprint_id: int) -> SprintSummary | None:
        ...
```

### Rules

- Methods must be `async classmethod`
- Methods starting with `_` are not auto-discovered
- Docstrings become MCP tool descriptions

### Class Methods

| Method | Description |
|--------|-------------|
| `get_tag_name()` | Returns the class name as a tag (e.g., `"SprintService"`) |

## UseCaseAppConfig

Application configuration class that organizes a group of UseCaseServices into one application.

```python
from nexusx.use_case import UseCaseAppConfig

config = UseCaseAppConfig(
    name="project",
    services=[SprintService, TaskService],
    description="Project management API",
)
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | `str` | Yes | Application name |
| `services` | `list[type[UseCaseService]]` | Yes | List of UseCaseService subclasses |
| `description` | `str \| None` | No | Application description |
| `context_extractor` | `Callable \| None` | No | MCP context extraction function |

## create_use_case_mcp_server

Create an MCP server for UseCase services, supporting multi-app and four-layer progressive discovery.

```python
from nexusx.use_case import create_use_case_mcp_server, UseCaseAppConfig

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
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `apps` | `list[UseCaseAppConfig]` | Yes | Application configuration list |
| `name` | `str` | No | Service name |

### Generated MCP Tools

| Tool | Description |
|------|-------------|
| `list_apps()` | List all available apps |
| `list_services(app_name)` | List services and method counts in an app |
| `describe_service(app_name, service_name)` | Return method signatures (SDL format) and type definitions |
| `call_use_case(app_name, service_name, method_name, params)` | Execute method |

## create_use_case_voyager

Create a Voyager visualization ASGI sub-application.

```python
from nexusx.voyager import create_use_case_voyager

voyager = create_use_case_voyager(
    apps=[
        UseCaseAppConfig(
            name="project",
            services=[SprintService, TaskService],
        ),
    ],
)
```

### REST Endpoints

| Endpoint | Description |
|----------|-------------|
| `/dot` | DOT format service dependency graph |
| `/dot-search` | Searchable DOT graph |
| `/er-diagram` | Mermaid ER diagram |
| `/source` | Source code information |

## FromContext

Marker annotation for injecting parameters from MCP context.

```python
from typing import Annotated
from nexusx.use_case import FromContext

class SprintService(UseCaseService):
    @classmethod
    async def list_sprints(cls, tenant_id: Annotated[int, FromContext()]) -> list[SprintSummary]:
        ...
```

## build_dto_select

Helper function that builds a SELECT statement for querying DTO fields.

```python
from nexusx import build_dto_select

stmt = build_dto_select(SprintSummary)
stmt = build_dto_select(SprintSummary, where=Sprint.id == sprint_id)
```

> **Note:** When ORM relationships use `lazy="noload"` (the recommended pattern with ErManager + Resolver), this function provides minimal benefit since the only pruning is on scalar columns. You can achieve the same result with `select(Entity)` and `DTO.model_validate(entity)`. Use this function when the DTO selects a small subset of scalar columns from a wide table.
