# MCP API 参考

MCP 服务配置的完整 API 参考。

## config_simple_mcp_server

创建单应用 MCP 服务。

```python
from sqlmodel_nexus.mcp import config_simple_mcp_server

mcp = config_simple_mcp_server(
    base=SQLModel,              # SQLModel 基类
    name="My API",              # 服务名称
    session_factory=async_session,  # session 工厂
)
```

### 参数

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| `base` | `type` | 是 | SQLModel 基类 |
| `name` | `str` | 是 | 服务名称 |
| `session_factory` | `Callable` | 否 | session 工厂 |

### 生成的工具

| 工具 | 说明 |
|------|------|
| `get_schema()` | 获取 GraphQL schema |
| `graphql_query(query)` | 执行 GraphQL 查询 |
| `graphql_mutation(mutation)` | 执行 GraphQL 变更 |

## create_mcp_server

创建多应用 MCP 服务。

```python
from sqlmodel_nexus.mcp import create_mcp_server

mcp = create_mcp_server(
    apps=[
        {"name": "blog", "base": BlogBase, "description": "Blog API"},
        {"name": "shop", "base": ShopBase, "description": "Shop API"},
    ],
    name="Multi-App API",
)
```

### 参数

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| `apps` | `list[dict]` | 是 | 应用配置列表 |
| `name` | `str` | 是 | 服务名称 |

### 生成的工具

| 工具 | 说明 |
|------|------|
| `list_apps()` | 列出所有应用 |
| `list_queries(app_name)` | 列出应用的查询 |
| `get_query_schema(name, app_name)` | 获取查询 schema |
| `graphql_query(query, app_name)` | 执行查询 |

## AppConfig

多应用配置类型（`create_mcp_server` 的 apps 参数中的字典结构）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | 应用名称 |
| `base` | `type` | SQLModel 基类 |
| `description` | `str` | 应用描述 |
| `session_factory` | `Callable` | session 工厂 |
