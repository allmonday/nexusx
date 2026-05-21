# UseCase 服务

UseCaseService 让你将业务逻辑定义为服务类，同时服务于 MCP 和 Web 框架——一个定义，两种呈现。

## 设计理念

```
UseCaseService 子类 ──┬── MCP server（AI 代理，四层渐进式发现）
                      └── FastAPI routes（REST API，OpenAPI 文档）
```

## 定义 UseCaseService

`UseCaseService` 子类声明 `async classmethod` 方法。元类自动发现公共方法：

```python
from nexusx.use_case import UseCaseService

class SprintService(UseCaseService):
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

四层渐进式发现：应用发现 → 服务列表 → 方法详情 → 执行。

```python
from nexusx.use_case import UseCaseAppConfig, create_use_case_mcp_server

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
mcp.run()  # stdio 模式
```

### MCP 工具

| 工具 | 用途 |
|------|------|
| `list_apps()` | 发现可用应用 |
| `list_services(app_name)` | 列出应用中的服务和方法数量 |
| `describe_service(app_name, service_name)` | 方法签名（SDL 格式）+ DTO 类型定义 |
| `call_use_case(app_name, service_name, method_name, params)` | 执行方法 |

### describe_service 输出

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

## 下一步

- [UseCase + FastAPI](./use_case_fastapi.zh.md) — 同一服务类嵌入 FastAPI
- [MCP 服务](./mcp_service.zh.md) — 纯 MCP 集成（GraphQL 模式）
