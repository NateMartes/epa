"""
Service Methods for API System Endpoints

Functions are called here if their name is specified as
an operationId in the OpenAPI specification.
"""

from epa_api.apis.system_api_base import BaseSystemApi
from epa_api.models.status import Status

class SystemAPIImplementation(BaseSystemApi):
    async def get_api_status(self) -> Status:
        return Status(status="OK", version="1.0.0")