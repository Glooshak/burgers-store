from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.utils import timezone


class Restaurant(models.Model):

    class RestaurantQuerySet(models.QuerySet):

        def get_restaurants_with_items(self):
            return self.prefetch_related(
                models.Prefetch(
                    'menu_items',
                    queryset=RestaurantMenuItem.objects.select_related('product')
                )
            ).filter(menu_items__availability=True).distinct()

    objects = RestaurantQuerySet.as_manager()

    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):

    class OrderQuerySet(models.QuerySet):

        def obtain_whole_price(self):

            not_finished_orders = self.exclude(status=Order.StatusChoice.FINISHED).prefetch_related(
                models.Prefetch(
                    'order', queryset=ProductOrder.objects.prefetch_related('product')
            )).annotate(
                order_price=models.Sum(models.F('order__product__price') * models.F('order__quantity'))
            )

            restaurants = Restaurant.objects.get_restaurants_with_items()
            orders = not_finished_orders.select_related('performer')

            for order in orders:
                if order.performer:
                    continue
                products_in_order = order.order
                product_pks = {product.product.pk for product in products_in_order.all()}
                order.performers = []
                for restaurant in restaurants:
                    restaurant_menu = restaurant.menu_items.all()
                    available_product_pks = {rm.product.pk for rm in restaurant_menu}
                    if product_pks.issubset(available_product_pks):
                        order.performers.append(restaurant)

            return orders

    class StatusChoice(models.TextChoices):
        GOTTEN = 'GT', 'Заказ принят в обработку'
        PACKING = 'PA', 'На сборе'
        DELIVERTING = 'DE', 'Отдано курьеру'
        FINISHED = 'FI', 'Заказ доставлен и закончен'

    class PayMethodChoice(models.TextChoices):
        IN_CASH = 'IC', 'Наличными'
        WITH_CREDIT_CARD = 'WC', 'Карточкой'

    custome_manager = OrderQuerySet.as_manager()

    performer = models.ForeignKey(
        Restaurant,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Ресторан(ы)',
        related_name='orders',
    )
    pay_method = models.CharField(
        max_length=2,
        choices=PayMethodChoice.choices,
        default=PayMethodChoice.IN_CASH,
        db_index=True,
    )
    comment = models.TextField(
        blank=True,
    )
    status = models.CharField(
        max_length=2,
        choices=StatusChoice.choices,
        default=StatusChoice.GOTTEN,
        db_index=True,
    )
    first_name = models.CharField(
        max_length=64,
    )
    second_name = models.CharField(
        max_length=64,
    )
    phone_number_regex = RegexValidator(
        regex='^\+?1?\d{8,15}$',
    )
    phone_number = models.CharField(
        validators=[phone_number_regex,],
        max_length=16,
    )
    address = models.CharField(
        max_length=256,
    )
    registrated_at = models.DateField(
        verbose_name='Registrated at',
        db_index=True,
        default=timezone.now,
    )
    called_at = models.DateField(
        verbose_name='Called at',
        db_index=True,
        blank=True,
        null=True,
    )
    delivered_at = models.DateField(
        verbose_name='Delivered at',
        db_index=True,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f'{self.first_name} {self.second_name}'


class ProductOrder(models.Model):
    product = models.ForeignKey(
        'Product',
        related_name='product',
        on_delete=models.CASCADE,
    )
    order = models.ForeignKey(
        'Order',
        related_name='order',
        on_delete=models.CASCADE,
    )
    quantity = models.PositiveIntegerField(

    )
    price = models.DecimalField(
        'Фиксированная цена продукта',
        max_digits=99,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
    )

    def __str__(self):
        return f'{self.product.name} {self.quantity}'
