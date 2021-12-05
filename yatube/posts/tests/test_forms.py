import tempfile
import shutil

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from posts.forms import PostForm
from posts.models import Post, Group, User, Comment
from django.test import Client, TestCase, override_settings
from django.urls import reverse

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

TEST_SLUG = 'test_slug'
TEST_TEXT = 'Тестовый пост !'
TEST_DESCRIPTION = 'Тестовое описание'
TEST_TITLE = 'Тестовая группа'
POST_EDIT_TEXT = 'Тестовый текст отредактированного поста'
USERNAME = 'Maxim'
ANOTHER = 'Another'
TEST_SLUG2 = 'test_slug2'
TEST_TITLE2 = 'Тестовая группа2'
TEST_DESCRIPTION2 = 'Тестовое описание группы 2'
CREATE_POST_URL = reverse('posts:post_create')
AUTHORIZATION_URL = reverse('users:login') + '?next='
PROFILE_URL = reverse('posts:profile', kwargs={'username': USERNAME})
GROUP2_URL = reverse('posts:group_list', kwargs={'slug': TEST_SLUG2})
FIRST_GIF = 'small.gif'
SECOND_GIF = 'small2.gif'
THIRD_GIF = 'small3.gif'
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.other = User.objects.create_user(username=ANOTHER)
        cls.guest = Client()
        cls.user = cls.user
        cls.author = Client()
        cls.author.force_login(cls.user)
        cls.another = Client()
        cls.another.force_login(cls.other)
        cls.group = Group.objects.create(
            title=TEST_TITLE,
            slug=TEST_SLUG,
            description=TEST_DESCRIPTION
        )
        cls.group2 = Group.objects.create(
            title=TEST_TITLE,
            slug=TEST_SLUG2,
            description=TEST_DESCRIPTION2
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEST_TEXT,
            group=cls.group,
        )
        cls.form = PostForm()
        cls.POST_EDIT = reverse(
            'posts:post_edit',
            kwargs={'post_id': cls.post.id}
        )
        cls.POST_DETAIL = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.id}
        )
        cls.ADD_COMMENT_URL = reverse(
            'posts:add_comment',
            kwargs={'post_id': cls.post.id}
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        ids = set(Post.objects.all().values_list('id', flat=True))
        uploaded = SimpleUploadedFile(
            name=FIRST_GIF,
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст нового поста',
            'group': self.group.id,
            'image': uploaded
        }
        response = self.author.post(
            CREATE_POST_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, PROFILE_URL)
        created_posts = Post.objects.exclude(id__in=ids)
        self.assertEqual(len(created_posts), 1)
        post = created_posts.get()
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.image, f'posts/{FIRST_GIF}')

    def test_edit_post(self):
        uploaded = SimpleUploadedFile(
            name=SECOND_GIF,
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': POST_EDIT_TEXT,
            'group': self.group2.id,
            'image': uploaded
        }
        response = self.author.post(
            self.POST_EDIT,
            data=form_data,
            follow=True
        )
        post = response.context['post']
        self.assertRedirects(response, self.POST_DETAIL)
        self.assertEqual(
            post.image,
            f'{Post.image.field.upload_to}{SECOND_GIF}'
        )
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post.author)

    def test_creation_edition_of_post(self):
        variants_of_pages = {
            CREATE_POST_URL: self.author,
            self.POST_EDIT: self.author
        }
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for url, client in variants_of_pages.items():
            response = client.get(url)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_comment_of_posts(self):
        ids = set(Comment.objects.all().values_list('id', flat=True))
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.author.post(
            self.ADD_COMMENT_URL,
            data=form_data,
            follow=True
        )
        comments = Comment.objects.exclude(id__in=ids)
        self.assertEqual(len(comments), 1)
        comment = comments.get()
        self.assertRedirects(response, self.POST_DETAIL)
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)

    def test_anonymous_create_post(self):
        ids = set(Post.objects.all().values_list('id', flat=True))
        form_data = {
            'text': 'Тестовый текст нового поста',
            'group': self.group.id,
        }
        response = self.guest.post(
            CREATE_POST_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            AUTHORIZATION_URL + response.context['next']
        )
        created_posts = Post.objects.exclude(id__in=ids)
        self.assertEqual(len(created_posts), 0)

    def test_anonymous_comment(self):
        ids = set(Comment.objects.all().values_list('id', flat=True))
        form_data = {
            'text': 'Тестовый комментарий',
        }
        self.guest.post(
            self.ADD_COMMENT_URL,
            data=form_data,
            follow=True
        )
        comments = Comment.objects.exclude(id__in=ids)
        self.assertEqual(len(comments), 0)

    def test_not_author_edit_post(self):
        uploaded = SimpleUploadedFile(
            name=THIRD_GIF,
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': POST_EDIT_TEXT,
            'group': self.group2.id,
            'image': uploaded
        }
        cases = {
            self.guest: f'/auth/login/?next={self.POST_EDIT}',
            self.another: self.POST_DETAIL
        }
        for client, url in cases.items():
            with self.subTest(client=client):
                response = client.post(
                    self.POST_EDIT,
                    data=form_data,
                    follow=True
                )
                self.assertRedirects(response, url)
                post = Post.objects.get(pk=self.post.id)
                self.assertEqual(post.group, self.post.group)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.image, self.post.image)
