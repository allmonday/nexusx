# 迁移指南

## 1.3.x → 1.4.0: RpcServiceConfig 移除

`create_rpc_mcp_server` 和 `create_rpc_voyager` 不再接受 `RpcServiceConfig` 配置字典，直接传 `RpcService` 子类列表。

```python
# Before (1.3.x)
from sqlmodel_nexus import RpcServiceConfig, create_rpc_mcp_server

mcp = create_rpc_mcp_server(
    services=[
        RpcServiceConfig(name="task", service=TaskService, description="..."),
        RpcServiceConfig(name="sprint", service=SprintService, description="..."),
    ],
)

# After (1.4.0)
from sqlmodel_nexus import create_rpc_mcp_server

mcp = create_rpc_mcp_server(
    services=[TaskService, SprintService],
)
```

## 1.3.2 → 1.3.3: Loader(str) 移除

`Loader('relationship_name')` 字符串查找模式已移除。

```python
# Before (1.3.2)
def resolve_owner(self, loader=Loader("owner")):
    return loader.load(self.owner_id)

# After (1.3.3) — 使用 DataLoader 类或异步函数
def resolve_owner(self, loader=Loader(UserLoader)):
    return loader.load(self.owner_id)
```

**注意**：隐式自动加载已覆盖常见场景。当字段名匹配关系且类型兼容时，不需要手写 `resolve_*` 方法。

```python
class TaskDTO(DefineSubset):
    __subset__ = (Task, ("id", "title", "owner_id"))
    owner: UserDTO | None = None   # 自动加载，无需 resolve_*
```
