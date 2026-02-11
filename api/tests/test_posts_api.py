# coding: utf-8

from fastapi.testclient import TestClient


from datetime import datetime  # noqa: F401
from pydantic import Field, StrictStr  # noqa: F401
from typing import List, Optional  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from epa_api.models.post import Post  # noqa: F401


def test_get_posts(client: TestClient):
    """Test case for get_posts

    Retrieve posts
    """
    params = [("post_id", 'post_id_example'),     ("name", 'name_example'),     ("category_slug", 'category_slug_example'),     ("since", '2013-10-20T19:20:30+01:00')]
    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/v1/post",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

