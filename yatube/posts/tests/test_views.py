from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()


class PostPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.newauthor = User.objects.create_user(username='newauthor')
        cls.newgroup = Group.objects.create(
            title='Какая-то группа',
            slug='newgroup',
            description='Бла бла бла'
        )
        cls.newgroup2 = Group.objects.create(
            title='Какая-то группа 2',
            slug='newgroup2',
            description='Бла бла бла'
        )
        cls.post = Post.objects.create(
            text='Какой-то текст',
            group=cls.newgroup,
            author=cls.author,
            image='posts/Kasatka.jpg'
        )

        cls.templates_pages_name = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': PostPagesTests.newgroup.slug,
            }): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': PostPagesTests.author.username,
            }): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': PostPagesTests.post.id
            }): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={
                'post_id': PostPagesTests.post.id
            }): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        list = []
        for i in range(13):
            post = Post(
                text=f'Какой-то текст {i}',
                group=PostPagesTests.newgroup2,
                author=PostPagesTests.newauthor
            )
            list.append(post)
        cls.posts = Post.objects.bulk_create(list)

    def setUp(self):
        self.guest = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.author)
        self.newauthorized_client = Client()
        self.newauthorized_client.force_login(PostPagesTests.newauthor)

    def test_pages_uses_correct_template(self):
        for (reverse_name,
             template) in PostPagesTests.templates_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_index_page_show_correct_context(self):
        posts = Post.objects.all()
        response = self.authorized_client.get(reverse('posts:index'))
        page_objects = response.context['page_obj']
        for post in page_objects:
            with self.subTest(value=post):
                self.assertTrue(
                    post in posts,
                    f'Поста под номером "{post.id}" нет на главной странице'
                )

    def test_posts_group_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={
                'slug': PostPagesTests.newgroup.slug
            }),
        )
        except_group = PostPagesTests.newgroup
        post = Post.objects.filter(group=except_group).first()
        first_object = response.context['page_obj'][0]
        group = response.context['group']
        group_context = {
            first_object.text: post.text,
            first_object.author: post.author,
            first_object.group: post.group,
            first_object.pub_date: post.pub_date,
            group.title: except_group.title,
            group.description: except_group.description,
            first_object.image: post.image
        }
        for value, expect_value in group_context.items():
            with self.subTest(value=value):
                self.assertEqual(value, expect_value)

    def test_posts_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={
                'username': PostPagesTests.author.username
            }),
        )
        first_object = response.context['page_obj'][0]
        profile = response.context['profile']
        profile_context = {
            first_object.text: PostPagesTests.post.text,
            first_object.author: PostPagesTests.post.author,
            first_object.group: PostPagesTests.post.group,
            first_object.pub_date: PostPagesTests.post.pub_date,
            first_object.image: PostPagesTests.post.image,
            profile: PostPagesTests.author
        }
        for value, expect_value in profile_context.items():
            with self.subTest(value=value):
                self.assertEqual(value, expect_value)

    def test_posts_details_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={
                'post_id': PostPagesTests.post.id
            }),
        )
        post = response.context['post']
        post_context = {
            post.text: PostPagesTests.post.text,
            post.author: PostPagesTests.post.author,
            post.group: PostPagesTests.post.group,
            post.pub_date: PostPagesTests.post.pub_date,
            post.image: PostPagesTests.post.image
        }
        for value, expect_value in post_context.items():
            with self.subTest(value=value):
                self.assertEqual(value, expect_value)

    def test_posts_edit_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={
                'post_id': PostPagesTests.post.id
            }),
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_posts_create_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={
                'post_id': PostPagesTests.post.id
            }),
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_first_page_contains_ten_records(self):

        response = self.client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context['page_obj']),
            10,
            'На первой странице index не 10 постов'
        )
        response = self.client.get(reverse('posts:index'))

    def test_second_page_contains_fore_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']), 4,
            'На первой странице index не 4 постов'
        )

    def test_post_create_location(self):
        post = Post.objects.all().first()
        app_path = {
            'index': self.client.get(reverse('posts:index')),
            'group_list': self.guest.get(reverse('posts:group_list', kwargs={
                'slug': f'{post.group.slug}'
            })),
        }
        for name, response in app_path.items():
            self.assertTrue(
                post in response.context['page_obj'],
                f'Эленента нет на странице {name}'
            )

    def test_post_subscribe_authorized_client(self):
        count_follow = Follow.objects.all().count()
        self.authorized_client.get(reverse('posts:profile_follow', kwargs={
            'username': PostPagesTests.newauthor.username,
        }))
        self.assertEqual(
            Follow.objects.all().count(), count_follow + 1,
            'Количество подписчиков не изменилось'
        )

        self.authorized_client.get(reverse('posts:profile_unfollow', kwargs={
            'username': PostPagesTests.newauthor.username,
        }))
        self.assertEqual(
            Follow.objects.all().count(), count_follow,
            'Количество подписчиков не изменилось'
        )

    def test_post_subscribe_guest(self):
        count_follow = Follow.objects.all().count()
        self.guest.get(reverse('posts:profile_follow', kwargs={
            'username': PostPagesTests.newauthor.username,
        }))
        self.assertEqual(
            Follow.objects.all().count(), count_follow,
            'Не авторизированный пользователь может подписаться на автора'
        )

    def test_post_subscribe_post_location(self):
        following = Follow.objects.create(
            user=PostPagesTests.author,
            author=PostPagesTests.newauthor
        )
        post = Post.objects.create(
            text='Это пост',
            group=PostPagesTests.newgroup,
            author=PostPagesTests.newauthor,
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertTrue(
            post in response.context['page_obj'],
            'Пост не отобразился у подписчика'
        )
        response = self.newauthorized_client.get(reverse('posts:follow_index'))
        self.assertFalse(
            post in response.context['page_obj'],
            'Пост отобразился не у подписчика'
        )
        following.delete()

    def test_subskribe_on_self(self):
        count_follow = Follow.objects.all().count()
        self.authorized_client.get(reverse('posts:profile_follow', kwargs={
            'username': PostPagesTests.author.username,
        }))
        self.assertEqual(
            Follow.objects.all().count(), count_follow,
            'Нельзя подписываться на самого себя'
        )
