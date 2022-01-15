from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Post, Group

User = get_user_model()


class PostModelTest(TestCase):
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
            text="test-group",
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        # self.user = PostModelTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_post = Post.author

    # Проверяем общедоступные страницы
    def test_homepage(self):
        """Страница homepage/ доступна любому пользователю."""
        response = self.guest_client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_about(self):
        """Страница about/author доступна любому пользователю."""
        response = self.guest_client.get("/about/author/")
        self.assertEqual(
            response.status_code, 200, "Page about/author/ not founded"
        )

    def test_tech(self):
        """Страница about/tech доступна любому пользователю."""
        response = self.guest_client.get("/about/tech/")
        self.assertEqual(
            response.status_code, 200, "Page about/tech/ not founded"
        )

    def test_group_slug(self):
        """Страница group_slug доступна любому пользователю."""
        response = self.guest_client.get("/group/test-slug/")
        self.assertEqual(
            response.status_code, 200, "Page group/slug not founded"
        )

    def test_profile_username(self):
        """Страница profile_username доступна любому пользователю."""
        response = self.guest_client.get("/profile/auth/")
        self.assertEqual(
            response.status_code, 200, "Page profile/username not founded"
        )

    def test_post_id(self):
        """Страница post_id доступна любому пользователю."""
        response = self.guest_client.get("/posts/1/")
        self.assertEqual(
            response.status_code, 200, "Page posts/post_id not founded"
        )

    # Проверяем доступность страниц для автора
    def test_post_id_edit(self):
        """Страница post_id_edit доступна author post."""
        response = self.author_post.get("/posts/1/edit/")
        self.assertEqual(
            response.status_code, 200, "Page posts/post_id_edit not founded"
        )

    # Проверяем доступность страниц для автора
    def test_create(self):
        """Страница create доступна authorized client."""
        response = self.authorized_client.get("/create/")
        self.assertEqual(response.status_code, 200, "Page create not founded")

    # Проверяем unexisting page
    def test_post_id_edit(self):
        """Страница non exist."""
        response = self.authorized_client.get("/unexisting_page/")
        self.assertEqual(response.status_code, 404, "Page not founded ")

    # Проверка вызываемых шаблонов для каждого адреса
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            "/": "posts/index.html",
            "/group/test-slug/": "posts/group_list.html",
            "/profile/auth/": "posts/profile.html",
            "/posts/1/": "posts/post_detail.html",
            "/create/": "posts/create_post.html",
            "/posts/1/edit/": "posts/create_post.html",
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
