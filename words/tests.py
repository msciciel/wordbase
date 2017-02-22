from django.test import TestCase
from django.utils import timezone
from django.shortcuts import reverse

from datetime import timedelta
from .models import Word, User


def create_word(word_text, days=0):
    """
    Creates a word with given `word_text` and added the given number of `days` offset to now (negative for words added
    in the past, positive for words that added in the future).
    """
    time = timezone.now() + timedelta(days=days)
    word = Word.objects.create(word_text=word_text, add_date=time)
    word.save()
    return word


def create_user(username, password):
    user = User.objects.create_user(username=username, password=password)
    user.save
    return user


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
    def test_index_view_user_with_no_words(self):
        """
        If no words exists, an appropriate message should be displayed.
        """
        credentials = {'username': 'student', 'password': 'student'}
        create_user(**credentials)

        self.client.login(**credentials)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No words are added to database.")
        self.assertQuerysetEqual(response.context['words_list'], [])

    def test_index_view_user_with_words(self):
        """
        Index page should return list of words for user.
        """
        credentials = {'username': 'student', 'password': 'student'}
        user = create_user(**credentials)
        word1 = create_word('word1')
        word2 = create_word('word2')
        create_word('word3')
        user.words.add(word1)
        user.words.add(word2)
        user.save()

        self.client.login(**credentials)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "word1")
        self.assertContains(response, "word2")
        self.assertQuerysetEqual(response.context['words_list'], ['<Word: word1>', '<Word: word2>'])

    def test_parse_view(self):
        """
        Parser page should return form for pasting text.
        """
        credentials = {'username': 'student', 'password': 'student'}
        user = create_user(**credentials)
        user.save()

        self.client.login(**credentials)
        response = self.client.get(reverse('words:parse'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Paste text to parse:")
        self.assertContains(response, '<form action="/words/extract/" method="post">')

    def test_exract_view_with_empty_text(self):
        """
        If no new words were found, an appropriate message should be displayed.
        """
        credentials = {'username': 'student', 'password': 'student'}
        user = create_user(**credentials)
        user.save()

        self.client.login(**credentials)
        response = self.client.post(reverse('words:extract'), {'text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Extracted words:")
        self.assertContains(response, "No new words were found !")

    def test_exract_view_with_only_new_words_text(self):
        """
        Extract page should return list of new words from pasted text.
        """
        credentials = {'username': 'student', 'password': 'student'}
        user = create_user(**credentials)
        user.save()
        create_word('media')
        create_word('dismissed')

        self.client.login(**credentials)
        text = """The court said the criminal case against him should be dismissed and
         he had a "right to rehabilitation", Russian media report."""
        words = sorted([
            'the', 'court', 'said', 'criminal', 'case', 'against', 'him', 'should', 'dismissed', 'and',
            'had', 'right', 'rehabilitation', 'russian', 'media', 'report'
        ])
        response = self.client.post(reverse('words:extract'), {'text': text})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Extracted words:")
        new_words = sorted(list(response.context['words'].keys()))
        self.assertListEqual(new_words, words)

    def test_exract_view_with_new_words_text(self):
        """
        Extract page should return list of new words from pasted text.
        """
        credentials = {'username': 'student', 'password': 'student'}
        user = create_user(**credentials)
        create_word('media')
        create_word('dismissed')
        user.words.add(create_word('criminal'))
        user.words.add(create_word('against'))
        user.words.add(create_word('should'))
        user.save()

        self.client.login(**credentials)
        text = """The court said the criminal case against him should be dismissed and
         he had a "right to rehabilitation", Russian media report."""
        words = sorted([
            'the', 'court', 'said', 'case', 'him', 'dismissed', 'and',
            'had', 'right', 'rehabilitation', 'russian', 'media', 'report'
        ])
        response = self.client.post(reverse('words:extract'), {'text': text})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Extracted words:")
        new_words = sorted(list(response.context['words'].keys()))
        self.assertListEqual(new_words, words)

    def test_save_view_with_only_new_words(self):
        """
        Save page should return list of new words from pasted text.
        """
        credentials = {'username': 'student', 'password': 'student'}
        user = create_user(**credentials)

        self.client.login(**credentials)
        words = ['the', 'court', 'said', 'case', 'him', 'dismissed', 'and']
        response = self.client.post(reverse('words:save'), {'words': words})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Saved words:")
        self.assertListEqual(sorted(response.context['words']), sorted(words))
        self.assertQuerysetEqual(
            user.words.all().order_by('word_text'),
            ['<Word: {}>'.format(w) for w in sorted(words)]
        )

    def test_save_view_with_mixed_new_words(self):
        """
        Save page should return list of only new words from pasted text.
        """
        credentials = {'username': 'student', 'password': 'student'}
        user = create_user(**credentials)
        for word in ['case', 'him']:
            user.words.add(create_word(word))

        self.client.login(**credentials)
        words = ['the', 'court', 'said', 'case', 'him', 'dismissed', 'and']
        new_words = words.copy()
        new_words.remove('case')
        new_words.remove('him')
        response = self.client.post(reverse('words:save'), {'words': words})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Saved words:")
        self.assertListEqual(sorted(response.context['words']), sorted(new_words))

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        for word in words:
            self.assertContains(response, word)
        self.assertQuerysetEqual(
            response.context['words_list'],
            ['<Word: {}>'.format(w) for w in sorted(words)]
        )
