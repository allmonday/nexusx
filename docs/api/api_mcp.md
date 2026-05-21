# MCP API Reference

Complete API reference for MCP service configuration.

## config_simple_mcp_server

Create a single-app MCP service.

```python
from nexusx.mcp import config_simple_mcp_server

mcp = config_simple_mcp_server(
    base=SQLModel,              # SQLModel base class
    name="My API",              # Service name
    session_factory=async_session,  # Session factory
)
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `base` | `type` | Yes | SQLModel base class |
| `name` | `str` | Yes | Service name |
| `session_factory` | `Callable` | No | Session factory |

### Generated Tools

| Tool | Description |
|------|-------------|
| `get_schema()` | Get GraphQL schema |
| `graphql_query(query)` | Execute GraphQL query |
| `graphql_mutation(mutation)` | Execute GraphQL mutation |

## create_mcp_server

Create a multi-app MCP service.

```python
from nexusx.mcp import create_mcp_server

mcp = create_mcp_server(
    apps=[
        {"name": "blog", "base": BlogBase, "description": "Blog API"},
        {"name": "shop", "base": ShopBase, "description": "Shop API"},
    ],
    name="Multi-App API",
)
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `apps` | `list[dict]` | Yes | Application configuration list |
| `name` | `str` | Yes | Service name |

### Generated Tools

| Tool | Description |
|------|-------------|
| `list_apps()` | List all applications |
| `list_queries(app_name)` | List queries for an app |
| `get_query_schema(name, app_name)` | Get query schema |
| `graphql_query(query, app_name)` | Execute query |

## AppConfig

Multi-app configuration type (the dictionary structure in `create_mcp_server`'s apps parameter):

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Application name |
| `base` | `type` | SQLModel base class |
| `description` | `str` | Application description |
| `session_factory` | `Callable` | Session factory |
