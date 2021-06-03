import json

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from rest_framework import status

from .models import Article
from .serializers import ArticleSerializer


class ArticleTest(TestCase):
    """ Test module for Article model """
    def setUp(self):
        user = User.objects.create_user(username='user1', password='12345')
        Article.objects.create(
            title='article1', slug='slug1', author=user, content='content1', published=True)

    def test_article(self):
        user = User.objects.get(username='user1')
        article = Article.objects.get(author=user)
        self.assertEqual(article.title, 'article1')
        self.assertEqual(article.slug, 'slug1')
        self.assertEqual(article.author, user)
        self.assertEqual(article.content, 'content1')
        self.assertEqual(article.published, True)


client = Client()


class GetAllArticlesTest(TestCase):
    """ Test module for GET all articles API """

    def setUp(self):
        user1 = User.objects.create_user(username='user1', password='12345')
        user2 = User.objects.create_user(username='user2', password='54321')
        Article.objects.create(
            title='article1', slug='slug1', author=user1, content='content1', published=True)
        Article.objects.create(
            title='article2', slug='slug2', author=user1, content='content2', published=True)
        Article.objects.create(
            title='article3', slug='slug3', author=user2, content='content3', published=False)
        Article.objects.create(
            title='article4', slug='slug4', author=user2, content='content4', published=False)

    def test_get_all_articles(self):
        # get API response
        response = client.get(reverse('api:list'))
        # get data from db
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GetSingleArticleTest(TestCase):
    """ Test module for GET single article API """

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='12345')
        self.user2 = User.objects.create_user(username='user2', password='54321')
        self.article1 = Article.objects.create(
            title='article1', slug='slug1', author=self.user1, content='content1', published=True)
        self.article2 = Article.objects.create(
            title='article2', slug='slug2', author=self.user1, content='content2', published=True)
        self.article3 = Article.objects.create(
            title='article3', slug='slug3', author=self.user2, content='content3', published=False)
        self.article4 = Article.objects.create(
            title='article4', slug='slug4', author=self.user2, content='content4', published=False)

    def test_get_valid_single_article(self):
        response = client.get(
            reverse('api:detail', kwargs={'pk': self.article3.pk}))
        article = Article.objects.get(pk=self.article3.pk)
        serializer = ArticleSerializer(article)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_single_article(self):
        response = client.get(
            reverse('api:detail', kwargs={'pk': 30}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CreateNewArticleTest(TestCase):
    """ Test module for inserting a new article """

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='12345')
        self.valid_payload = {
            "title": "article1",
            "slug": "slug1",
            "author": 1,
            "content": "content1",
            "published": False
        }
        self.invalid_payload = {
            "title": "",
            "slug": "slug1",
            "author": 1,
            "content": "content1",
            "published": False
        }

    def test_create_valid_article(self):
        response = client.post(
            reverse('api:list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_article(self):
        response = client.post(
            reverse('api:list'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateSingleArticleTest(TestCase):
    """ Test module for updating an existing article record """

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='12345')
        self.article1 = Article.objects.create(
            title='article1', slug='slug1', author=self.user1, content='content1', published=True)
        self.article2 = Article.objects.create(
            title='article2', slug='slug2', author=self.user1, content='content2', published=True)
        self.valid_payload = {
            "title": "new-article",
            "slug": "new-slug",
            "author": 1,
            "content": "change content1",
            "published": False
        }
        self.invalid_payload = {
            "title": "",
            "slug": "",
            "author": 1,
            "content": "content1",
            "published": False
        }

    def test_valid_update_article(self):
        response = client.put(
            reverse('api:detail', kwargs={'pk': self.article1.pk}),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_update_article(self):
        response = client.put(
            reverse('api:detail', kwargs={'pk': self.article1.pk}),
            data=json.dumps(self.invalid_payload),
            content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DeleteSingleArticleTest(TestCase):
    """ Test module for deleting an existing article record """

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='12345')
        self.article1 = Article.objects.create(
            title='article1', slug='slug1', author=self.user1, content='content1', published=True)
        self.article2 = Article.objects.create(
            title='article2', slug='slug2', author=self.user1, content='content2', published=True)

    def test_valid_delete_article(self):
        response = client.delete(
            reverse('api:detail', kwargs={'pk': self.article1.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_invalid_delete_article(self):
        response = client.delete(
            reverse('api:detail', kwargs={'pk': 30}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
