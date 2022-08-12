from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

"""
Разнести ли характеристики компьютеры тоже на категории или написать все в один класс, но тогда как в шаблоне страницы выводить свои
заголовки в характеристиках для каждой категории. 
"""


class Category(models.Model):
    category_name = models.CharField(max_length=30)
    sub_categories = models.ManyToManyField("self", blank=True)
    is_sub_category = models.BooleanField(default=False)
    parent = models.IntegerField()



    def __str__(self):
        return self.category_name


class SubCategory(models.Model):
    name = models.TextField(max_length=50)
    categories = models.ManyToManyField(Category)

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)  # "штрих код"
    price = models.DecimalField(max_digits=12,
                                decimal_places=0)  # decimal_places знаки после запятой
    creation_date = models.DateTimeField(auto_now_add=True)  # auto now сдесь время создания записи в базе данных
    last_update_time = models.DateTimeField(auto_now=True)  # auto now сдесь время последнего обновления
    image1 = models.ImageField(blank=True)
    mark = models.CharField(max_length=50, blank=True)
    available = models.BooleanField(default=True)  # доступность товара в магазине True or False
    sub_category = models.ManyToManyField(SubCategory)
    global_rating = models.DecimalField(max_digits=65, decimal_places=1, default=0)

    def __str__(self):
        return self.title


# class ScreenCharacteristic(models.Model):
#     Diagonal_inches = models.IntegerField
#

class GPU_Characteristic(models.Model):
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    width = models.CharField(max_length=50)
    height = models.CharField(max_length=50)
    gpu_memory = models.CharField(max_length=50)
    TDP = models.IntegerField()


class LaptopCharacteristic(models.Model):
    guarantee_mounth = models.CharField(max_length=20)
    model = models.CharField(max_length=50)  # конкретная модель компьютера
    operational_system = models.CharField(max_length=30)
    cpu = models.CharField(max_length=50)
    gpu = models.ForeignKey(GPU_Characteristic, on_delete=models.CASCADE)
    batery = models.CharField(max_length=50)
    screen_diagonal = models.DecimalField(max_digits=5, decimal_places=1)
    product_connected = models.ManyToManyField(Product)


class Photo(models.Model):
    product_connected = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(blank=True, upload_to="images")

    def __str__(self):
        return str(self.product_connected)


class Review(models.Model):
    review = models.TextField(max_length=500)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    product_connected = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update_time = models.DateTimeField(auto_now=True)
    rating = models.DecimalField(max_digits=5, decimal_places=0)

    def __str__(self):
        return f"{self.product_connected}"  # , self.author


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MaxValueValidator(999)], default=1)
    status = models.CharField(max_length=100)

    def __str__(self):
        return str(self.user)
