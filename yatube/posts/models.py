from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField("имя", max_length=200)
    slug = models.SlugField("адрес", unique=True)
    description = models.TextField("описание")

    class Meta:
        verbose_name = "Groups, it will be shown in admin panel"

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField("заголовок")
    pub_date = models.DateTimeField("дата публикации", auto_now_add=True)
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name="сообщество",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="автор",
    )

    class Meta:
        verbose_name = "Posts, it will be shown in admin panel"
        ordering = (
            "pk",
            "-pub_date",
        )

    def __str__(self):
        return self.text
