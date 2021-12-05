from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, User, Follow, Comment
from posts.settings import POSTS_ON_PAGE


TEST_SLUG = 'test_slug'
TEST_TEXT = 'Тестовый пост !'
TEST_DESCRIPTION = 'Тестовое описание'
TEST_TITLE = 'Тестовая группа'
USERNAME = 'Maxim'
FOLLOWER = 'follower'
TEST_SLUG2 = 'test_slug2'
TEST_TITLE2 = 'Тестовая группа2'
TEST_DESCRIPTION2 = 'Тестовое описание группы 2'
INDEX_URL = reverse('posts:index')
FOLLOW_INDEX_URL = reverse('posts:follow_index')
GROUP_URL = reverse('posts:group_list', kwargs={'slug': TEST_SLUG})
PROFILE_URL = reverse('posts:profile', kwargs={'username': USERNAME})
GROUP2_URL = reverse('posts:group_list', kwargs={'slug': TEST_SLUG2})
PROFILE_UNFOLLOW_URL = reverse(
    'posts:profile_unfollow',
    kwargs={'username': USERNAME}
)
PROFILE_FOLLOW_URL = reverse(
    'posts:profile_follow',
    kwargs={'username': USERNAME}
)
POSTS_ON_SECOND_PAGE = 3


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.follower = User.objects.create_user(username=FOLLOWER)
        cls.guest_client = Client()
        cls.user = cls.user
        cls.follow_client = Client()
        cls.follow_client.force_login(cls.follower)
        cls.author = Client()
        cls.author.force_login(cls.user)
        cls.group = Group.objects.create(
            title=TEST_TITLE,
            slug=TEST_SLUG,
            description=TEST_DESCRIPTION
        )
        cls.second_group = Group.objects.create(
            slug=TEST_SLUG2,
            title=TEST_TITLE2,
            description=TEST_DESCRIPTION2
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEST_TEXT,
            group=cls.group
        )
        cls.POST_DEATAIL_URL = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.id}
        )

    def test_pages_shows_correct_context(self):
        Follow.objects.create(user=self.follower, author=self.user)
        urls = [
            INDEX_URL,
            GROUP_URL,
            PROFILE_URL,
            self.POST_DEATAIL_URL,
            FOLLOW_INDEX_URL
        ]
        for url in urls:
            response = self.follow_client.get(url)
            if 'page_obj' in response.context:
                self.assertEqual(len(response.context['page_obj']), 1)
                post = response.context['page_obj'][0]
            else:
                post = response.context['post']
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.group, self.post.group)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.id, self.post.id)
            self.assertEqual(post.image, self.post.image)

    def test_post_in_other_group(self):
        response = self.author.get(GROUP2_URL)
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_author_on_page_profile(self):
        response = self.author.get(PROFILE_URL)
        self.assertEqual(response.context['author'], self.user)

    def test_group_on_group_page(self):
        response = self.author.get(GROUP_URL)
        self.assertEqual(response.context['group'], self.group)
        self.assertEqual(response.context['group'].title, self.group.title)
        self.assertEqual(response.context['group'].slug, self.group.slug)
        self.assertEqual(
            response.context['group'].description,
            self.group.description
        )

    def test_comments_on_post_detail_page(self):
        comment_text = 'Тестовый комментарий'
        Comment.objects.create(
            author=self.user,
            text=comment_text,
            post=self.post,
        )
        response = self.author.get(self.POST_DEATAIL_URL)
        self.assertEqual(len(response.context['comments']), 1)
        comment = response.context['post'].comments.all()[0]
        self.assertEqual(comment.text, comment_text)
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)

    def test_cache_on_index_page(self):
        cache.clear()
        response = self.author.get(INDEX_URL)
        Post.objects.all().delete()
        Post.objects.create(
            text=TEST_TEXT,
            author=self.user,
        )
        second_response = self.author.get(INDEX_URL)
        self.assertEqual(response.content, second_response.content)
        cache.clear()
        third_response = self.author.get(INDEX_URL)
        self.assertNotEqual(response.content, third_response.content)

    def test_users_can_unfollow(self):
        Follow.objects.create(author=self.user, user=self.follower)
        self.follow_client.get(
            PROFILE_UNFOLLOW_URL,
            follow=True
        )
        self.assertEqual(len(Follow.objects.all()), 0)

    def test_users_can_follow(self):
        self.follow_client.get(
            PROFILE_FOLLOW_URL,
            follow=True
        )
        self.assertEqual(len(Follow.objects.all()), 1)

    def test_post_on_other_follow_page(self):
        response = self.author.get(FOLLOW_INDEX_URL)
        self.assertNotIn(self.post, response.context['page_obj'])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.guest = Client()
        cls.author = Client()
        cls.author.force_login(cls.user)
        cls.group = Group.objects.create(
            title=TEST_TITLE,
            slug=TEST_SLUG,
            description=TEST_DESCRIPTION
        )
        Post.objects.bulk_create(Post(
            author=cls.user,
            text=TEST_TEXT + f'{i}',
            group=cls.group
        ) for i in range(POSTS_ON_PAGE + POSTS_ON_SECOND_PAGE)
        )

    def test_first_page(self):
        urls = [
            INDEX_URL,
            GROUP_URL,
            PROFILE_URL,
        ]
        for url in urls:
            response = self.author.get(url)
            self.assertEqual(len(response.context['page_obj']),
                             POSTS_ON_PAGE)

    def test_second_page(self):
        urls = [
            INDEX_URL,
            GROUP_URL,
            PROFILE_URL,
        ]
        for url in urls:
            response = self.author.get(f'{url}?page=2')
            self.assertEqual(len(response.context['page_obj']),
                             POSTS_ON_SECOND_PAGE)
