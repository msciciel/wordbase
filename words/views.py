from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.contrib.auth.decorators import login_required


from .models import Word

import re


@login_required
def index(request):
    words_list = Word.objects.order_by('word_text')
    context = {
        'words_list': words_list,
    }
    return render(request, 'words/index.html', context)


@login_required
def detail(request, word_id):
    word = get_object_or_404(Word, pk=word_id)
    context = {
        'word': word
    }
    return render(request, 'words/detail.html', context)


@login_required
def parse(request):
    return render(request, 'words/parse.html')


@login_required
def extract(request):
    try:
        text = request.POST['text']
    except KeyError:
        context = {
            'error_message': "You didn't provide text data."
        }
        return render(request, 'words/parse.html', context)
    else:
        words = {}

        for line in text.split('\n'):
            for item in [w.lower() for w in line.split()]:
                m = re.match('^[,.("]?(?P<word>[a-z]+-?[a-z]{2,})[,.)"]?$', item)
                if m:
                    word = m.group('word')
                    if word not in words and not Word.objects.filter(word_text=word).exists():
                        words.update({
                            word: line
                        })

        context = {
            'words': words
        }

        return render(request, 'words/extract.html', context)


@login_required
def save(request):
    try:
        words = request.POST.getlist('words')
    except KeyError:
        return render(request, 'words/save.html')
    else:
        context = {
            'words': words
        }
        for word in words:
            Word.objects.create(word_text=word, add_date=timezone.now()).save()

        return render(request, 'words/save.html', context)
