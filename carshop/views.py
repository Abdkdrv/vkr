import time
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse, HttpResponseForbidden
from .forms import CarForm, UserForm, OrderForm
from .models import Car, Order, User, CarModel, Cart, CartItem, Status
from django.shortcuts import render, get_object_or_404


def home(request):
    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse('home'))
    else:
        form = CarForm()

    cars = Car.objects.all()
    return render(request, 'home.html', {'form': form, 'cars': cars})


def load_car_models(request):
    dev_id = request.GET.get('dev_id')
    car_models = CarModel.objects.filter(dev_id=dev_id).values('id', 'name')
    return JsonResponse(list(car_models), safe=False)


@login_required
def delete_car(request, id):
    if request.user.is_superuser:
        car = get_object_or_404(Car, id=id)
        car.delete()
        return redirect('catalog')
    else:
        return HttpResponseForbidden("У вас нет прав для удаления этого объекта.")


@login_required
def cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)
    if request.method == 'POST':
        order = Order.objects.create(
            user_id=request.user,
            car_id=request.cartitem.car,
            status=Status.objects.get(id=1),
            pickup_location=request.POST.get('pickup_location', 'Default Location'),
            delivery_status='Pending',
            delivery_date=request.POST.get('delivery_date', '2023-12-31'),
            delivery_time=request.POST.get('delivery_time', '12:00:00'),
            payment_status='Pending',
            payment_method=request.POST.get('payment_method', 'Credit Card'),
        )
        for item in items:
            order.items.add(item)
        cart.items.clear()
        return redirect('order_success')
    return render(request, 'cart.html', {'cart': cart, 'items': items})


def add_to_cart(request, car_id):
    car = Car.objects.get(id=car_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, car=car)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)


@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)

    if request.method == 'POST':
        pickup_location = request.POST.get('pickup_location', 'Не указано')
        payment_method = request.POST.get('payment_method', 'Безналичная оплата')  # Default to "Безналичная оплата" if not provided

        for item in items:
            order = Order.objects.create(
                user_id=request.user,
                car_id=item.car,
                status=Status.objects.get(id=1),
                pickup_location=pickup_location,
                delivery_date=None,
                payment_status='Оплата произведена',
                payment_method=payment_method,
            )
            order.save()

        cart.items.all().delete()
        return redirect('order_success')

    return render(request, 'checkout.html', {'cart': cart, 'items': items})


@login_required
def add_to_cart(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, car=car)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('catalog')


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart')


@login_required
def all_orders(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("У вас нет прав для доступа к этой странице.")

    orders = Order.objects.all()

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order.objects.get(id=form.cleaned_data['order_id'])
            order.delivery_date = form.cleaned_data['delivery_date']
            order.pickup_location = form.cleaned_data['pickup_location']
            order.status = form.cleaned_data['status']
            order.save()
            return redirect('all_orders')
    else:
        form = OrderForm()

    return render(request, 'all_orders.html', {'orders': orders, 'form': form})


@login_required
def orders(request):
    orders = Order.objects.filter(user_id=request.user)
    return render(request, 'orders.html', {'orders': orders})


@login_required
def order_success(request):
    return render(request, 'order_success.html')


@login_required
def aboutus(request):
    return render(request, 'aboutus.html')


@login_required
def contacts(request):
    return render(request, 'contacts.html')


def catalog(request):
    cars = Car.objects.all()
    query = request.GET.get('q')
    if query:
        cars = Car.objects.filter(model__icontains=query)
    else:
        cars = Car.objects.all()
    return render(request, 'catalog.html', {'cars': cars})


def edit_car(request, car_id):
    car = get_object_or_404(Car, pk=car_id)

    if request.method == 'POST':
        form = CarForm(request.POST, request.FILES, instance=car)
        if form.is_valid():
            form.save()
            version = int(time.time())
            return redirect('catalog')
    else:
        form = CarForm(instance=car)

    version = int(time.time())
    return render(request, 'edit_car.html', {'form': form, 'version': version})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(reverse('home'))
        else:
            messages.error(request, 'Неправильный логин или пароль')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect(reverse('home'))


def register_view(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            return redirect(reverse('home'))
        else:
            messages.error(request, 'Ошибка при регистрации. Проверьте данные и попробуйте снова.')
    else:
        form = UserForm()
    return render(request, 'register.html', {'form': form})
