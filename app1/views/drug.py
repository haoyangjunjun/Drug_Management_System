import requests
from django.http import HttpResponse
from django.shortcuts import render, redirect
from app1 import models
from app1.util.form import DrugModelForm, SaleModelForm, InModelForm
from app1.util.pagination import Pagination


def home(request):
    return redirect("/drug_list/")


# 药品库存---------------------------------------------------------------------
def drug_list(request):
    # queryset = models.Drug.objects.all()
    url1 = "https://api.shserve.cn/api/yiyan"
    response = requests.get(url1)
    if response.status_code == 200:
        data = response.text
    else:
        print("请求失败，状态码：", response.status_code)

    data_dict = {}
    search_value = request.GET.get('q', '')  # 得到搜索值
    if search_value:
        data_dict = {"name__contains": search_value}  # 字段__contains包含.....
    queryset = models.Drug.objects.filter(**data_dict).order_by("id")  # **为字典-字段顺序排列
    page_object = Pagination(request, queryset)
    context = {
        'search_value': search_value,  # 搜索值
        'queryset': page_object.page_queryset,
        'page_string': page_object.html(),
        'active': 'drug_list',  # 侧边栏状态
        'title': "出库记录",
        'data': data
    }
    return render(request, 'drug_list.html', context)


def drug_add(request):
    if request.method == 'GET':
        form = DrugModelForm
        context = {
            'form': form,
            'active': 'drug_add',  # 侧边栏状态
            'title': '添加药品',
            'title3': '在这里添加新的药品'
        }
        return render(request, 'drug_add.html', context)

    form = DrugModelForm(data=request.POST)  # 用户post提交的数据，数据校验
    drug_name = request.POST.get('name')
    if models.Drug.objects.filter(name=drug_name).exists():
        context = {
            'form': form,
            'active': 'drug_add',  # 侧边栏状态
            'title': '添加药品',
            'title3': '警告，此药品已经存在，添加失败'
        }
        return render(request, 'drug_add.html', context)  # 失败
    else:
        if form.is_valid():  # 如果数据合法，保存
            form.save()
            return redirect('/drug_list/')
        context = {
            'form': form,
            'active': 'drug_add',  # 侧边栏状态
            'title': '添加药品',
            'title3': '添加失败'
        }
        return render(request, 'drug_add.html', context)  # 失败


def drug_edit(request, nid):
    row_object = models.Drug.objects.filter(id=nid).first()  # 保证修改范围
    if not row_object:
        return HttpResponse("警告，数据不存在！")
    if request.method == "GET":
        form = DrugModelForm(instance=row_object)  # 这将更新row_object在数据库中的记录，而不是创建一个新的记录
        # 现在，form的初始值将是row_object的字段值
        # 将这个form渲染到模板中，以便用户可以编辑row_object的字段
        context = {
            'form': form,
            'title': '编辑药品库存',
            'title3': '注意，对价格进行修改将影响收支记录！'
        }
        return render(request, 'drug_add.html', context)
    form = DrugModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/drug_list/')
    context = {
        'form': form,
        'title': '编辑药品库存',
        'title2': '---------注意，对价格进行修改将影响收支记录！'
    }
    return render(request, 'drug_add.html', context)


def drug_delete(request, nid):
    # 判断能否删除
    search_value = models.Drug.objects.filter(id=nid).first()  # 得到药品名字
    if models.OutOrder.objects.filter(name=search_value).exists():  # 药品存在？
        from django.contrib import messages
        messages.success(request, '警告，此药品有出库记录，无法删除，如想删除，请删除对应库存记录')
        return redirect('/drug_list/')
    else:
        models.Drug.objects.filter(id=nid).delete()
    return redirect('/drug_list/')


# 出库---------------------------------------------------------------------
def sale_list(request):
    data_dict = {}
    search_value = request.GET.get('q', '')  # 得到搜索值
    if search_value:
        data_dict = {"time__contains": search_value}  # 字段__contains包含.....
    queryset = models.OutOrder.objects.filter(**data_dict).order_by("id")  # **为字典-字段顺序排列
    page_object = Pagination(request, queryset)
    context = {
        'active': 'sale_list',
        'search_value': search_value,  # 搜索值
        'queryset': page_object.page_queryset,
        'page_string': page_object.html(),
    }
    return render(request, 'sale_list.html', context)


def sale_add(request):
    if request.method == 'GET':
        form = SaleModelForm
        context = {
            'form': form,
            'active': 'sale_add',  # 侧边栏状态
            'title': '添加出库记录'
        }
        return render(request, 'public_add.html', context)

    form = SaleModelForm(data=request.POST)  # 用户post提交的数据，数据校验
    if form.is_valid():  # 如果数据合法，保存
        if form.is_valid():
            drug_name = form.cleaned_data.get('name')
            quantity = form.cleaned_data.get('quantity')
            insurance1 = form.cleaned_data.get('insurance')
            # 查找对应的药物对象
            drug = models.Drug.objects.filter(name=drug_name).first()
            if drug:
                if drug.insurance == 2 and insurance1 is True:  # 检查医保卡
                    form.add_error("insurance", "非医保卡报销，出库失败")
                    context = {
                        'form': form,
                        'active': 'sale_add',  # 侧边栏状态
                        'title': '添加出库记录'
                    }
                    return render(request, 'public_add.html', context)
                else:
                    # 检查库存是否足够
                    if drug.storage >= quantity:
                        # 更新库存
                        drug.storage -= quantity
                        drug.save()
                        form.instance.drug = drug  # form.instance.drug = drug  # 如果需要关联Drug对象
                        form.save()  # 保存出库记录
                        return redirect('/sale_list/')
                    else:
                        # 库存不足的处理逻辑
                        form.add_error(form.quantity, "库存不足，无法出库")
            else:
                # 找不到药物的处理逻辑
                form.add_error(form.name, "找不到指定的药物")
    context = {
        'form': form,
        'active': 'sale_add',  # 侧边栏状态
        'title': '添加出库记录'
    }
    return render(request, 'public_add.html', context)


#
# def sale_edit(request, nid):
#     row_object = models.OutOrder.objects.filter(id=nid).first()  # 保证修改范围
#     if not row_object:
#         return HttpResponse("警告，数据不存在！")
#     if request.method == "GET":
#         form = SaleModelForm(instance=row_object)  # 这将更新row_object在数据库中的记录，而不是创建一个新的记录
#         context = {
#             'form': form,
#             'title': '编辑出库记录'
#         }
#         return render(request, 'public_add.html', context)
#     form = SaleModelForm(data=request.POST, instance=row_object)
#     if form.is_valid():
#         form.save()
#         return redirect('/sale_list/')
#     context = {
#         'form': form,
#     }
#     return render(request, 'public_add.html', context)


def sale_delete(request, nid):
    models.OutOrder.objects.filter(id=nid).delete()
    return redirect('/sale_list/')


# 入库---------------------------------------------------------------------
def in_list(request):
    data_dict = {}
    search_value = request.GET.get('q', '')  # 得到搜索值
    if search_value:
        data_dict = {"time__contains": search_value}  # 字段__contains包含.....
    queryset = models.InOrder.objects.filter(**data_dict).order_by("id")  # **为字典-字段顺序排列
    page_object = Pagination(request, queryset)
    context = {
        'active': 'in_list',
        'search_value': search_value,  # 搜索值
        'queryset': page_object.page_queryset,
        'page_string': page_object.html(),
        'title': "入库记录",
    }
    return render(request, 'in_list.html', context)


def in_add(request):
    if request.method == 'GET':
        form = InModelForm
        context = {
            'form': form,
            'active': 'in_add',  # 侧边栏状态
            'title': '添加入库记录'
        }
        return render(request, 'public_add.html', context)

    form = InModelForm(data=request.POST)  # 用户post提交的数据，数据校验
    if form.is_valid():  # 如果数据合法，保存
        form.save()  # 保存出库记录
        from django.db import connection
        with connection.cursor() as cursor:
            # 调用存储过程，注意这里不需要括号（除非存储过程需要参数）
            cursor.execute("CALL InsertWarnings()")  # 调用MySQL里的存储过程函数
        return redirect('/in_list/')
    context = {
        'form': form,
        'active': 'in_add',  # 侧边栏状态
        'title': '添加入库记录'
    }
    return render(request, 'public_add.html', context)


def in_delete(request, nid):
    models.InOrder.objects.filter(id=nid).delete()
    return redirect('/in_list/')
