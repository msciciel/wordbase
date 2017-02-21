from django.conf.urls import url
from django.contrib.auth import views as auth_views


from . import views

app_name = 'words'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'(?P<word_id>\d+)/$', views.detail, name='detail'),
    url(r'^parse/$', views.parse, name='parse'),
    url(r'^extract/$', views.extract, name='extract'),
    url(r'^save/$', views.save, name='save'),
    url(r'login/', auth_views.login, name='login'),
    url(r'logout/', auth_views.logout, {'next_page': '/'}, name='logout'),
]
