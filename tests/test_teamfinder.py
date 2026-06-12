import json

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from projects.models import Project, Skill


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
    skill = Skill.objects.create(name="Django")
    project = Project.objects.create(name="Project", description="Description", owner=owner)
    project.participants.add(owner)
    project.skills.add(skill)
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
def test_project_skill_filter(client, project):
    response = client.get(reverse("projects:list"), {"skill": "Django"})
    assert response.status_code == 200
    assert project in response.context["page_obj"].object_list


@pytest.mark.django_db
def test_project_owner_can_add_skill(client, users, project):
    owner, participant = users
    client.force_login(owner)
    response = client.post(
        reverse("projects:add_skill", args=(project.pk,)),
        data=json.dumps({"name": "Python"}),
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Python"
    assert project.skills.filter(name="Python").exists()
