# coding: utf-8

from fastapi.testclient import TestClient


from epa_api.models.status import Status  # noqa: F401


def test_get_status(client: TestClient):
    """Test case for get_status

    Check API health
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/status",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

