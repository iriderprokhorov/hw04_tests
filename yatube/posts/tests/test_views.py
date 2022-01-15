# deals/tests/test_views.py
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.posts_obj = []
        cls.user = User.objects.create_user(username="auth")
        # group-test1
        cls.group1 = Group.objects.create(
            title="test-group1",
            slug="test-slug1",
            description="test-descriptipon1",
        )
        # group-test2
        cls.group2 = Group.objects.create(
            title="test-group2",
            slug="test-slug2",
            description="test-descriptipon2",
        )
        # add 15 posts group1
        for i in range(1, 15):
            cls.posts_obj.append(
                Post(
                    author=cls.user,
                    text="test-text" + str(i),
                    group=cls.group1,
                )
            )
        # add 15 posts group2
        for i in range(16, 30):
            cls.posts_obj.append(
                Post(
                    author=cls.user,
                    text="test-text" + str(i),
                    group=cls.group2,
                )
            )
        cls.posts = Post.objects.bulk_create(cls.posts_obj)
        # without group
        cls.posts_obj.append(Post(author=cls.user, text="test-text31"))

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        # self.user = PostModelTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_post = Post.author

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", kwargs={"slug": "test-slug1"}
            ): "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={"username": "auth"}
            ): "posts/profile.html",
            reverse(
                "posts:post_detail", kwargs={"post_id": "1"}
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit", kwargs={"pk": "1"}
            ): "posts/create_post.html",
            reverse("posts:post_create"): "posts/create_post.html",
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверка контекста страниц
    def test_home_page_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse("posts:index"))
        first_object = response.context["page_obj"][0]
        self.assertEqual(str(first_object.text), "test-text1")

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slug1"})
        )
        first_object = response.context["page_obj"][0]
        self.assertEqual(str(first_object.text), "test-text1")
        self.assertEqual(str(first_object.group), "test-group1")

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse("posts:profile", kwargs={"username": "auth"})
        )
        first_object = response.context["page_obj"][0]
        self.assertEqual(str(first_object.text), "test-text1")
        self.assertEqual(str(first_object.author), "auth")
        self.assertEqual(str(first_object.group), "test-group1")

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse("posts:post_detail", kwargs={"post_id": "1"})
        )
        self.assertEqual(str(response.context["post"]), "test-text1")
        self.assertEqual(str(response.context["post"].pk), "1")

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit с правильным контекстом."""
        response = self.guest_client.get(
            reverse("posts:post_edit", kwargs={"pk": "1"})
        )
        self.assertEqual(str(response.context["post"]), "test-text1")
        self.assertEqual(str(response.context["is_edit"]), "True")
        self.assertEqual(str(response.context["post"].pk), "1")
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_post_create_show_correct_context(self):
        """Шаблон post_create с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:post_create"))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    # Проверяем паджинатор
    def test_index_page_contains_31(self):
        """На страницу index выводится по 10 постов"""
        response = self.client.get(reverse("posts:index"))
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_group_list_page_contains_15(self):
        """На страницу group_list выводится 10 постов"""
        response = self.client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slug1"})
        )
        self.assertEqual(len(response.context["page_obj"]), 10)

    def test_profile_page_contains_31(self):
        """На страницу profile выводится 10 постов"""
        response = self.client.get(
            reverse("posts:profile", kwargs={"username": "auth"})
        )
        self.assertEqual(len(response.context["page_obj"]), 10)

    # Проверка создания поста с указанием группы на главной,на страницы
    # группы и в профайле уже протестирована. Проверим что пост не попал в чужую группу
    def test_post_create_with_group_show_correct_context(self):
        """Создание поста с указанием группы."""
        response = self.guest_client.get(
            reverse("posts:group_list", kwargs={"slug": "test-slug2"})
        )
        for i in range(0, len(response.context["post_list"])):
            # self.assertEqual(str(obj.text), "test-text1")
            self.assertEqual(
                str(response.context["post_list"][i].group), "test-group2"
            )
            # print(str(response.context["post_list"][i].group))
