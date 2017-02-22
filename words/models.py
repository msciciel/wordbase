from django.db import models
from django.contrib.auth.models import User, AbstractUser


class Word(models.Model):
    word_text = models.CharField(max_length=100, unique=True)
    add_date = models.DateField('date added')

    def __str__(self):
        return self.word_text


class User(AbstractUser):
    words = models.ManyToManyField(Word)
