import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def test_db_user(db):
    return User.objects.create_user(email="test@examle.com", password="p14assword$123")


@pytest.fixture
def test_api_user():
    return APIClient()
