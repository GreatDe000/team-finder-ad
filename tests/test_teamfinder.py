import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from projects.models import Project


@pytest.fixture
def users(db):
    User = get_user_model()
    owner = User.objects.create_user(
        email="owner@example.com",
        password="password",
        name="Owner",
        surname="User",
        phone="+79000000100",
    )
    participant = User.objects.create_user(
        email="participant@example.com",
        password="password",
        name="Part",
        surname="User",
        phone="+79000000101",
    )
    return owner, participant


@pytest.fixture
def project(users):
    owner, participant = users
    project = Project.objects.create(name="Project", description="Description", owner=owner)
    project.participants.add(owner)
    participant.favorites.add(project)
    return project


@pytest.mark.django_db
def test_project_list_is_public(client, project):
    response = client.get(reverse("projects:list"))
    assert response.status_code == 200
    assert b"Project" in response.content


@pytest.mark.django_db
def test_anonymous_cannot_create_project(client):
    response = client.get(reverse("projects:create"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_favorite_toggle(client, users, project):
    owner, participant = users
    client.force_login(owner)
    response = client.post(reverse("projects:toggle_favorite", args=(project.pk,)))
    assert response.status_code == 200
    assert response.json()["favorited"] is True
    assert owner.favorites.filter(pk=project.pk).exists()


@pytest.mark.django_db
def test_user_filters_are_available_for_auth_user(client, users, project):
    owner, participant = users
    client.force_login(participant)
    response = client.get(reverse("users:list"), {"filter": "owners-of-favorite-projects"})
    assert response.status_code == 200
    assert owner in response.context["page_obj"].object_list


@pytest.mark.django_db
def test_project_complete_by_owner(client, users, project):
    owner, participant = users
    client.force_login(owner)
    response = client.post(reverse("projects:complete", args=(project.pk,)))
    project.refresh_from_db()
    assert response.status_code == 200
    assert response.json()["project_status"] == Project.CLOSED
    assert project.status == Project.CLOSED


@pytest.mark.django_db
def test_project_toggle_participate(client, users, project):
    owner, participant = users
    client.force_login(participant)
    response = client.post(reverse("projects:toggle_participate", args=(project.pk,)))
    assert response.status_code == 200
    assert response.json()["participant"] is True
    assert project.participants.filter(pk=participant.pk).exists()
