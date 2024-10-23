from django.http import HttpResponse
from django.shortcuts import render, redirect
from app1 import models
from app1.util.form import SupplierModelForm
from app1.util.pagination import Pagination


def supplier_list(request):
    data_dict = {}
    search_value = request.GET.get('q', '')  # 得到搜索值
    if search_value:
        data_dict = {"name__contains": search_value}  # 字段__contains包含.....
    queryset = models.Supplier.objects.filter(**data_dict).order_by("id")  # **为字典-字段顺序排列
    page_object = Pagination(request, queryset)
    context = {
        'active': 'supplier_list',  # 侧边栏状态
        'search_value': search_value,  # 搜索值
        'queryset': page_object.page_queryset,
        'page_string': page_object.html()
    }
    return render(request, 'supplier_list.html', context)


def supplier_add(request):
    if request.method == 'GET':
        form = SupplierModelForm
        context = {
            'form': form,
            'active': 'supplier_add',  # 侧边栏状态
            'title': '添加供货商'
        }
        return render(request, 'public_add.html', context)

    form = SupplierModelForm(data=request.POST)  # 用户post提交的数据，数据校验
    name = request.POST.get('name')
    if models.Supplier.objects.filter(name=name).exists():
        context = {
            'form': form,
            'active': 'supplier_add',  # 侧边栏状态
            'title': '添加供货商',
            'title3': '供货商重名，添加失败！'
        }
        return render(request, 'public_add.html', context)
    else:
        if form.is_valid():  # 如果数据合法，保存
            form.save()
            return redirect('/supplier_list/')
        context = {
            'form': form,
            'active': 'supplier_add',  # 侧边栏状态
            'title': '添加供货商'
        }
        return render(request, 'public_add.html', context)


def supplier_edit(request, nid):
    row_object = models.Supplier.objects.filter(id=nid).first()  # 保证修改范围
    if not row_object:
        return HttpResponse("警告，数据不存在！")
    if request.method == "GET":
        form = SupplierModelForm(instance=row_object)  # 这将更新row_object在数据库中的记录，而不是创建一个新的记录
        context = {
            'form': form,
            'title': '编辑供货商'
        }
        return render(request, 'public_add.html', context)
    form = SupplierModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/supplier_list/')
    context = {
        'form': form,
    }
    return render(request, 'public_add.html', context)


def supplier_delete(request, nid):
    # 判断能否删除
    if models.Drug.objects.filter(supplier=nid).exists():  # 药品存在？
        from django.contrib import messages
        messages.success(request, '警告，此供应商有对应记录，无法删除，如想删除，请删除对应库存记录')
        return redirect('/supplier_list/')
    else:
        models.Supplier.objects.filter(id=nid).delete()
    return redirect('/supplier_list/')
