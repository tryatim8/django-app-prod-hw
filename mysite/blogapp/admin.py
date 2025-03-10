from django.contrib import admin

from blogapp.models import Article, Author, Category, Tag


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['pk', 'title', 'pub_date', 'content_short']
    list_display_links = ['pk', 'title']

    @classmethod
    def content_short(cls, obj: Article):
        return obj.content if len(obj.content) < 50 else obj.content[:48] + '...'


class AuthorInLine(admin.TabularInline):
    model = Author


class CategoryInLine(admin.TabularInline):
    model = Category


class TagInLine(admin.StackedInline):
    model = Article.tags.through

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name']
    list_display_links = ['pk', 'name']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name']
    list_display_links = ['pk', 'name']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name']
    list_display_links = ['pk', 'name']
