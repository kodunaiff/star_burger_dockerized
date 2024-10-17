from django.utils import timezone

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Count, F, Sum
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
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


class OrderQuerySet(models.QuerySet):
    def calculate_order(self):
        return self.annotate(
            total=Sum(F('orders__quantity') * F('orders__product__price'))
        )

    def ordered_by_status_and_id(self):
        return self.annotate(
            status_order=models.Case(
                models.When(status="new", then=1),
                models.When(status="confirmed", then=2),
                models.When(status="packed", then=3),
                models.When(status="delivered", then=4)
            )
        ).order_by("status_order", "id")


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('confirmed', 'Подтвержден'),
        ('packed', 'Собран'),
        ('delivered', 'Доставлен'),
    ]
    PAYMENT_CHOICES = [
        ('cash', 'Наличный'),
        ('card', 'Безналичный'),
        ('unknown', 'Неизвестно'),
    ]

    firstname = models.CharField(
        'Имя',
        max_length=50
    )
    lastname = models.CharField(
        'Фамилия',
        max_length=70
    )
    phonenumber = PhoneNumberField(
        'Номер клиента',
        max_length=20
    )
    address = models.TextField(
        'Адрес доставки',
        help_text='Город, улица, дом'
    )
    status = models.CharField(
        verbose_name="статус заказа",
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        db_index=True,
    )
    comment = models.TextField(
        verbose_name='комментарий',
        blank=True,
    )
    created_at = models.DateTimeField(
        verbose_name='время создания',
        default=timezone.now,
        db_index=True,
    )
    called_at = models.DateTimeField(
        verbose_name='время созвона',
        blank=True,
        null=True,
        db_index=True,
    )
    delivered_at = models.DateTimeField(
        verbose_name='время доставки',
        blank=True,
        null=True,
        db_index=True,
    )
    payment = models.CharField(
        verbose_name='способ оплаты',
        max_length=20,
        choices=PAYMENT_CHOICES,
        default='unknown',
        db_index=True,
    )
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        verbose_name="готовит",
        related_name="r_orders",
        null=True,
        blank=True,
    )
    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'# {self.id} {self.firstname} {self.lastname}'


class OrderElements(models.Model):
    order = models.ForeignKey(
        'Order', verbose_name='Заказ',
        on_delete=models.CASCADE, related_name='orders'
    )
    product = models.ForeignKey(
        'Product', verbose_name='Товар',
        on_delete=models.CASCADE, related_name='items'
    )
    quantity = models.IntegerField(
        verbose_name='количество',
        validators=[MinValueValidator(1),
                    MaxValueValidator(100)]
    )
    position_cost = models.DecimalField(
        verbose_name='стоимость позиции',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        ordering = ['order']
        verbose_name = 'элементы заказа'
        verbose_name_plural = 'элементы заказа'

    def __str__(self):
        return f"{self.order} - {self.product}"
