from django.http import HttpResponse
from django.shortcuts import render, redirect
from app1 import models
from app1.util.form import AdminModelForm, AdminEditModelForm, AdminResetModelForm
from app1.util.pagination import Pagination


def admin_list(request):
    data_dict = {}
    search_value = request.GET.get('q', '')  # 得到搜索值
    if search_value:
        data_dict = {"username__contains": search_value}  # 字段__contains包含.....
    queryset = models.Admin.objects.filter(**data_dict).order_by("id")  # **为字典-字段顺序排列
    page_object = Pagination(request, queryset)
    context = {
        'queryset': page_object.page_queryset,
        'active': 'admin_list',  # 侧边栏状态
        'search_value': search_value,  # 搜索值
        'page_string': page_object.html(),
    }
    return render(request, 'admin_list.html', context)


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
    username = request.POST.get('username')
    if models.Admin.objects.filter(username=username).exists():
        context = {
            'form': form,
            'active': 'admin_add',  # 侧边栏状态
            'title': '添加管理员',
            'title3': '名称已存在，添加失败！'
        }
        return render(request, 'public_add.html', context)
    else:
        if form.is_valid():  # 如果数据合法，保存
            form.save()
            return redirect('/admin_list/')
        context = {
            'form': form,
            'active': 'admin_add',  # 侧边栏状态
            'title': '添加管理员'
        }
        return render(request, 'public_add.html', context)


def admin_edit(request, nid):
    row_object = models.Admin.objects.filter(id=nid).first()  # 保证修改范围
    if not row_object:
        return HttpResponse("警告，数据不存在！")
    if request.method == "GET":
        form = AdminEditModelForm(instance=row_object)  # 这将更新row_object在数据库中的记录，而不是创建一个新的记录
        # 现在，form的初始值将是row_object的字段值
        # 将这个form渲染到模板中，以便用户可以编辑row_object的字段
        context = {
            'form': form,
            'title': '编辑用户名'
        }
        return render(request, 'public_add.html', context)
    form = AdminEditModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/admin_list/')
    context = {
        'form': form,
    }
    return render(request, 'public_add.html', context)


def admin_delete(request, nid):
    models.Admin.objects.filter(id=nid).delete()
    return redirect('/admin_list/')


def admin_reset(request, nid):
    row_object = models.Admin.objects.filter(id=nid).first()  # 保证修改范围
    title = "重置密码 - {}".format(row_object.username)  # 显示用户名
    if not row_object:
        return HttpResponse("警告，数据不存在！")
    if request.method == "GET":
        form = AdminResetModelForm()
        context = {
            'form': form,
            'title': title
        }
        return render(request, 'public_add.html', context)
    form = AdminResetModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/admin_list/')
    return render(request, 'public_add.html', {"form": form})
