# Changelog

## 1.4.0

### Breaking Change: rpc → use_case Refactor

`RpcService` → `UseCaseService`, `create_rpc_mcp_server` → `create_use_case_mcp_server`, `create_rpc_voyager` → `create_use_case_voyager`.

Added four-layer MCP tools (`list_apps` → `list_services` → `describe_service` → `call_use_case`), multi-app management support (`UseCaseAppConfig`), and context injection (`FromContext`).

### Breaking Change: Removal of `RpcServiceConfig` (Historical)

The `RpcServiceConfig` TypedDict has been removed. Services now directly accept a list of subclasses.

- Service names are derived from `cls.__name__`
- Service descriptions are derived from `cls.__doc__`

## 1.3.3

### Breaking Change: Removal of `Loader(str)` Support

Removed the string-based `Loader('relationship_name')` pattern. Only `Loader(DataLoaderClass)` and `Loader(async_callable)` are supported.

Note: Implicit auto-loading (field name matching relationship + compatible type) already covers common scenarios without needing `resolve_*` methods.

## 1.3.2

### Bug Fix: Introspection defaultValue Format

Fixed `IntrospectionGenerator` default value serialization, changing from Python `repr()` to JSON format (`json.dumps`).

## 1.3.1

### New Features

- Full documentation for Core API, RPC + Voyager modes from v1.3.0 onwards
- Updated `llms-full.txt` to reflect current API

---

For the complete changelog, see [CHANGELOG.md on GitHub](https://github.com/allmonday/nexusx/blob/master/CHANGELOG.md).
