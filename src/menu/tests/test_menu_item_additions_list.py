import pytest
from django.urls import reverse


@pytest.mark.django_db(reset_sequences=True)
def test_additions_list_menu_item(client, create_menu_item, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    menu_item = create_menu_item(additions_count=5)

    response = client.get(reverse('menu_api:menu_item_additions_list', kwargs={'menu_item_id': menu_item.id}))

    assert response.status_code == 200
    assert len(response.data) == menu_item.possible_additions.count()


@pytest.mark.django_db(reset_sequences=True)
def test_additions_list_menu_item_for_authenticated_users(client, create_menu_item, admin_user, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    menu_item = create_menu_item(additions_count=5)

    client.force_login(admin_user)
    response = client.get(reverse('menu_api:menu_item_additions_list', kwargs={'menu_item_id': menu_item.id}))
    assert response.status_code == 403


@pytest.mark.django_db(reset_sequences=True)
def test_additions_list_for_not_existing_menu_item(client):
    response = client.get(reverse('menu_api:menu_item_additions_list', kwargs={'menu_item_id': 666}))
    assert response.status_code == 404


@pytest.mark.django_db(reset_sequences=True)
def test_additions_list_for_menu_item_not_including_hidden_elements(client, create_menu_item, create_menu_item_addition, mocker):
    mocked_storage = mocker.patch('django.core.files.storage.FileSystemStorage.save')
    mocked_storage.return_value = 'test'

    additions = [
        create_menu_item_addition(),
        create_menu_item_addition(),
        create_menu_item_addition(),
        create_menu_item_addition(show=False),
    ]
    menu_item = create_menu_item(additions=additions)

    response = client.get(reverse('menu_api:menu_item_additions_list', kwargs={'menu_item_id': menu_item.id}))

    assert response.status_code == 200
    assert len(response.data) == 3
