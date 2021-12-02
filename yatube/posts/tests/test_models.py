from django.test import TestCase

from posts.models import Group, Post, User

TEST_SLUG = 'test_slug'
TEST_TEXT = 'Тестовый пост !'
TEST_DESCRIPTION = 'Тестовое описание'
TEST_TITLE = 'Тестовая группа'
USERNAME = 'Maxim'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title=TEST_TITLE,
            slug=TEST_SLUG,
            description=TEST_DESCRIPTION
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEST_TEXT
        )

    def test_models_have_correct_object_names(self):
        self.assertEqual(str(self.post), self.post.text[:15])
        self.assertEqual(str(self.group), self.group.title)

    def test_verbose_name_post(self):
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_verbose_name_group(self):
        field_verboses = {
            'title': 'Название',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Group._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text_post(self):
        field_help_text = {
            'text': 'Введите текст',
            'group': 'Выбирите группу'
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).help_text,
                    expected_value
                )
