import csv
import io

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.urls import path
from django.shortcuts import render, redirect

from .forms import ImportCSVForm
from .models import Product, Order
from .admin_mixins import ExportAsCSVMixin


class OrderInline(admin.TabularInline):
    model = Product.orders.through


@admin.action(description="Archive products")
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.action(description="Unarchive products")
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    actions = [
        mark_archived,
        mark_unarchived,
        "export_csv",
    ]
    inlines = [
        OrderInline,
    ]
    # list_display = "pk", "name", "description", "price", "discount"
    list_display = "pk", "name", "description_short", "price", "discount", "archived"
    list_display_links = "pk", "name"
    ordering = "-name", "pk"
    search_fields = "name", "description"
    fieldsets = [
        (None, {
           "fields": ("name", "description"),
        }),
        ("Price options", {
            "fields": ("price", "discount"),
            "classes": ("wide", "collapse"),
        }),
        ("Extra options", {
            "fields": ("archived",),
            "classes": ("collapse",),
            "description": "Extra options. Field 'archived' is for soft delete",
        })
    ]

    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + "..."


# admin.site.register(Product, ProductAdmin)


# class ProductInline(admin.TabularInline):
class ProductInline(admin.StackedInline):
    model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        ProductInline,
    ]
    list_display = "delivery_address", "promocode", "created_at", "user_verbose"
    change_list_template = 'shopapp/orders_changelist.html'

    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username
    
    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path('import_orders_csv/', self.import_csv_file, name='import_orders_csv'),
        ]
        return new_urls + urls

    def import_csv_file(self, request: HttpRequest) -> HttpResponse:
        if request.method == 'GET':
            form = ImportCSVForm()
            context = {'form': form}
            return render(request, 'admin/csv_form.html', context=context)
        form = ImportCSVForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {'form': form}
            return render(request, 'admin/csv_form.html',
                          context=context, status=400)
        self.save_csv_orders(
            form.files['csv_file'].file,
            encoding=request.encoding,
        )
        self.message_user(request, 'Orders imported from CSV-file successfully')
        return redirect('..')

    def save_csv_orders(self, file, encoding):
        csv_file = io.TextIOWrapper(file, encoding)
        reader = csv.DictReader(csv_file)
        with transaction.atomic():
            for row in reader:
                order = Order(
                    delivery_address=row.get('delivery_address'),
                    promocode=row.get('promocode'),
                    user=User.objects.get(pk=int(row.get('user')))
                )
                order.save()
                products = Product.objects.filter(
                    pk__in=list(map(int, row.get('products').split(',')))
                )
                order.products.add(*products)
