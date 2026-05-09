# RPC + FastAPI

同一 RpcService 类在 FastAPI 中的使用——路由是薄包装器，业务逻辑留在服务中。

## 路由定义

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

## OpenAPI 分组

`get_tag_name()` 返回 OpenAPI 兼容的标签名：

```python
SprintService.get_tag_name()  # → "sprint"
TaskService.get_tag_name()    # → "task"
```

FastAPI 的 `/docs` 页面会按服务标签自动分组路由。

## 架构优势

```
RpcService 子类 ──┬── MCP server（AI 代理）
                  └── FastAPI routes（REST API）
```

- **业务逻辑单一定义**：修改只需改一处
- **路由薄包装**：FastAPI 路由只做参数传递和异常处理
- **类型安全**：相同的 DTO 类型在两种模式中复用
- **OpenAPI 自动生成**：FastAPI 自动生成 openapi.json，可用于 TypeScript SDK 生成

## 完整示例

```python
from fastapi import FastAPI
from sqlmodel_nexus.rpc import RpcService, create_rpc_mcp_server

# 服务定义
class SprintService(RpcService):
    @classmethod
    async def list_sprints(cls) -> list[SprintSummary]:
        ...

    @classmethod
    async def get_sprint(cls, sprint_id: int) -> SprintSummary | None:
        ...

# MCP 模式
mcp = create_rpc_mcp_server(services=[SprintService], name="Sprint API")

# FastAPI 模式
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

## 下一步

- [RPC 服务](./rpc_service.zh.md) — RpcService 的完整定义方式
- [Core API 模式](../guide/core_api.zh.md) — DTO 定义和 resolve 模式
