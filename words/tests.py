from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User

from datetime import timedelta
from .models import Word


def create_word(word_text, days):
    """
    Creates a word with given `word_text` and added the given number of `days` offset to now (negative for words added
    in the past, positive for words that added in the future).
    """
    time = timezone.now() + timedelta(days=days)
    return Word.objects.create(word_text=word_text, add_date=time)


class LoginTests(TestCase):
    def test_login_homepage(self):
        """
        Not logged user should be redirected to login form.
        """
        response = self.client.get('/')
        self.assertRedirects(response, '/words/login/?next=/')

    def test_login_words_index(self):
        """
        Not logged user should be redirected to login form.
        """
        response = self.client.get('/words/')
        self.assertRedirects(response, '/words/login/?next=/words/')


class WordsViewIndexTests(TestCase):
    def test_index_view_with_no_words(self):
        """
        If no words exists, an appropriate message should be displayed.
        """
        User.objects.create_user(username='example', password='example')
        self.client.login(username='example', password='example')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No words are added to database.")
        self.assertQuerysetEqual(response.context['words_list'], [])
