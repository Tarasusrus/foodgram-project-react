import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
def test_user_list(api_client):
    url = reverse('api:user-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) > 0  # Проверяем, что список не пустой

@pytest.mark.django_db
def test_user_registration(api_client):
    url = reverse('api:user-list')
    data = {
        'email': 'user@example.com',
        'username': 'myusername',
        'first_name': 'John',
        'last_name': 'Doe',
        'password': 'mypassword'
    }

    response = api_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['email'] == 'user@example.com'
    assert response.data['username'] == 'myusername'
    assert response.data['first_name'] == 'John'
    assert response.data['last_name'] == 'Doe'


@pytest.mark.django_db
def test_user_token_take(api_client):
    url = reverse('api:user-list')
    data = {
        'password': 'testpassword',
        'email': 'test_email',
    }

    response = api_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['password'] == 'testpassword'
    assert response.data['email'] == None