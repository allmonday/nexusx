# RPC 服务

RpcService 让你将业务逻辑定义为服务类，同时服务于 MCP 和 Web 框架——一个定义，两种呈现。

## 设计理念

```
RpcService 子类 ──┬── MCP server（AI 代理，渐进式发现）
                  └── FastAPI routes（REST API，OpenAPI 文档）
```

## 定义 RpcService

`RpcService` 子类声明 `async classmethod` 方法。元类自动发现公共方法：

```python
from sqlmodel_nexus.rpc import RpcService

class SprintService(RpcService):
    """Sprint 管理服务。"""

    @classmethod
    async def list_sprints(cls) -> list[SprintSummary]:
        """获取所有 sprint 及其任务数。"""
        stmt = build_dto_select(SprintSummary)
        async with async_session() as session:
            rows = (await session.exec(stmt)).all()
        dtos = [SprintSummary(**dict(row._mapping)) for row in rows]
        return await Resolver().resolve(dtos)

    @classmethod
    async def get_sprint(cls, sprint_id: int) -> SprintSummary | None:
        """按 ID 获取 sprint。"""
        stmt = build_dto_select(SprintSummary, where=Sprint.id == sprint_id)
        async with async_session() as session:
            rows = (await session.exec(stmt)).all()
        if not rows:
            return None
        dto = SprintSummary(**dict(rows[0]._mapping))
        return await Resolver().resolve(dto)
```

## 暴露到 MCP

三层渐进式发现：发现 → 检查 → 执行。

```python
from sqlmodel_nexus.rpc import create_rpc_mcp_server

mcp = create_rpc_mcp_server(
    services=[
        SprintService,
        TaskService,
    ],
    name="Project RPC API",
)
mcp.run()  # stdio 模式
```

### MCP 工具

| 工具 | 用途 |
|------|------|
| `list_services()` | 发现可用服务和方法数量 |
| `describe_service(service_name)` | 方法签名（SDL 格式）+ DTO 类型定义 |
| `call_rpc(service_name, method_name, params)` | 执行方法 |

### describe_service 输出

```json
{
  "name": "sprint",
  "methods": [
    {"name": "list_sprints", "signature_sdl": "list_sprints(): [SprintSummary!]!"},
    {"name": "get_sprint", "signature_sdl": "get_sprint(sprint_id: Int!): SprintSummary"}
  ],
  "types": "type SprintSummary {\n  id: Int\n  name: String!\n  tasks: [TaskSummary!]!\n}"
}
```

## 下一步

- [RPC + FastAPI](./rpc_fastapi.zh.md) — 同一服务类嵌入 FastAPI
- [MCP 服务](./mcp_service.zh.md) — 纯 MCP 集成（无 RPC）
