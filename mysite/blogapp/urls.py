from django.urls import path
from django.http import HttpResponse

from blogapp.views import ArticleListView

app_name = 'blogapp'

urlpatterns = [
    path('', view=lambda x: HttpResponse('Hello world!'), name='homepage'),
    path('articles/', ArticleListView.as_view(), name='articles')
]
