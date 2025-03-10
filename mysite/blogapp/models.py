from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, default='')

    def __str__(self):
        return f'Author (pk={self.pk} name={self.name})'


class Category(models.Model):
    name = models.CharField(max_length=40, unique=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f'Category (pk={self.pk} name={self.name})'


class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f'Tag (pk={self.pk} name={self.name})'


class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    pub_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(Author, on_delete=models.PROTECT,
                               related_name='articles_by_author')
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL,
                                 related_name='articles_in_category')
    tags = models.ManyToManyField(Tag, related_name='articles_with_tag')

    def __str__(self):
        return f'Article (pk={self.pk} name={self.title})'
