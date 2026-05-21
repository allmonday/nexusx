# 变更记录

## 1.4.0

### Breaking Change: rpc → use_case 重构

`RpcService` → `UseCaseService`，`create_rpc_mcp_server` → `create_use_case_mcp_server`，`create_rpc_voyager` → `create_use_case_voyager`。

新增四层 MCP 工具（`list_apps` → `list_services` → `describe_service` → `call_use_case`），支持多应用管理（`UseCaseAppConfig`）和上下文注入（`FromContext`）。

### Breaking Change: 移除 `RpcServiceConfig`（历史）

`RpcServiceConfig` TypedDict 已移除。服务直接接受子类列表。

- 服务名称从 `cls.__name__` 派生
- 服务描述从 `cls.__doc__` 派生

## 1.3.3

### Breaking Change: 移除 `Loader(str)` 支持

移除基于字符串的 `Loader('relationship_name')` 模式。仅支持 `Loader(DataLoaderClass)` 和 `Loader(async_callable)`。

注意：隐式自动加载（字段名匹配关系 + 兼容类型）已经覆盖了常见场景，无需 `resolve_*` 方法。

## 1.3.2

### Bug Fix: 内省 defaultValue 格式

修复 `IntrospectionGenerator` 默认值序列化，从 Python `repr()` 改为 JSON 格式（`json.dumps`）。

## 1.3.1

### 新功能

- 从 v1.3.0 起提供完整的 Core API、RPC + Voyager 模式文档
- 更新 `llms-full.txt` 以反映当前 API

---

完整变更记录请查看 [GitHub 上的 CHANGELOG.md](https://github.com/allmonday/nexusx/blob/master/CHANGELOG.md)。
