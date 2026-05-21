# MCP 服务

将 SQLModel API 暴露给 AI 代理，一行代码创建 MCP 服务。

## 安装

```bash
pip install nexusx[fastmcp]
```

## Simple MCP Server

最简模式——传入 SQLModel 基类即可：

```python
from nexusx.mcp import config_simple_mcp_server

mcp = config_simple_mcp_server(
    base=SQLModel,
    name="My API",
)
mcp.run()  # stdio 模式
```

提供的工具：

| 工具 | 用途 |
|------|------|
| `get_schema()` | 获取 GraphQL schema |
| `graphql_query(query)` | 执行 GraphQL 查询 |
| `graphql_mutation(mutation)` | 执行 GraphQL 变更 |

## Multi-App MCP Server

管理多个应用的 API：

```python
from nexusx.mcp import create_mcp_server

mcp = create_mcp_server(
    apps=[
        {"name": "blog", "base": BlogBase, "description": "Blog API"},
        {"name": "shop", "base": ShopBase, "description": "Shop API"},
    ],
    name="Multi-App API",
)
mcp.run()
```

多应用工具：

| 工具 | 用途 |
|------|------|
| `list_apps()` | 列出所有可用应用 |
| `list_queries(app_name)` | 列出应用的查询 |
| `get_query_schema(name, app_name)` | 获取查询 schema |
| `graphql_query(query, app_name)` | 执行查询 |

## session_factory 配置

MCP 服务需要 `session_factory` 来执行数据库查询：

```python
mcp = config_simple_mcp_server(
    base=SQLModel,
    name="My API",
    session_factory=async_session,
)
```

## stdio vs HTTP 模式

```python
# stdio 模式（默认，用于 CLI 集成）
mcp.run()

# HTTP 模式（用于 Web 服务）
mcp.run(transport="sse", host="0.0.0.0", port=8003)
```

## 下一步

- [UseCase 服务](./use_case_service.zh.md) — 业务逻辑的 MCP + REST 双模式服务
- [GraphQL 模式](../guide/graphql_mode.zh.md) — MCP 底层使用的 GraphQL API
