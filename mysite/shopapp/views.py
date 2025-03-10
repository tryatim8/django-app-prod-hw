"""
В этом модуле лежат различные наборы представлений.

Разные view для интернет-магазина: по товарам, заказам и так далее.
"""
import logging
from timeit import default_timer

from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import (
    HttpResponse,
    HttpRequest,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.contrib.syndication.views import Feed
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer


logger = logging.getLogger(__name__)


class UserOrdersExportView(LoginRequiredMixin, View):

    def get(self, request: HttpRequest, user_id) -> JsonResponse:
        cache_key = f'user_orders_{user_id}'
        serialized_data = cache.get(cache_key)

        if serialized_data is None:
            logger.info('Cache miss, set data in the cache!')
            self.owner = get_object_or_404(User, pk=self.kwargs['user_id'])
            orders = (Order.objects.filter(user=self.owner)
                      .prefetch_related('products')
                      .select_related('user')
                      .order_by('-created_at'))
            serialized_data = OrderSerializer(orders, many=True).data
            cache.set(cache_key, serialized_data, 300)

        logger.info('Cache hits, get data from cache.')
        return JsonResponse(serialized_data, safe=False)


class UserOrdersListView(LoginRequiredMixin, ListView):
    model = Order
    template_name_suffix = '_of_user_list'

    def dispatch(self, request, *args, **kwargs):
        self.owner = get_object_or_404(User, pk=self.kwargs['user_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return (Order.objects.filter(user=self.owner)
                .prefetch_related('products')
                .only('pk', 'promocode', 'delivery_address', 'products__name'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner'] = self.owner
        return context


class LatestProductFeed(Feed):
    title = 'Shop latest products'
    description = 'Updates on changes and additions shop products'
    link = reverse_lazy('shopapp:products_list')

    def items(self):
        return Product.objects.order_by('-created_at')[:5]

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description[:150] if item.description else 'None'

    # def item_link(self, item: Product):
    #     return item.get_absolute_url()


class ShopIndexView(View):
    """Представление стартовой страницы приложения."""

    def get(self, request: HttpRequest) -> HttpResponse:
        """Рендер стартовой html-страницы `shop-index.html`."""
        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999),
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
        }
        logger.info('Hello example info message <3 !')
        return render(request, 'shopapp/shop-index.html', context=context)


class ProductDetailsView(DetailView):
    """Представление для возвращения деталей товара."""

    template_name = "shopapp/products-details.html"
    model = Product
    context_object_name = "product"


class ProductsListView(ListView):
    """Представление для возвращения списка товаров."""

    template_name = "shopapp/products-list.html"
    # model = Product
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(CreateView):
    """Представление для создания товара."""

    model = Product
    fields = "name", "price", "description", "discount"
    success_url = reverse_lazy("shopapp:products_list")


class ProductUpdateView(UpdateView):
    """Представление для изменения товара с заданным pk."""

    model = Product
    fields = "name", "price", "description", "discount"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        """Редирект в случае удачного запроса страницу товара."""
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk},
        )


class ProductDeleteView(DeleteView):
    """Представление для безопасного удаления товара по pk."""

    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        """Метод не удаляет, а помещает товар в архив."""
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class OrdersListView(LoginRequiredMixin, ListView):
    """Представление для возвращения списка заказов."""

    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )


class OrderDetailView(PermissionRequiredMixin, DetailView):
    """Представление для возвращения деталей заказа по pk."""

    permission_required = "shopapp.view_order"
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )


class ProductsDataExportView(View):
    """Представление для возвращения списка товаров."""

    def get(self, request: HttpRequest) -> JsonResponse:
        """Гет-запрос списка товаров в формате JSON."""
        products = Product.objects.order_by("pk").all()
        products_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": product.price,
                "archived": product.archived,
            }
            for product in products
        ]
        return JsonResponse({"products": products_data})


class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над товарами.

    Полный CRUD для объектов Product: методы GET, POST, PUT, PATCH, DELETE.
    """

    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['pk', 'name', 'price', 'discount']


class OrderViewSet(ModelViewSet):
    """
    Набор представлений для действий над заказами.

    Полный CRUD для объектов Order: методы GET, POST, PUT, PATCH, DELETE.
    """

    serializer_class = OrderSerializer
    queryset = Order.objects.prefetch_related('products').all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['pk', 'delivery_address', 'created_at']
    filterset_fields = ['delivery_address', 'promocode', 'user']
