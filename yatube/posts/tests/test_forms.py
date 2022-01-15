from posts.forms import PostForm
from posts.models import Post, Group
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client, TestCase

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="test-group",
            slug="test-slug",
            description="test-descriptipon",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="test-post",
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post"""
        # Посчитали количество постов до
        posts_count = Post.objects.count()
        form_data = {"text": "test-post-create", "group": self.group.pk}
        # Отправили POST-запрос
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        # Проверили редирект
        self.assertRedirects(
            response, reverse("posts:profile", kwargs={"username": "auth"})
        )
        # Посчитали количество постов после
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверили, что пост сохранился в бд
        print("amount posts", posts_count)
        self.assertTrue(
            Post.objects.filter(
                text="test-post-create", group=self.group
            ).exists()
        )

    def test_post_edit(self):
        """Валидная форма редактирует запись в Post"""
        form_data = {
            "text": "test-post-edit",
            "group": self.group.pk,
        }
        # Отправили POST-запрос
        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"pk": "1"}),
            data=form_data,
            follow=True,
            is_edit=True,
        )
        # Проверили редирект
        self.assertRedirects(
            response,
            reverse("posts:post_detail", kwargs={"post_id": "1"}),
        )
        # Проверили, что пост обновлен
        self.assertTrue(
            Post.objects.filter(
                text="test-post-edit", id="1", group=self.group
            ).exists()
        )
