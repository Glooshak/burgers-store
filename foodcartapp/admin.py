from django.contrib import admin
from django.shortcuts import reverse, redirect
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Product, Order, ProductOrder
from .models import ProductCategory
from .models import Restaurant
from .models import RestaurantMenuItem
from star_burger.settings import ALLOWED_HOSTS


class ProductOrderInline(admin.TabularInline):
    model = ProductOrder


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'pk', 'first_name', 'address',
    ]

    def response_change(self, request, obj):

        if 'next' in request.GET and url_has_allowed_host_and_scheme(
            url := request.GET['next'], ALLOWED_HOSTS,
        ):
            return redirect(url)

        return super().response_change(request, obj)

    def save_formset(self, request, form, formset, change):
        product_order_set = formset.save(commit=False)
        for product_order in product_order_set:
            if not product_order.price:
                product_order.price = product_order.product.price
            product_order.save()
        formset.save_m2m()

    inlines = [
        ProductOrderInline,
    ]


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('??????????', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('????????????????', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return '???????????????? ????????????????'
        return format_html('<img src="{url}" style="max-height: 200px;"/>', url=obj.image.url)
    get_image_preview.short_description = '????????????'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return '?????? ????????????????'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html('<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', edit_url=edit_url, src=obj.image.url)
    get_image_list_preview.short_description = '????????????'


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass
