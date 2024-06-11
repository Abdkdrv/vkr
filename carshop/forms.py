from django import forms
from django.conf import settings
from .models import Status, User, Car, Developer, CarModel, Color, Condition, Transmission, Fuel, User
from django.contrib.auth.hashers import make_password


class OrderForm(forms.Form):
    order_id = forms.IntegerField(widget=forms.HiddenInput())
    delivery_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    pickup_location = forms.CharField(max_length=200)
    status = forms.ModelChoiceField(queryset=Status.objects.all())


class UserForm(forms.ModelForm):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'Имя пользователя',
            'email': 'Электронная почта',
            'phone_number': 'Номер телефона',
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CarForm(forms.ModelForm):

    class Meta:
        model = Car
        fields = ['dev_id', 'model_id', 'year', 'color_id', 'kilometers', 'condition_id', 'price', 'transmission_id', 'fuel_id', 'engine_capacity', 'desc', 'image']
        labels = {
            'dev_id': 'Марка',
            'model_id': 'Модель',
            'year': 'Год выпуска',
            'color_id': 'Цвет',
            'kilometers': 'Пробег',
            'condition_id': 'Состояние',
            'price': 'Стоимость',
            'transmission_id': 'Привод',
            'fuel_id': 'Тип топлива',
            'engine_capacity': 'Объем двигателя',
            'desc': 'Описание',
            'image': 'Изображение',
        }

        dev_id = forms.ModelChoiceField(queryset=Developer.objects.all(), label="Марка")
        model_id = forms.ModelChoiceField(queryset=CarModel.objects.none(), label="Модель")
        color_id = forms.ModelChoiceField(queryset=Color.objects.all(), label="Цвет")
        condition_id = forms.ModelChoiceField(queryset=Condition.objects.all(), label="Состояние")
        transmission_id = forms.ModelChoiceField(queryset=Transmission.objects.all(), label="Привод")
        fuel_id = forms.ModelChoiceField(queryset=Fuel.objects.all(), label="Тип топлива")