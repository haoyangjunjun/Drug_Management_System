from django.http import HttpResponse
from django.shortcuts import render, redirect
from io import BytesIO  # 内存
from app1 import models
from app1.util.code import check_code
from app1.util.form import LoginForm, AdminModelForm


def login(request):
    if request.method == "GET":
        form = LoginForm()
        return render(request, 'login.html', {"form": form})
    form = LoginForm(data=request.POST)
    if form.is_valid():
        # print(form.cleaned_data)  # 验证成功，获取到用户名密码
        # 获取用户对象 方法之一   admin_object = models.Admin.objects.filter(username=form.cleaned_data['username'], password=form.cleaned_data['password']).first()
        # 去除code，的数据库校验
        user_input_code = form.cleaned_data.pop('code')
        code = request.session.get('image_code', '')
        if code.upper() != user_input_code.upper():
            form.add_error("code", "验证码错误或超时")
            return render(request, 'login.html', {'form': form})
        admin_object = models.Admin.objects.filter(**form.cleaned_data).first()
        if not admin_object:
            form.add_error("password", "用户名或密码错误")
            return render(request, 'login.html', {"form": form})
        # 验证完成
        # 生成字符串，写到cookie、session中
        request.session["info"] = {'id': admin_object.id, 'name': admin_object.username}
        request.session.set_expiry(60 * 60 * 24)  # 登录信息只保存24小时

        # return HttpResponse("ok")
        return redirect('/drug_list/')
    return render(request, 'login.html', {"form": form})


def admin_add(request):
    if request.method == 'GET':
        form = AdminModelForm
        context = {
            'form': form,
            'active': 'admin_add',  # 侧边栏状态
            'title': '添加管理员'
        }
        return render(request, 'public_add.html', context)

    form = AdminModelForm(data=request.POST)  # 用户post提交的数据，数据校验
    if form.is_valid():  # 如果数据合法，保存
        form.save()
        from django.contrib import messages
        messages.success(request, '提示：注册成功，请登录')
        return redirect('/login/')
    context = {
        'form': form,
        'active': 'admin_add',  # 侧边栏状态
        'title': '添加管理员'
    }
    print(form)
    return render(request, 'public_add.html', context)


def image_code(request):
    img, code_string = check_code()
    request.session['image_code'] = code_string  # 验证码写入session
    request.session.set_expiry(60)  # 60秒倒计时删除验证码
    stream = BytesIO()
    img.save(stream, 'png')
    return HttpResponse(stream.getvalue())


def logout(request):
    request.session.clear()
    return redirect("/login/")
