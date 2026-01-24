# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from epa_api.apis.system_api_base import BaseSystemApi
import epa_api.api_implementation

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from epa_api.models.extra_models import TokenModel  # noqa: F401
from epa_api.models.status import Status


router = APIRouter()

ns_pkg = epa_api.api_implementation
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/v1/status",
    responses={
        200: {"model": Status, "description": "API is healthy"},
    },
    tags=["System"],
    summary="Check API health",
    response_model_by_alias=True,
)
async def get_api_status(
) -> Status:
    if not BaseSystemApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseSystemApi.subclasses[0]().get_api_status()
