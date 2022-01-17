from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post, User

from . import constants


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=constants.TEST_USERNAME)
        cls.group = Group.objects.create(
            title="test-group",
            slug=constants.TEST_SLUG,
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
        response = self.guest_client.get(constants.MAIN_PAGE)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about(self):
        """Страница about/author доступна любому пользователю."""
        response = self.guest_client.get(constants.ABOUT_AUTHOR_PAGE)
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            "Page about/author/ not founded",
        )

    def test_tech(self):
        """Страница about/tech доступна любому пользователю."""
        response = self.guest_client.get(constants.ABOUT_TECH_PAGE)
        self.assertEqual(
            response.status_code, HTTPStatus.OK, "Page about/tech/ not founded"
        )

    def test_group_slug(self):
        """Страница group_slug доступна любому пользователю."""
        response = self.guest_client.get(
            constants.GROUP_PAGE + constants.TEST_SLUG + constants.MAIN_PAGE
        )
        self.assertEqual(
            response.status_code, HTTPStatus.OK, "Page group/slug not founded"
        )

    def test_profile_username(self):
        """Страница profile_username доступна любому пользователю."""
        response = self.guest_client.get(
            constants.PROFILE_PAGE
            + constants.TEST_USERNAME
            + constants.MAIN_PAGE
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            "Page profile/username not founded",
        )

    def test_post_id(self):
        """Страница post_id доступна любому пользователю."""
        print("TUTA")
        print(self.post.pk)
        response = self.guest_client.get(
            constants.POSTS_PAGE + str(self.post.pk) + constants.MAIN_PAGE
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            "Page posts/post_id not founded",
        )

    # Проверяем доступность страниц для автора
    def test_post_id_edit(self):
        """Страница post_id_edit доступна author post."""
        response = self.author_post.get(
            constants.POSTS_PAGE + self.post.pk + constants.EDIT_PAGE
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            "Page posts/post_id_edit not founded",
        )

    # Проверяем доступность страниц для автора
    def test_create(self):
        """Страница create доступна authorized client."""
        response = self.authorized_client.get(constants.CREATE_PAGE)
        self.assertEqual(
            response.status_code, HTTPStatus.OK, "Page create not founded"
        )

    # Проверяем unexisting page
    def test_post_id_edit(self):
        """Страница non exist."""
        response = self.authorized_client.get(constants.UNEXISTING_PAGE)
        self.assertEqual(
            response.status_code, HTTPStatus.OK.NOT_FOUND, "Page not founded "
        )

    # Проверка вызываемых шаблонов для каждого адреса
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            "/": "posts/index.html",
            "/group/test-slug/": "posts/group_list.html",
            "/profile/auth/": "posts/profile.html",
            "/posts/1/": "posts/post_detail.html",
            constants.CREATE_PAGE: "posts/create_post.html",
            "/posts/1/edit/": "posts/create_post.html",
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
