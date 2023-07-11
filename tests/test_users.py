import pytest
from django.urls import reverse
from rest_framework import status

@pytest.mark.django_db
def test_user_list(api_client):
    url = reverse('api:user-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) > 0  # Проверяем, что список не пустой
