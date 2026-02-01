from contextvars import ContextVar
from typing import Optional
from epa_api.models.extra_models import TokenModel

current_token_data: ContextVar[TokenModel | None] = ContextVar("current_token_data", default=None)
