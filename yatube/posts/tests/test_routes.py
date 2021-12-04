from django.test import TestCase
from django.urls import reverse

SLUG = 'test_slug'
USERNAME = 'Maxim'
POST_ID = 1


class PostsRoutesTest(TestCase):
    def test_routes(self):
        variants = [
            ['/', 'index', []],
            ['/create/', 'post_create', []],
            ['/follow/', 'follow_index', []],
            [f'/group/{SLUG}/', 'group_list', [SLUG]],
            [f'/profile/{USERNAME}/', 'profile', [USERNAME]],
            [f'/posts/{POST_ID}/', 'post_detail', [POST_ID]],
            [f'/posts/{POST_ID}/edit/', 'post_edit', [POST_ID]],
            [f'/profile/{USERNAME}/follow/', 'profile_follow', [USERNAME]],
            [f'/posts/{POST_ID}/comment/', 'add_comment', [POST_ID]],
            [f'/profile/{USERNAME}/unfollow/', 'profile_unfollow', [USERNAME]],
        ]
        for url, name, arg in variants:
            with self.subTest(url=url):
                self.assertEqual(url, reverse(f'posts:{name}', args=arg))
