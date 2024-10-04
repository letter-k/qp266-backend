import json

import pytest
from django.urls import reverse


def test_user_login(test_db_user, test_api_user):
    response = test_api_user.post(
        reverse("graphql"),
        data=json.dumps(
            {
                "query": """
                mutation {
                    obtainAuthToken(credentials: {username: "test@examle.com", password: "p14assword$123"}) {
                        token
                    }
                }
            """
            }
        ),
        content_type="application/json",
    )

    assert "errors" not in response.json()
    assert "token" in response.json()["data"]["obtainAuthToken"]


def test_user_login_incorrect_username(test_db_user, test_api_user):
    response = test_api_user.post(
        reverse("graphql"),
        data=json.dumps(
            {
                "query": """
                mutation {
                    obtainAuthToken(credentials: {username: "t0st@examle.com", password: "p14assword$123"}) {
                        token
                    }
                }
            """
            }
        ),
        content_type="application/json",
    )

    assert "errors" in response.json()
    assert response.json()["data"]["obtainAuthToken"] is None


def test_user_login_incorrect_password(test_db_user, test_api_user):
    response = test_api_user.post(
        reverse("graphql"),
        data=json.dumps(
            {
                "query": """
                mutation {
                    obtainAuthToken(credentials: {username: "test@examle.com", password: "p@14assword$123"}) {
                        token
                    }
                }
            """
            }
        ),
        content_type="application/json",
    )

    assert "errors" in response.json()
    assert response.json()["data"]["obtainAuthToken"] is None


def test_user_login_incorrect_username_n_password(test_db_user, test_api_user):
    response = test_api_user.post(
        reverse("graphql"),
        data=json.dumps(
            {
                "query": """
                mutation {
                    obtainAuthToken(credentials: {username: "t0st@examle.com", password: "p@14assword$123"}) {
                        token
                    }
                }
            """
            }
        ),
        content_type="application/json",
    )

    assert "errors" in response.json()
    assert response.json()["data"]["obtainAuthToken"] is None


@pytest.fixture
def auth_client(test_db_user, test_api_user):
    response = test_api_user.post(
        reverse("graphql"),
        data=json.dumps(
            {
                "query": """
                mutation {
                    obtainAuthToken(credentials: {username: "test@examle.com", password: "p14assword$123"}) {
                        token
                    }
                }
            """
            }
        ),
        content_type="application/json",
    )

    assert "token" in response.json()["data"]["obtainAuthToken"]
    test_api_user.credentials(HTTP_AUTHORIZATION="Bearer " + response.json()["data"]["obtainAuthToken"]["token"])
    return test_api_user


def test_ping_without_auth(test_db_user, test_api_user):
    response = test_api_user.post(
        reverse("graphql"),
        data=json.dumps(
            {
                "query": """
                query{
                    ping
                }
            """
            }
        ),
        content_type="application/json",
    )

    assert "errors" in response.json()


def test_ping(test_db_user, auth_client):
    response = auth_client.post(
        reverse("graphql"),
        data=json.dumps(
            {
                "query": """
                query{
                    ping
                }
            """
            }
        ),
        content_type="application/json",
    )

    assert "errors" not in response.json()
    assert response.json()["data"]["ping"] == "PONG"
