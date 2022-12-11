from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class CreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='author')
        cls.Group1 = Group.objects.create(
            title='Какаято  группа',
            slug='slug',
            description='Бла бла бла'
        )
        cls.Group2 = Group.objects.create(
            title='Какаято  группа 1',
            slug='slug1',
            description='Бла бла бла'
        )
        cls.post = Post.objects.create(
            text='Какойто текст',
            group=cls.Group1,
            author=cls.user,
            image='posts/Kasatka.jpg'
        )

    def setUp(self):
        self.user = User.objects.get(username='author')
        self.guest = Client()
        self.client = Client()
        self.client.force_login(self.user)

    def test_cant_create_none_text(self):

        tasks_count = Post.objects.count()
        form_data = {
            'text': '',
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), tasks_count)
        self.assertFormError(
            response,
            'form',
            'text',
            'Обязательное поле.'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit(self):
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'text',
        }
        self.client.post(
            reverse('posts:post_edit', kwargs={'post_id': 1}),
            data=form_data,
            follow=True
        )
        post = Post.objects.get(id=1)
        self.assertEqual(
            Post.objects.count(),
            tasks_count,
            'Не совпадает количество постов'
        )
        self.assertNotEqual(
            post.text,
            CreateFormTests.post.text,
            'Значения поля text не изменено'
        )
        self.assertNotEqual(
            post.group,
            CreateFormTests.post.group,
            'Значения поля group не изменено'
        )

    def test_post_create_(self):
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'text',
            'image': 'posts/Kasatka.jpg'
        }
        self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), tasks_count + 1)

    def test_comment_form(self):
        count_comments = CreateFormTests.post.comments.count()
        form_data = {
            'text': 'text',
        }
        self.client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': CreateFormTests.post.id}
            ),
            data=form_data,
            follow=True,
        )
        self.assertEqual(
            CreateFormTests.post.comments.count(),
            count_comments + 1
        )
