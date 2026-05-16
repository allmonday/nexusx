# Voyager Visualization Advanced

sqlmodel-nexus includes a built-in Voyager module that provides interactive UseCase service graphs and ER entity relationship visualization.

> **Prerequisites**: [UseCase Service](./use_case_service.md) (for service graph) and optionally [Core API Mode](../guide/core_api.md) (for ER diagram integration via `er_manager`).

## create_use_case_voyager

```python
from sqlmodel_nexus.voyager import create_use_case_voyager
from sqlmodel_nexus.use_case import UseCaseAppConfig

voyager = create_use_case_voyager(
    apps=[
        UseCaseAppConfig(
            name="project",
            services=[SprintService, TaskService],
            description="Project management",
        ),
    ],
    er_manager=er,
    name="Project API",
    module_colors={"sprint": "#0f766e", "task": "#0891b2"},
    initial_page_policy="first",
    online_repo_url="https://github.com/example/project",
    version="1.0.0",
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `apps` | `list[UseCaseAppConfig]` | — | Application configuration list |
| `er_manager` | `ErManager \| None` | `None` | ErManager instance for ER diagram integration |
| `name` | `str` | `"UseCase API"` | Project name displayed in UI title |
| `module_colors` | `dict[str, str] \| None` | `None` | Custom colors for service modules |
| `initial_page_policy` | `"first" / "full" / "empty"` | `"first"` | Initial page loading policy |
| `online_repo_url` | `str \| None` | `None` | Online repository URL for source code links |
| `version` | `str` | `"1.0.0"` | Version number displayed in UI |

### Mount to FastAPI

```python
from fastapi import FastAPI

app = FastAPI()
app.mount("/voyager", voyager)
```

## REST Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/dot` | GET | Complete service dependency graph in DOT format |
| `/dot-search` | GET | Searchable and filterable DOT graph |
| `/er-diagram` | GET | Mermaid format ER diagram (requires er_manager) |
| `/source` | GET | Source code information for service methods |

## Visualization Content

### UseCase Service Graph

Displays UseCaseService methods, parameters, return types, and their dependencies:

- Method signatures (SDL format)
- DTO type definitions
- Inter-service call relationships

### ER Entity Relationship Diagram

Integrated via the `er_manager` parameter, showing:

- SQLModel entities and their fields
- ORM relationships (ForeignKey / Relationship)
- Custom relationships (`__relationships__`)
- DefineSubset → source entity mappings

### DefineSubset Tracking

Voyager automatically tracks DefineSubset DTO to source entity mappings:

```python
class TaskDTO(DefineSubset):
    __subset__ = (Task, ("id", "title", "owner_id"))
```

In Voyager, this displays the `TaskDTO` → `Task` subset relationship along with the selected fields.

## Use Cases

- **Development phase**: Visually verify entity relationships and UseCase service structure
- **Team collaboration**: Share interactive ER diagrams to aid modeling discussions
- **Debugging**: Check if DataLoader relationships are registered as expected
- **Documentation**: Export graphs via DOT/Mermaid endpoints for embedding in docs

## Integration with MCP Service

The service structure displayed by Voyager also serves the MCP mode — AI agents can discover and call the same services via MCP tools:

```python
from sqlmodel_nexus.use_case import UseCaseAppConfig, create_use_case_mcp_server
from sqlmodel_nexus.voyager import create_use_case_voyager

# Same set of app configurations
apps = [
    UseCaseAppConfig(
        name="project",
        services=[SprintService, TaskService],
    ),
]

# MCP service (AI agents)
mcp = create_use_case_mcp_server(apps=apps, name="API")

# Voyager visualization (developers)
voyager = create_use_case_voyager(apps=apps, er_manager=er)

app = FastAPI()
app.mount("/mcp", mcp)
app.mount("/voyager", voyager)
```

## Next Steps

- [ER Diagram Visualization](../guide/er_diagram_visual.md) — Mermaid output and Voyager basics
- [UseCase Service](./use_case_service.md) — UseCaseService definitions displayed by Voyager
- [ER Diagram & Non-ORM Relationships](../guide/er_diagram.md) — Entity relationship declaration and discovery
