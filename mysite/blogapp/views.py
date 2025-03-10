from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from blogapp.models import Article


class ArticleListView(LoginRequiredMixin, ListView):
    queryset = (Article.objects
                .select_related('author')
                .select_related('category')
                .prefetch_related('tags')
                .defer('updated_at', 'content'))
    context_object_name = 'articles'
