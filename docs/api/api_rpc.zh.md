# RPC API 参考

RpcService、create_rpc_mcp_server、create_rpc_voyager 的完整 API 参考。

## RpcService

业务服务基类。子类声明 `async classmethod` 方法，元类自动发现公共方法。

```python
from sqlmodel_nexus.rpc import RpcService

class SprintService(RpcService):
    """Sprint 管理服务。"""

    @classmethod
    async def list_sprints(cls) -> list[SprintSummary]:
        ...

    @classmethod
    async def get_sprint(cls, sprint_id: int) -> SprintSummary | None:
        ...
```

### 规则

- 方法必须是 `async classmethod`
- 方法名以 `_` 开头的不会被自动发现
- docstring 成为 MCP 工具的描述

### 类方法

| 方法 | 说明 |
|------|------|
| `get_tag_name()` | 返回 OpenAPI 兼容的标签名（如 `"sprint"`） |

## create_rpc_mcp_server

创建 RPC 服务的 MCP 服务端。

```python
from sqlmodel_nexus.rpc import create_rpc_mcp_server

mcp = create_rpc_mcp_server(
    services=[SprintService, TaskService],
    name="Project RPC API",
)
```

### 参数

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| `services` | `list[type[RpcService]]` | 是 | RpcService 子类列表 |
| `name` | `str` | 是 | 服务名称 |

### 生成的 MCP 工具

| 工具 | 说明 |
|------|------|
| `list_services()` | 列出可用服务和方法数量 |
| `describe_service(service_name)` | 返回 SDL 格式的方法签名和类型定义 |
| `call_rpc(service_name, method_name, params)` | 执行方法 |

## create_rpc_voyager

创建 Voyager 可视化 ASGI 子应用。

```python
from sqlmodel_nexus.rpc import create_rpc_voyager

voyager = create_rpc_voyager(
    services=[SprintService, TaskService],
)
```

### REST 端点

| 端点 | 说明 |
|------|------|
| `/dot` | DOT 格式服务依赖图 |
| `/dot-search` | 可搜索的 DOT 图 |
| `/er-diagram` | Mermaid ER 图 |
| `/source` | 源代码信息 |

## build_dto_select

辅助函数，构建查询 DTO 所需字段的 SELECT 语句。

```python
from sqlmodel_nexus.rpc import build_dto_select

stmt = build_dto_select(SprintSummary)
stmt = build_dto_select(SprintSummary, where=Sprint.id == sprint_id)
```
