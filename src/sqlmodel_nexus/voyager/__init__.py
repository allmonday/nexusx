"""Voyager visualization for UseCase services and ER diagrams.

Provides interactive visualization of UseCase service structure
and entity-relationship diagrams, decoupled from FastAPI.
"""
from sqlmodel_nexus.voyager.create_voyager import create_use_case_voyager

__all__ = ["create_use_case_voyager"]
