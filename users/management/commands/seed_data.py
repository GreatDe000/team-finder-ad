from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from projects.models import Project, Skill


class Command(BaseCommand):
    help = "Create demo users, skills and projects"

    def handle(self, *args, **options):
        User = get_user_model()
        users_data = [
            {
                "email": "maria@yandex.ru",
                "password": "password",
                "name": "Мария",
                "surname": "Иванова",
                "phone": "+79000000001",
                "github_url": "https://github.com/maria",
                "about": "Frontend-разработчик, люблю образовательные pet-проекты.",
            },
            {
                "email": "alex@yandex.ru",
                "password": "password",
                "name": "Алексей",
                "surname": "Петров",
                "phone": "+79000000002",
                "github_url": "https://github.com/alex",
                "about": "Backend-разработчик на Python и Django.",
            },
            {
                "email": "olga@yandex.ru",
                "password": "password",
                "name": "Ольга",
                "surname": "Смирнова",
                "phone": "+79000000003",
                "github_url": "https://github.com/olga",
                "about": "UI/UX-дизайнер и продуктовый исследователь.",
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

        skills = {}
        for name in ("Django", "Python", "JavaScript", "UI/UX", "PostgreSQL", "Docker"):
            skills[name], _ = Skill.objects.get_or_create(name=name)

        projects_data = [
            {
                "name": "EduTracker",
                "description": (
                    "Сервис для отслеживания учебных целей "
                    "и командной работы студентов."
                ),
                "owner": users[0],
                "github_url": "https://github.com/maria/edutracker",
                "skills": ("Django", "JavaScript"),
            },
            {
                "name": "DevBoard",
                "description": "Доска задач для небольших команд pet-проектов.",
                "owner": users[1],
                "github_url": "https://github.com/alex/devboard",
                "skills": ("Python", "PostgreSQL", "Docker"),
            },
            {
                "name": "DesignHub",
                "description": "Платформа для совместного обсуждения дизайн-концепций.",
                "owner": users[2],
                "github_url": "https://github.com/olga/designhub",
                "skills": ("UI/UX", "JavaScript"),
            },
        ]
        projects = []
        for data in projects_data:
            skill_names = data.pop("skills")
            project, _ = Project.objects.get_or_create(name=data["name"], defaults=data)
            project.participants.add(project.owner)
            for skill_name in skill_names:
                project.skills.add(skills[skill_name])
            projects.append(project)

        users[0].favorites.add(projects[1])
        users[1].favorites.add(projects[0], projects[2])
        users[2].favorites.add(projects[0])
        projects[0].participants.add(users[1])
        projects[1].participants.add(users[2])
        self.stdout.write(self.style.SUCCESS("Demo data created"))
