"""Tests for the UseCase module — UseCaseService, ServiceIntrospector, and MCP server."""

from __future__ import annotations

import json

import pytest
from pydantic import BaseModel

from sqlmodel_nexus.use_case.business import UseCaseService
from sqlmodel_nexus.use_case.introspector import (
    ServiceIntrospector,
    _type_to_sdl_name,
)
from sqlmodel_nexus.use_case.server import create_use_case_mcp_server
from sqlmodel_nexus.use_case.types import UseCaseAppConfig

# ──────────────────────────────────────────────────
# Test DTOs
# ──────────────────────────────────────────────────


class UserDTO(BaseModel):
    id: int
    name: str


class TaskDTO(BaseModel):
    id: int
    title: str
    owner: UserDTO | None = None


# ──────────────────────────────────────────────────
# Test Services
# ──────────────────────────────────────────────────


class UserService(UseCaseService):
    """User management service."""

    @classmethod
    async def list_users(cls) -> list[UserDTO]:
        """Get all users."""
        return [UserDTO(id=1, name="Alice"), UserDTO(id=2, name="Bob")]

    @classmethod
    async def get_user(cls, user_id: int) -> UserDTO | None:
        """Get a user by ID."""
        if user_id == 1:
            return UserDTO(id=1, name="Alice")
        return None

    @classmethod
    async def create_user(cls, name: str, email: str) -> UserDTO:
        """Create a new user."""
        return UserDTO(id=99, name=name)


class TaskService(UseCaseService):
    """Task management service."""

    @classmethod
    async def list_tasks(cls) -> list[TaskDTO]:
        """Get all tasks."""
        return [
            TaskDTO(id=1, title="Task 1", owner=UserDTO(id=1, name="Alice")),
        ]

    @classmethod
    async def _internal_helper(cls) -> str:
        """This should NOT be exposed."""
        return "private"

    @classmethod
    async def get_task(cls, task_id: int, include_owner: bool = True) -> TaskDTO | None:
        """Get a task by ID."""
        return TaskDTO(id=task_id, title="Test Task")


# ──────────────────────────────────────────────────
# Tests: UseCaseService
# ──────────────────────────────────────────────────


class TestUseCaseService:
    def test_discovers_async_classmethods(self):
        """Public async classmethods are discovered."""
        assert "list_users" in UserService.__use_case_methods__
        assert "get_user" in UserService.__use_case_methods__
        assert "create_user" in UserService.__use_case_methods__

    def test_excludes_private_methods(self):
        """Methods starting with _ are excluded."""
        assert "_internal_helper" not in TaskService.__use_case_methods__

    def test_excludes_get_tag_name(self):
        """get_tag_name is excluded from use case methods."""
        for service_cls in [UserService, TaskService]:
            assert "get_tag_name" not in service_cls.__use_case_methods__

    def test_get_tag_name_returns_class_name(self):
        """get_tag_name returns the class name by default."""
        assert UserService.get_tag_name() == "UserService"
        assert TaskService.get_tag_name() == "TaskService"

    def test_use_case_service_base_has_empty_methods(self):
        """UseCaseService base class has empty __use_case_methods__."""
        assert UseCaseService.__use_case_methods__ == {}


# ──────────────────────────────────────────────────
# Tests: _type_to_sdl_name
# ──────────────────────────────────────────────────


class TestTypeToSdlName:
    def test_int(self):
        assert _type_to_sdl_name(int) == "Int"

    def test_str(self):
        assert _type_to_sdl_name(str) == "String"

    def test_float(self):
        assert _type_to_sdl_name(float) == "Float"

    def test_bool(self):
        assert _type_to_sdl_name(bool) == "Boolean"

    def test_list_of_int(self):
        assert _type_to_sdl_name(list[int]) == "[Int!]!"

    def test_optional_int(self):
        assert _type_to_sdl_name(int | None) == "Int"

    def test_list_of_dto(self):
        assert _type_to_sdl_name(list[UserDTO]) == "[UserDTO!]!"

    def test_optional_dto(self):
        assert _type_to_sdl_name(UserDTO | None) == "UserDTO"

    def test_dto_class(self):
        assert _type_to_sdl_name(UserDTO) == "UserDTO"

    def test_dict(self):
        assert _type_to_sdl_name(dict) == "JSON"

    def test_empty_annotation(self):
        from inspect import Parameter

        assert _type_to_sdl_name(Parameter.empty) == "String"


# ──────────────────────────────────────────────────
# Tests: ServiceIntrospector
# ──────────────────────────────────────────────────


def _make_introspector() -> ServiceIntrospector:
    return ServiceIntrospector([UserService, TaskService])


class TestServiceIntrospector:
    def test_list_services(self):
        introspector = _make_introspector()
        services = introspector.list_services()
        assert len(services) == 2

        user_svc = next(s for s in services if s["name"] == "UserService")
        assert user_svc["description"] == "User management service."
        assert user_svc["methods_count"] == 3

        task_svc = next(s for s in services if s["name"] == "TaskService")
        assert task_svc["methods_count"] == 2  # list_tasks + get_task (excludes _internal)

    def test_describe_service_methods(self):
        introspector = _make_introspector()
        info = introspector.describe_service("UserService")
        assert info is not None
        assert info["name"] == "UserService"
        assert len(info["methods"]) == 3

    def test_describe_service_signatures(self):
        introspector = _make_introspector()
        info = introspector.describe_service("UserService")
        assert info is not None

        list_users = next(m for m in info["methods"] if m["name"] == "list_users")
        assert list_users["description"] == "Get all users."
        assert "list_users()" in list_users["signature"]
        assert "list[UserDTO]" in list_users["signature"]
        assert "[UserDTO!]!" in list_users["signature_sdl"]

        get_user = next(m for m in info["methods"] if m["name"] == "get_user")
        assert "user_id" in get_user["signature"]
        assert "UserDTO" in get_user["signature"]

    def test_describe_service_types(self):
        """types field contains SDL type definitions for referenced DTOs."""
        introspector = _make_introspector()
        info = introspector.describe_service("UserService")
        assert info is not None

        types_str = info["types"]
        assert "type UserDTO" in types_str
        assert "id: Int" in types_str
        assert "name: String!" in types_str

    def test_describe_service_task_types(self):
        """types includes nested DTOs from return values."""
        introspector = _make_introspector()
        info = introspector.describe_service("TaskService")
        assert info is not None

        types_str = info["types"]
        assert "type TaskDTO" in types_str
        assert "type UserDTO" in types_str
        assert "owner: UserDTO" in types_str

    def test_describe_service_with_params(self):
        introspector = _make_introspector()
        info = introspector.describe_service("UserService")
        assert info is not None

        get_user = next(m for m in info["methods"] if m["name"] == "get_user")
        assert "user_id" in get_user["parameters"]

    def test_describe_service_not_found(self):
        introspector = _make_introspector()
        assert introspector.describe_service("nonexistent") is None

    def test_get_service(self):
        introspector = _make_introspector()
        assert introspector.get_service("UserService") is UserService
        assert introspector.get_service("nonexistent") is None

    def test_uses_class_docstring_as_description(self):
        introspector = _make_introspector()
        info = introspector.describe_service("TaskService")
        assert info is not None
        assert info["description"] == "Task management service."


# ──────────────────────────────────────────────────
# Tests: MCP Server (integration)
# ──────────────────────────────────────────────────

APP_NAME = "test_app"


def _make_mcp_server():
    return create_use_case_mcp_server(
        apps=[
            UseCaseAppConfig(
                name=APP_NAME,
                services=[UserService, TaskService],
                description="Test app",
            ),
        ],
        name="Test UseCase API",
    )


class TestUseCaseMcpServer:
    @pytest.fixture
    def mcp_server(self):
        return _make_mcp_server()

    def test_server_creation(self, mcp_server):
        """Server is created successfully with 4 tools."""
        assert mcp_server is not None

    @pytest.mark.asyncio
    async def test_list_apps(self, mcp_server):
        """list_apps returns all registered apps."""
        result = await mcp_server.call_tool("list_apps", {})
        data = json.loads(result.content[0].text)
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == APP_NAME
        assert data["data"][0]["services_count"] == 2

    @pytest.mark.asyncio
    async def test_list_services_tool(self, mcp_server):
        """list_services returns all registered services for an app."""
        result = await mcp_server.call_tool("list_services", {"app_name": APP_NAME})
        data = json.loads(result.content[0].text)
        assert data["success"] is True
        assert len(data["data"]) == 2

    @pytest.mark.asyncio
    async def test_list_services_case_insensitive(self, mcp_server):
        """list_services works with case-insensitive app name."""
        result = await mcp_server.call_tool("list_services", {"app_name": "Test_App"})
        data = json.loads(result.content[0].text)
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_describe_service_tool(self, mcp_server):
        """describe_service returns method details with SDL signatures."""
        result = await mcp_server.call_tool(
            "describe_service",
            {"app_name": APP_NAME, "service_name": "UserService"},
        )
        data = json.loads(result.content[0].text)
        assert data["success"] is True
        assert data["data"]["name"] == "UserService"
        assert len(data["data"]["methods"]) == 3
        # Check that types field has SDL
        assert "type UserDTO" in data["data"]["types"]

    @pytest.mark.asyncio
    async def test_describe_service_not_found(self, mcp_server):
        """describe_service returns error for unknown service."""
        result = await mcp_server.call_tool(
            "describe_service",
            {"app_name": APP_NAME, "service_name": "unknown"},
        )
        data = json.loads(result.content[0].text)
        assert data["success"] is False

    @pytest.mark.asyncio
    async def test_call_use_case_no_params(self, mcp_server):
        """call_use_case works with no parameters."""
        result = await mcp_server.call_tool(
            "call_use_case",
            {
                "app_name": APP_NAME,
                "service_name": "UserService",
                "method_name": "list_users",
                "params": "{}",
            },
        )
        data = json.loads(result.content[0].text)
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["data"][0]["name"] == "Alice"

    @pytest.mark.asyncio
    async def test_call_use_case_with_params(self, mcp_server):
        """call_use_case passes parameters to the method."""
        result = await mcp_server.call_tool(
            "call_use_case",
            {
                "app_name": APP_NAME,
                "service_name": "UserService",
                "method_name": "get_user",
                "params": json.dumps({"user_id": 1}),
            },
        )
        data = json.loads(result.content[0].text)
        assert data["success"] is True
        assert data["data"]["id"] == 1
        assert data["data"]["name"] == "Alice"

    @pytest.mark.asyncio
    async def test_call_use_case_returns_null(self, mcp_server):
        """call_use_case handles None return values."""
        result = await mcp_server.call_tool(
            "call_use_case",
            {
                "app_name": APP_NAME,
                "service_name": "UserService",
                "method_name": "get_user",
                "params": json.dumps({"user_id": 999}),
            },
        )
        data = json.loads(result.content[0].text)
        assert data["success"] is True
        assert data["data"] is None

    @pytest.mark.asyncio
    async def test_call_use_case_app_not_found(self, mcp_server):
        """call_use_case returns error for unknown app."""
        result = await mcp_server.call_tool(
            "call_use_case",
            {
                "app_name": "unknown",
                "service_name": "UserService",
                "method_name": "list_users",
                "params": "{}",
            },
        )
        data = json.loads(result.content[0].text)
        assert data["success"] is False

    @pytest.mark.asyncio
    async def test_call_use_case_service_not_found(self, mcp_server):
        """call_use_case returns error for unknown service."""
        result = await mcp_server.call_tool(
            "call_use_case",
            {
                "app_name": APP_NAME,
                "service_name": "unknown",
                "method_name": "foo",
                "params": "{}",
            },
        )
        data = json.loads(result.content[0].text)
        assert data["success"] is False

    @pytest.mark.asyncio
    async def test_call_use_case_method_not_found(self, mcp_server):
        """call_use_case returns error for unknown method."""
        result = await mcp_server.call_tool(
            "call_use_case",
            {
                "app_name": APP_NAME,
                "service_name": "UserService",
                "method_name": "nonexistent",
                "params": "{}",
            },
        )
        data = json.loads(result.content[0].text)
        assert data["success"] is False

    @pytest.mark.asyncio
    async def test_call_use_case_invalid_json(self, mcp_server):
        """call_use_case returns error for invalid JSON params."""
        result = await mcp_server.call_tool(
            "call_use_case",
            {
                "app_name": APP_NAME,
                "service_name": "UserService",
                "method_name": "list_users",
                "params": "invalid",
            },
        )
        data = json.loads(result.content[0].text)
        assert data["success"] is False

    @pytest.mark.asyncio
    async def test_call_use_case_invalid_param_type(self, mcp_server):
        """call_use_case returns error when params is not a dict."""
        result = await mcp_server.call_tool(
            "call_use_case",
            {
                "app_name": APP_NAME,
                "service_name": "UserService",
                "method_name": "list_users",
                "params": "[1,2]",
            },
        )
        data = json.loads(result.content[0].text)
        assert data["success"] is False

    @pytest.mark.asyncio
    async def test_call_use_case_wrong_param_name(self, mcp_server):
        """call_use_case returns error when parameter name doesn't match."""
        result = await mcp_server.call_tool(
            "call_use_case",
            {
                "app_name": APP_NAME,
                "service_name": "UserService",
                "method_name": "get_user",
                "params": json.dumps({"wrong_param": 1}),
            },
        )
        data = json.loads(result.content[0].text)
        assert data["success"] is False
