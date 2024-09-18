from django.urls import reverse


def test_user_login(client, test_user):
    response = client.post(
        reverse("login"),
        data={
            "username": "test@examle.com",
            "password": "p14assword$123",
        },
    )

    assert response.status_code == 200
    assert "token" in response.data


def test_user_login_incorrect_username(client, test_user):
    response = client.post(
        reverse("login"),
        data={
            "username": "t0st@examle.com",
            "password": "p14assword$123",
        },
    )

    assert response.status_code == 400
    assert "token" not in response.data


def test_user_login_incorrect_password(client, test_user):
    response = client.post(
        reverse("login"),
        data={
            "username": "test@examle.com",
            "password": "p@14assword$123",
        },
    )

    assert response.status_code == 400
    assert "token" not in response.data


def test_user_login_incorrect_username_n_password(client, test_user):
    response = client.post(
        reverse("login"),
        data={
            "username": "t0st@examle.com",
            "password": "p@14assword$123",
        },
    )

    assert response.status_code == 400
    assert "token" not in response.data
