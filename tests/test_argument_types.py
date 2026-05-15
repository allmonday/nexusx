"""Tests for inline literal argument type preservation in GraphQL queries."""

from __future__ import annotations

import pytest
from graphql import parse
from sqlmodel import SQLModel, select

from sqlmodel_nexus.decorator import query
from sqlmodel_nexus.execution.argument_builder import ArgumentBuilder
from sqlmodel_nexus.execution.query_executor import QueryExecutor
from sqlmodel_nexus.loader.registry import ErManager
from sqlmodel_nexus.query_parser import QueryParser
from tests.conftest import FixtureUser, get_test_session_factory


class TestArgumentBuilderTypeConversion:
    """Verify that _extract_value preserves Python types from GraphQL literals."""

    def _extract_from_query(self, graphql_query: str, arg_name: str) -> tuple:
        """Parse a GraphQL query and extract argument value via ArgumentBuilder."""
        document = parse(graphql_query)
        # Get the first field's arguments
        for definition in document.definitions:
            for selection in definition.selection_set.selections:
                for arg in selection.arguments:
                    if arg.name.value == arg_name:
                        builder = ArgumentBuilder()
                        return builder._extract_value(arg.value)
        raise ValueError(f"Argument '{arg_name}' not found")

    def test_int_literal_preserved_as_int(self):
        """Inline int literal (e.g. limit: 5) must be int, not str."""
        value = self._extract_from_query("{ users(limit: 5) { id } }", "limit")
        assert value == 5
        assert isinstance(value, int), f"Expected int, got {type(value).__name__}: {value!r}"

    def test_negative_int_literal_preserved(self):
        value = self._extract_from_query("{ users(offset: -1) { id } }", "offset")
        assert value == -1
        assert isinstance(value, int)

    def test_float_literal_preserved_as_float(self):
        value = self._extract_from_query("{ users(ratio: 3.14) { id } }", "ratio")
        assert value == 3.14
        assert isinstance(value, float)

    def test_string_literal_preserved_as_str(self):
        value = self._extract_from_query('{ users(name: "Alice") { id } }', "name")
        assert value == "Alice"
        assert isinstance(value, str)

    def test_boolean_true_preserved(self):
        value = self._extract_from_query("{ users(active: true) { id } }", "active")
        assert value is True

    def test_boolean_false_preserved(self):
        value = self._extract_from_query("{ users(active: false) { id } }", "active")
        assert value is False

    def test_null_literal_preserved(self):
        value = self._extract_from_query("{ users(filter: null) { id } }", "filter")
        assert value is None

    def test_list_of_ints_preserved(self):
        value = self._extract_from_query("{ users(ids: [1, 2, 3]) { id } }", "ids")
        assert value == [1, 2, 3]
        assert all(isinstance(v, int) for v in value)

    def test_nested_object_with_mixed_types(self):
        value = self._extract_from_query(
            '{ users(filter: {age: 25, name: "Bob", active: true}) { id } }',
            "filter",
        )
        assert value == {"age": 25, "name": "Bob", "active": True}
        assert isinstance(value["age"], int)
        assert isinstance(value["active"], bool)


class TestArgumentTypeInE2EQuery:
    """End-to-end test: verify the @query method receives correctly typed arguments."""

    @pytest.mark.usefixtures("test_db")
    async def test_int_argument_reaches_method_as_int(self):
        """A @query method with int param should receive int, not str."""
        received_types: dict[str, type] = {}
        session_factory = get_test_session_factory()

        class UserQuery(SQLModel, table=False):
            @query
            async def get_filtered(cls, limit: int):
                received_types["limit"] = type(limit)
                async with session_factory() as session:
                    result = await session.exec(select(FixtureUser).limit(limit))
                    return list(result.all())

        entities = [FixtureUser]
        registry = ErManager(entities=entities, session_factory=session_factory)
        executor = QueryExecutor(registry)

        method = getattr(UserQuery, "get_filtered")
        query_methods = {"userGetFiltered": (FixtureUser, method)}
        parsed = QueryParser().parse("{ userGetFiltered(limit: 1) { id name } }")

        result = await executor.execute_query(
            "{ userGetFiltered(limit: 1) { id name } }",
            None, None, parsed, query_methods, {}, entities,
        )

        assert "data" in result
        assert "userGetFiltered" in result["data"]
        assert received_types.get("limit") is int, (
            f"Expected int, got {received_types.get('limit')}"
        )
