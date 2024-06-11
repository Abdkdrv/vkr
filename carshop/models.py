from django.conf import settings
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='bookstore_users',  # Change related_name to avoid conflict
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='bookstore_users_permissions',  # Change related_name to avoid conflict
        blank=True,
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username


class Developer(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class CarModel(models.Model):
    name = models.CharField(max_length=100)
    dev_id = models.ForeignKey(Developer, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Condition(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Transmission(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Fuel(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Car(models.Model):
    dev_id = models.ForeignKey(Developer, on_delete=models.CASCADE)
    model_id = models.ForeignKey(CarModel, on_delete=models.CASCADE)
    year = models.IntegerField()
    color_id = models.ForeignKey(Color, on_delete=models.CASCADE)
    kilometers = models.IntegerField()
    condition_id = models.ForeignKey(Condition, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    transmission_id = models.ForeignKey(Transmission, on_delete=models.CASCADE)
    fuel_id = models.ForeignKey(Fuel, on_delete=models.CASCADE)
    engine_capacity = models.FloatField()
    desc = models.TextField()
    image = models.ImageField(upload_to='media/images')

    def __str__(self):
        return f"{self.dev_id.name} {self.model_id.name} ({self.year})"


class Status(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Order(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    car_id = models.ForeignKey(Car, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    date_ordered = models.DateTimeField(auto_now_add=True)
    pickup_location = models.CharField(max_length=200)
    delivery_status = models.CharField(max_length=100)
    delivery_date = models.DateField(blank=True, null=True)
    delivery_time = models.TimeField(blank=True, null=True)
    payment_status = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)

    def __str__(self):
        return f"Order #{self.pk} by {self.user.username}"


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.car.model_id.name}"


class CartOrder(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    car_id = models.ForeignKey(Car, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CartOrder for {self.cart.user.username}"