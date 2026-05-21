# Voyager 可视化进阶

nexusx 内置 Voyager 模块，提供交互式的 UseCase 服务图和 ER 实体关系可视化。

## create_use_case_voyager

```python
from nexusx.voyager import create_use_case_voyager
from nexusx.use_case import UseCaseAppConfig

voyager = create_use_case_voyager(
    apps=[
        UseCaseAppConfig(
            name="project",
            services=[SprintService, TaskService],
            description="Project management",
        ),
    ],
    er_manager=er,
    name="Project API",
    module_colors={"sprint": "#0f766e", "task": "#0891b2"},
    initial_page_policy="first",
    online_repo_url="https://github.com/example/project",
    version="1.0.0",
)
```

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `apps` | `list[UseCaseAppConfig]` | — | 应用配置列表 |
| `er_manager` | `ErManager \| None` | `None` | ErManager 实例，用于 ER 图集成 |
| `name` | `str` | `"UseCase API"` | 项目名称，显示在 UI 标题 |
| `module_colors` | `dict[str, str] \| None` | `None` | 服务模块的自定义颜色 |
| `initial_page_policy` | `"first" / "full" / "empty"` | `"first"` | 初始页面加载策略 |
| `online_repo_url` | `str \| None` | `None` | 在线仓库 URL，用于源码链接 |
| `version` | `str` | `"1.0.0"` | 版本号，显示在 UI |

### 挂载到 FastAPI

```python
from fastapi import FastAPI

app = FastAPI()
app.mount("/voyager", voyager)
```

## REST 端点详解

| 端点 | 方法 | 说明 |
|------|------|------|
| `/dot` | GET | DOT 格式的完整服务依赖图 |
| `/dot-search` | GET | 支持搜索过滤的 DOT 图 |
| `/er-diagram` | GET | Mermaid 格式的 ER 图（需要 er_manager） |
| `/source` | GET | 服务方法的源代码信息 |

## 可视化内容

### UseCase 服务图

展示 UseCaseService 的方法、参数、返回类型及其之间的依赖关系：

- 方法签名（SDL 格式）
- DTO 类型定义
- 服务间调用关系

### ER 实体关系图

通过 `er_manager` 参数集成，展示：

- SQLModel 实体及其字段
- ORM 关系（ForeignKey / Relationship）
- 自定义关系（`__relationships__`）
- DefineSubset → 源实体的对应关系

### DefineSubset 追踪

Voyager 自动追踪 DefineSubset DTO 到其源实体的映射：

```python
class TaskDTO(DefineSubset):
    __subset__ = (Task, ("id", "title", "owner_id"))
```

在 Voyager 中会展示 `TaskDTO` → `Task` 的子集关系，以及被选中的字段。

## 使用场景

- **开发阶段**：可视化验证实体关系和 UseCase 服务结构是否正确
- **团队协作**：共享交互式 ER 图，辅助建模讨论
- **调试**：检查 DataLoader 关系是否按预期注册
- **文档**：通过 DOT/Mermaid 端点导出图形嵌入文档

## 与 MCP 服务配合

Voyager 展示的服务结构同时服务于 MCP 模式——AI 代理可以通过 MCP 工具发现和调用相同的服务：

```python
from nexusx.use_case import UseCaseAppConfig, create_use_case_mcp_server
from nexusx.voyager import create_use_case_voyager

# 同一批应用配置
apps = [
    UseCaseAppConfig(
        name="project",
        services=[SprintService, TaskService],
    ),
]

# MCP 服务（AI 代理）
mcp = create_use_case_mcp_server(apps=apps, name="API")

# Voyager 可视化（开发者）
voyager = create_use_case_voyager(apps=apps, er_manager=er)

app = FastAPI()
app.mount("/mcp", mcp)
app.mount("/voyager", voyager)
```

## 下一步

- [ER 图可视化](../guide/er_diagram_visual.zh.md) — Mermaid 输出和 Voyager 基础用法
- [UseCase 服务](./use_case_service.zh.md) — Voyager 展示的 UseCaseService 定义
- [ER 图与非 ORM 关系](../guide/er_diagram.zh.md) — 实体关系的声明和发现
