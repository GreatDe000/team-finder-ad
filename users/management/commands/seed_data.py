from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from projects.models import Project


class Command(BaseCommand):
    help = "Create demo users and projects"

    def handle(self, *args, **options):
        User = get_user_model()
        users_data = [
            {
                "email": "imya@yandex.ru",
                "password": "password",
                "name": "Мария",
                "surname": "Фамилия",
                "phone": "+88005553535",
                "github_url": "https://github.com/maria",
                "about": "Frontend-разработчик.",
            },
            {
                "email": "alex@yandex.ru",
                "password": "password",
                "name": "Алексей",
                "surname": "Алексеев",
                "phone": "+79000000001",
                "github_url": "https://github.com/alex",
                "about": "Backend-разработчик.",
            },
            {
                "email": "olga@yandex.ru",
                "password": "password",
                "name": "Ольга",
                "surname": "Смирнова",
                "phone": "+79000000002",
                "github_url": "https://github.com/olga",
                "about": "UI/UX-дизайнер.",
            },
        ]
        users = []
        for data in users_data:
            password = data.pop("password")
            user, created = User.objects.get_or_create(email=data["email"], defaults=data)
            if created:
                user.set_password(password)
                user.save()
            users.append(user)

        projects_data = [
            {
                "name": "EduTracker",
                "description": (
                    "Сервис для отслеживания учебных целей "
                    "и командной работы студентов."
                ),
                "owner": users[0],
                "github_url": "https://github.com/maria/edutracker",
            },
            {
                "name": "DevBoard",
                "description": "Доска задач.",
                "owner": users[1],
                "github_url": "https://github.com/alex/devboard",
            },
            {
                "name": "DesignHub",
                "description": "Платформа для совместного обсуждения дизайн-концепций.",
                "owner": users[2],
                "github_url": "https://github.com/olga/designhub",
            },
        ]
        projects = []
        for data in projects_data:
            project, _ = Project.objects.get_or_create(name=data["name"], defaults=data)
            project.participants.add(project.owner)
            projects.append(project)

        users[0].favorites.add(projects[1])
        users[1].favorites.add(projects[0], projects[2])
        users[2].favorites.add(projects[0])
        projects[0].participants.add(users[1])
        projects[1].participants.add(users[2])
        self.stdout.write(self.style.SUCCESS("Demo data created"))
