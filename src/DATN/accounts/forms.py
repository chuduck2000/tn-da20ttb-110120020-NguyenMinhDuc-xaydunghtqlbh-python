from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Account, UserProfile


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(
        attrs={"placeholder": "Nhập username vào đây"}))
    phone_number = forms.CharField(widget=forms.TextInput(
        attrs={"placeholder": "Nhập số điện thoại vào đây"}))
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Nhập Email vào đây"}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Nhập mật khẩu vào đây'}))
    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Nhập lại mật khẩu vào đây'}))

    class Meta:
        model = Account
        fields = ['username', 'phone_number', 'email', 'password']

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        password1 = cleaned_data.get('password1')

        if password != password1:
            raise forms.ValidationError(
                "Mật khẩu không hợp lệ"
            )

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Nhập họ và tên'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Nhập số điện thoại'
        self.fields['email'].widget.attrs['placeholder'] = 'Nhập địa chỉ Email'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('username', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages={'invalid': ("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ('address', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'