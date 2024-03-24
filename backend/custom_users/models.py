from django.db import models
from django.contrib.auth.models import AbstractUser

from .validators import username_validator


class User(AbstractUser):
    """Модель пользователя."""
    email = models.EmailField(verbose_name='email', max_length=256, unique=True)
    username = models.CharField(
        verbose_name='username',
        max_length=150,
        validators=[username_validator],
        unique=True
    )
    first_name = models.CharField(max_length=150, verbose_name="Имя")
    last_name = models.CharField(max_length=150, verbose_name="Фамилия")
    password = models.CharField(max_length=150)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["username"]

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        verbose_name="Подписчик",
        on_delete=models.CASCADE,
        related_name="follower",
    )
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name="following",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ["author"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_user_author",
            )
        ]

    def __str__(self):
        return f"{self.user} подписчик автора - {self.author}"
