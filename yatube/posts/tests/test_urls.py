from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post, User

TEST_SLUG = 'test_slug'
TEST_TEXT = 'Тестовый пост !'
TEST_DESCRIPTION = 'Тестовое описание'
TEST_TITLE = 'Тестовая группа'
USERNAME = 'Maxim'
INDEX_URL = reverse('posts:index')
GROUP_URL = reverse('posts:group_list', kwargs={'slug': TEST_SLUG})
PROFILE_URL = reverse('posts:profile', kwargs={'username': USERNAME})
CREATE_POST_URL = reverse('posts:post_create')
AUTHORIZATION_PAGE = reverse('users:login')
FOLLOW_INDEX_URL = reverse('posts:follow_index')
PROFILE_UNFOLLOW_URL = reverse(
    'posts:profile_unfollow',
    kwargs={'username': USERNAME}
)
PROFILE_FOLLOW_URL = reverse(
    'posts:profile_follow',
    kwargs={'username': USERNAME}
)
AUTHOR = 'Author'


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.auth = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=TEST_TITLE,
            slug=TEST_SLUG,
            description=TEST_DESCRIPTION
        )
        cls.post = Post.objects.create(
            author=cls.auth,
            text=TEST_TEXT,
            group=cls.group
        )
        cls.guest = Client()
        cls.another = Client()
        cls.author = Client()
        cls.another.force_login(cls.user)
        cls.author.force_login(cls.auth)
        cls.POST_EDIT_URL = reverse(
            'posts:post_edit',
            kwargs={'post_id': cls.post.id}
        )
        cls.POST_DETAIL_URL = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.id}
        )

    def test_pages_for_guest_client(self):
        variants_of_pages = [
            [INDEX_URL, self.guest, 200],
            [GROUP_URL, self.guest, 200],
            [PROFILE_URL, self.another, 200],
            [CREATE_POST_URL, self.another, 200],
            [self.POST_DETAIL_URL, self.guest, 200],
            [self.POST_EDIT_URL, self.author, 200],
            ['/unexisting_page/', self.guest, 404],
            [CREATE_POST_URL, self.guest, 302],
            [self.POST_EDIT_URL, self.another, 302],
            [self.POST_EDIT_URL, self.guest, 302],
            [FOLLOW_INDEX_URL, self.author, 200],
            [FOLLOW_INDEX_URL, self.guest, 302],
            [PROFILE_FOLLOW_URL, self.author, 302],
            [PROFILE_FOLLOW_URL, self.guest, 302],
            [PROFILE_UNFOLLOW_URL, self.author, 302],
            [PROFILE_UNFOLLOW_URL, self.guest, 302]
        ]
        for url, client, status_code in variants_of_pages:
            with self.subTest(url=url, clent=client):
                self.assertEqual(client.get(url).status_code, status_code)

    def test_urls_uses_correct_template(self):
        cases = {
            INDEX_URL: 'posts/index.html',
            GROUP_URL: 'posts/group_list.html',
            PROFILE_URL: 'posts/profile.html',
            self.POST_DETAIL_URL: 'posts/post_detail.html',
            self.POST_EDIT_URL: 'posts/create_post.html',
            CREATE_POST_URL: 'posts/create_post.html',
        }
        for adress, template in cases.items():
            with self.subTest(adress=adress):
                self.assertTemplateUsed(self.author.get(adress), template)

    def test_rediect_urls(self):
        variants_of_redirection = [
            [self.POST_EDIT_URL, self.another, self.POST_DETAIL_URL],
            [self.POST_EDIT_URL,
             self.guest,
             f'{AUTHORIZATION_PAGE}?next={self.POST_EDIT_URL}'],
            [CREATE_POST_URL,
             self.guest,
             f'{AUTHORIZATION_PAGE}?next={CREATE_POST_URL}']
        ]
        for url, client, redirect_url in variants_of_redirection:
            with self.subTest(url=url, redirect_url=redirect_url):
                self.assertEqual(client.get(url).url, redirect_url)
