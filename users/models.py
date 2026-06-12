from io import BytesIO
from uuid import uuid4

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Укажите адрес электронной почты")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True")
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    phone = models.CharField(max_length=12, unique=True, null=True, blank=True)
    github_url = models.URLField(blank=True)
    about = models.TextField(max_length=256, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("name", "surname")

    class Meta:
        ordering = ("-id",)
        indexes = (models.Index(fields=("email",)),)

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar.save(self._avatar_filename(), self._avatar_content(), save=False)
        super().save(*args, **kwargs)

    def _avatar_filename(self):
        return f"avatar_{uuid4()}.png"

    def _avatar_content(self):
        size = 256
        colors = ("#E8EEF8", "#E8F5E9", "#FFF3E0", "#F3E5F5", "#E0F2F1")
        color = colors[hash((self.email or self.name or "teamfinder")) % len(colors)]
        image = Image.new("RGB", (size, size), color)
        draw = ImageDraw.Draw(image)
        letter = (self.name or self.email or "T")[:1].upper()
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 120)
        except OSError:
            font = ImageFont.load_default()
        box = draw.textbbox((0, 0), letter, font=font)
        x = (size - (box[2] - box[0])) / 2
        y = (size - (box[3] - box[1])) / 2 - 8
        draw.text((x, y), letter, fill="#2F3542", font=font)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return ContentFile(buffer.getvalue())

    def __str__(self):
        return f"{self.name} {self.surname}".strip() or self.email
