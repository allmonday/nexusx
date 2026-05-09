# 变更记录

## 1.4.0

### Breaking Change: 移除 `RpcServiceConfig`

`RpcServiceConfig` TypedDict 已移除。`create_rpc_mcp_server` 和 `create_rpc_voyager` 现在直接接受 `RpcService` 子类列表。

- 服务名称从 `cls.__name__` 派生（如 `TaskService` → `"TaskService"`）
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

完整变更记录请查看 [GitHub 上的 CHANGELOG.md](https://github.com/allmonday/sqlmodel-nexus/blob/master/CHANGELOG.md)。
