# Migration Guide

## 1.6.0 → 1.7.0: Voyager ER Diagram 关系字段重构

Voyager ER diagram 的关系展示方式从「FK 字段出发」改为「relationship name 字段出发」。

### 变更说明

| 项目 | 旧行为 | 新行为 |
|------|--------|--------|
| Node 中的关系字段 | 显示 FK 字段（如 `user_id`），标记为 `is_object` | 显示 relationship name + 目标类型（如 `owner: User`） |
| 边的起点 | 从 FK 字段（如 `user_id`）出发 | 从 relationship 字段（如 `owner`）出发 |
| Toggle "Object fields" | 显示 FK 字段 | 显示 relationship 字段 |

### 影响

- 仅影响 `ErDiagramDotBuilder`（Voyager 可视化）
- `ErDiagram`（Mermaid 生成器）不受影响
- 公共 API 无变更，无需迁移代码

## rpc → use_case Refactor

The RPC module has been fully refactored into the UseCase pattern. Key changes:

| Old Name | New Name |
|----------|----------|
| `RpcService` | `UseCaseService` |
| `create_rpc_mcp_server` | `create_use_case_mcp_server` |
| `create_rpc_voyager` | `create_use_case_voyager` |
| `RpcVoyager` | `UseCaseVoyager` |

### MCP Tool Changes

Changed from three layers to four layers, adding `list_apps` layer for multi-app management:

| Old Tool | New Tool |
|----------|----------|
| `list_services()` | `list_apps()` → `list_services(app_name)` |
| `describe_service(service_name)` | `describe_service(app_name, service_name)` |
| `call_rpc(service_name, method_name, params)` | `call_use_case(app_name, service_name, method_name, params)` |

### Code Migration

```python
# Before (rpc)
from nexusx.rpc import RpcService, create_rpc_mcp_server

class SprintService(RpcService):
    ...

mcp = create_rpc_mcp_server(
    services=[SprintService, TaskService],
    name="Project API",
)

# After (use_case)
from nexusx.use_case import UseCaseService, UseCaseAppConfig, create_use_case_mcp_server

class SprintService(UseCaseService):
    ...

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

### New Features

- **Multi-app management**: Organize multiple apps via `UseCaseAppConfig`
- **FromContext**: Support parameter injection from MCP context
- **Case-insensitive lookup**: app_name lookup is case-insensitive

## 1.3.x → 1.4.0: RpcServiceConfig Removal (Historical)

`create_rpc_mcp_server` and `create_rpc_voyager` no longer accept `RpcServiceConfig` configuration dicts — pass `RpcService` subclass lists directly.

```python
# Before (1.3.x)
from nexusx import RpcServiceConfig, create_rpc_mcp_server

mcp = create_rpc_mcp_server(
    services=[
        RpcServiceConfig(name="task", service=TaskService, description="..."),
        RpcServiceConfig(name="sprint", service=SprintService, description="..."),
    ],
)

# After (1.4.0)
from nexusx import create_rpc_mcp_server

mcp = create_rpc_mcp_server(
    services=[TaskService, SprintService],
)
```

## 1.3.2 → 1.3.3: Loader(str) Removal

The `Loader('relationship_name')` string lookup pattern has been removed.

```python
# Before (1.3.2)
def resolve_owner(self, loader=Loader("owner")):
    return loader.load(self.owner_id)

# After (1.3.3) — use DataLoader class or async function
def resolve_owner(self, loader=Loader(UserLoader)):
    return loader.load(self.owner_id)
```

**Note**: Implicit auto-loading already covers common scenarios. When the field name matches a relationship and the type is compatible, you don't need to write `resolve_*` methods.

```python
class TaskDTO(DefineSubset):
    __subset__ = (Task, ("id", "title", "owner_id"))
    owner: UserDTO | None = None   # Auto-loaded, no resolve_* needed
```
