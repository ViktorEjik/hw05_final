from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    """Проверяем все URL-ы приложения Post"""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_autor = User.objects.create_user(username='author')
        cls.user_not_autor = User.objects.create_user(username='no_autor')
        cls.group = Group.objects.create(
            title='Какая-то группа',
            slug='newgroup',
            description='Бла бла бла'
        )
        cls.post = Post.objects.create(
            text='Какой-то текст',
            group=cls.group,
            author=cls.user_autor
        )

        cls.post_url = f'/posts/{cls.post.id}/'

        cls.public_urls = (
            ('/', 'posts/index.html'),
            (f'/group/{cls.group.slug}/', 'posts/group_list.html'),
            (cls.post_url, 'posts/post_detail.html'),
        )

        cls.author_urls = (
            (f'/posts/{cls.post.id}/edit/', 'posts/create_post.html'),
        )

        cls.not_author_urls = (
            ('/create/', 'posts/create_post.html'),
            (f'/profile/{cls.user_autor.username}/', 'posts/profile.html'),
        )

        cls.guest_redirect = (
            (f'/posts/{cls.post.id}/edit/',
             f'/auth/login/?next=/posts/{cls.post.id}/edit/'),
            ('/create/', '/auth/login/?next=/create/'),
        )

        cls.not_author_redirect = (
            (f'/posts/{cls.post.id}/edit/',
             f'/auth/login/?next=/posts/{cls.post.id}/edit/'),
        )

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(PostURLTest.user_autor)

        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTest.user_not_autor)

    def test_public_urls_exists_and_use_correct_teamplate(self):

        for (address, except_teamplate) in PostURLTest.public_urls:
            with self.subTest(address=address):
                ansver = self.guest_client.get(address)
                self.assertEqual(
                    ansver.status_code,
                    HTTPStatus.OK,
                    (f'Путь {address}, ожидался статус код {HTTPStatus.OK},'
                     f' а получен {ansver.status_code}'))
                self.assertTemplateUsed(ansver, except_teamplate)

    def test_posts_urls_exists_at_desired_location_authorized_no_author(self):

        for (address, except_teamplate) in (PostURLTest.not_author_urls):
            with self.subTest(address=address):
                ansver = self.authorized_client.get(address)
                self.assertEqual(
                    ansver.status_code,
                    HTTPStatus.OK,
                    (f'Путь {address}, ожидался статус код {HTTPStatus.OK},'
                     f' а получен {ansver.status_code}')
                )
                self.assertTemplateUsed(ansver, except_teamplate)

    def test_posts_urls_exists_at_desired_location_authorized(self):

        for (address, except_teamplate) in (PostURLTest.author_urls
                                            + PostURLTest.not_author_urls
                                            + PostURLTest.public_urls):
            with self.subTest(address=address):
                ansver = self.authorized_client_author.get(address)
                self.assertEqual(
                    ansver.status_code,
                    HTTPStatus.OK,
                    (f'Путь {address}, ожидался статус код {HTTPStatus.OK},'
                     f' а получен {ansver.status_code}')
                )
                self.assertTemplateUsed(ansver, except_teamplate)

    def test_gests_rederect(self):
        for (address, redirect) in PostURLTest.guest_redirect:
            ansver = self.guest_client.get(address)
            self.assertRedirects(ansver, redirect)

    def test_no_autor_redirect(self):
        for (address, redirect) in (PostURLTest.not_author_redirect):
            ansver = self.guest_client.get(address)
            self.assertRedirects(ansver, redirect)
