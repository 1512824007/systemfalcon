#coding:utf8
from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'用户名'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'密码'}))


class registerForm(forms.Form):
    username = forms.CharField(max_length=255,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户账号'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'}))
    password2 = forms.CharField(label='Confirm',
                                widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请再次输入密码'}))
    email = forms.EmailField(max_length=255,
                             widget=forms.EmailInput(attrs={'class':'form-control','placeholder': '请输入邮箱地址'}))

    phone = forms.CharField(max_length=255,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入手机号'}))
    code = forms.CharField(max_length=255,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入验证码'}))
    real_name = forms.CharField(max_length=255,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名(真实姓名)'}))
    #company = forms.CharField(max_length=255,
    #                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '公司'}))
    #department = forms.CharField(max_length=255,
    #                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '部门'}))
    #position = forms.CharField(max_length=255,
    #                          widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '职位'}))


class ForgetPwdForm(forms.Form):
    email = forms.EmailField(required=True)


class ModifyPwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=6)
    password2 = forms.CharField(required=True, min_length=6)
