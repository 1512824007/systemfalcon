#coding:utf8
from django.shortcuts import render
from django.contrib import auth

from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required

from userperm.views import UserIP
from userperm.models import Message
from models import Profile

from openfalcon.models import Roominfo

from .form import registerForm, ForgetPwdForm, ModifyPwdForm
from django.contrib.auth.models import User, Group


from itsdangerous import URLSafeTimedSerializer as utsr
import base64
from django.conf import settings as django_settings
from django.views.generic import View
from django.core.mail import send_mail
import string, random
from django.contrib.auth.hashers import make_password
from userauth.in_module import in_module

class Token:
    def __init__(self, security_key):
        self.security_key = security_key
        self.salt = base64.encodestring(security_key)

    def generate_validate_token(self, username):
        serializer = utsr(self.security_key)
        return serializer.dumps(username, self.salt)

    def confirm_validate_token(self, token, expiration=3600):
        serializer = utsr(self.security_key)
        return serializer.loads(token, salt=self.salt, max_age=expiration)

    def remove_validate_token(self, token):
        serializer = utsr(self.security_key)
        return serializer.loads(token, salt=self.salt)
token_confirm = Token(django_settings.SECRET_KEY)


def register(request,):
    up_reg = registerForm()
    group = Group.objects.all()
    if request.method=="POST":
        name = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']
        phone = request.POST['phone']
        email = request.POST['email']
        real_name = request.POST['real_name']
        code = request.POST['code']
        role = request.POST['role']
        department = request.POST['department']
        try:
            auth_user = User.objects.get(username=name.split('"')[1]).is_active
        except Exception as user_e:
            #print("user {0}".format(user_e))
            auth_user = False
        try:
            auth_email = User.objects.get(email=email.split('"')[1]).is_active
        except Exception as email_e:
            #print("email {0}".format(email_e))
            auth_email = False

        if auth_user:
            return HttpResponse(u'用户已存在, 请核对信息重新注册')
        elif auth_email:
            return HttpResponse(u'邮箱已存在, 请核对信息重新注册')
        else:
            origin_code = request.session['captcha']
            if code == origin_code:
                if password == password2:
                    user = User.objects.create_user(username=name.split('"')[1], password=password,
                                                    email=email.split('"')[1])
                    try:
                        user.is_active = True
                        #token = token_confirm.generate_validate_token(name)
                        #url_en = '/'.join([django_settings.DOMAIN, 'activate', token])
                        user.groups.add(department)
                        Profile.objects.filter(user__username=name.split('"')[1]).update(is_director=role,phone=str(phone.split('"')[1]),realName=str(real_name.split('"')[1]))
                        user.save()
                        return HttpResponse(u"0")
                    except Exception as e:
                        user.delete()
                        print e
                        return HttpResponse(e)
                else:
                    return HttpResponse(u'密码不一致,请重新输入')
            else:
                return HttpResponse(u'验证码错误,请重新输入')
    return render(request, 'registration/register.html', locals())


def active_user(request, token):
    try:
        username = token_confirm.confirm_validate_token(token)
    except:
        username = token_confirm.remove_validate_token(token)
        users = User.objects.filter(username=username)
        for user in users:
            user.delete()
        return HttpResponse(u'对不起，验证链接已过期，请重新注册')
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return HttpResponse(u"对不起，您所验证的用户不存在，请重新注册")
    user.is_active = True
    user.save()
    message = u'验证成功，请进行回返回进行登录操作'
    return HttpResponse(message)


def login(request):
    if request.method == "POST":
        if request.POST.has_key('login'):
            username = request.POST['username']
            password = request.POST['password']
            #username = up.cleaned_data['username']
            #password = up.cleaned_data['password']
            user = auth.authenticate(username=username,password=password)
            if user and user.is_active:
                auth.login(request, user)
                Message.objects.create(type='user_login', user=request.user, action='user_Login', action_ip=UserIP(request),content=u'user_login {0}'.format(request.user))
                return HttpResponseRedirect('/')
    else:
        return render(request, 'registration/login.html', locals())
    return render(request, 'registration/login.html', locals())


@login_required
def logout(request):
    Message.objects.create(type='logout', user=request.user, action=u'logout', action_ip=UserIP(request),content='user_logout {0}'.format(request.user))
    auth.logout(request)
    return HttpResponseRedirect('/')


def captcha(request):
    email = request.GET['email']
    #if ('@gw500.com' not in email) and ('@gosun.com' not in email):
    #    return HttpResponse(u'您的邮箱不是高升公司邮箱')
    #else:
    rand_str = ''.join(random.sample(string.letters + string.digits, 4))
    request.session['captcha'] = rand_str
    #from .tasks import send_register_email
    try:
        print(rand_str)
        #send_register_email.delay([str(email)],rand_str=rand_str)
        #send_mail(u'gosun监控系统', u'\n\n注册验证码:' + rand_str, 'sys@gosun.com', [str(email)])
        return HttpResponse(u'请到邮箱读取验证码')
    except Exception as e:
        return HttpResponse(e)


class ForgetPwdView(View):
    def get(self, request):
        forget_form = ForgetPwdForm()
        return render(request, "registration/forgetpwd.html", {"forget_form": forget_form})

    def post(self, request):
        forget_form = ForgetPwdForm(request.POST)
        rand_str = ''.join(random.sample(string.letters + string.digits, 4))
        request.session['captcha'] = rand_str.lower()
        if forget_form.is_valid():
            emai = request.POST.get("email", "")
            try:
                email = User.objects.get(email=emai).email
                return HttpResponseRedirect("/modify_pwd/?email="+email)
            except Exception as e:
                return render(request, "registration/forgetpwd.html", {"forget_form": forget_form, 'msg': u'邮箱未注册'})
        else:
            return render(request, "registration/forgetpwd.html", {"forget_form": forget_form})


class ModifyPwdView(View):
    def get(self, request):
        modify_form = ModifyPwdForm()
        email = request.GET.get('email')
        session_cap = request.session['captcha']
        try:
            send_mail(u'gosun监控平台密码变更', u'\n\n\n验证码:' + session_cap, 'sys@gosun.com', [email])
        except Exception as e:
            return HttpResponse(e)
        return render(request, "registration/password_reset.html", locals())
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            email = request.POST.get("email", "")
            cap = request.POST.get("captcha", "")
            session_cap = request.session['captcha']
            if pwd1 != pwd2:
                return render(request, "registration/password_reset.html", {"email": email, "msg": u"密码不一致"})
            else:
                if cap == session_cap:
                    user = User.objects.get(email=email)
                    user.password = make_password(pwd1)
                    user.save()
                    return HttpResponseRedirect("/accounts/login/")
                else:
                    forget_form = ForgetPwdForm(request.POST)
                    return render(request, "registration/forgetpwd.html", {"forget_form": forget_form, 'msg': u'验证码错误，请重新输入'})
        else:
            #email = request.POST.get("email", "")
            return HttpResponse(u'密码至少6位，或者其他字段不符合要求')
            #return render(request, "registration/password_reset.html", {"email": email})
