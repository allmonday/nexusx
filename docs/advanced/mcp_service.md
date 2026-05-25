# MCP Service

Expose SQLModel APIs to AI agents — create an MCP service with a single line of code.

## Installation

```bash
pip install nexusx[fastmcp]
```

## Simple MCP Server

The simplest mode — pass a SQLModel base class:

```python
from nexusx.mcp import create_simple_mcp_server

mcp = create_simple_mcp_server(
    base=SQLModel,
    name="My API",
)
mcp.run()  # stdio mode
```

Provided tools:

| Tool | Purpose |
|------|---------|
| `get_schema()` | Get GraphQL schema |
| `graphql_query(query)` | Execute GraphQL query |
| `graphql_mutation(mutation)` | Execute GraphQL mutation |

## Multi-App MCP Server

Manage APIs for multiple applications:

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

Multi-app tools:

| Tool | Purpose |
|------|---------|
| `list_apps()` | List all available apps |
| `list_queries(app_name)` | List queries for an app |
| `get_query_schema(name, app_name)` | Get query schema |
| `graphql_query(query, app_name)` | Execute query |

## session_factory Configuration

MCP services need a `session_factory` to execute database queries:

```python
mcp = create_simple_mcp_server(
    base=SQLModel,
    name="My API",
    session_factory=async_session,
)
```

## stdio vs HTTP Mode

```python
# stdio mode (default, for CLI integration)
mcp.run()

# HTTP mode (for web services)
mcp.run(transport="sse", host="0.0.0.0", port=8003)
```

## Next Steps

- [UseCase Service](./use_case_service.md) — Business logic dual-mode service for MCP + REST
- [GraphQL Mode](../guide/graphql_mode.md) — The GraphQL API used under the hood by MCP
