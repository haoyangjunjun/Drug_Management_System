from django.db.models import Sum
from django.db.models.functions import ExtractYear, ExtractMonth
from django.http import JsonResponse
from django.shortcuts import render
from app1.models import OutOrder, InOrder, Warnings, Drug
from datetime import datetime
from collections import defaultdict


def out_order_summary_view(request):
    # 按月份的收入条形图-------------------------------------------------------------
    # 获取当前年份
    search_value = request.GET.get('year', '')  # 得到搜索值
    search_value2 = request.GET.get('month', '')  # 得到搜索值2
    if search_value:
        current_year = search_value  # 搜索搜索年份
    else:
        current_year = datetime.now().year
    if search_value2:
        current_month = int(search_value2)  # 搜索搜索
    else:
        current_month = datetime.now().month
    queryset = OutOrder.objects.annotate(  # 返回一个查询集，其中返回的对象已使用额外的数据或聚合进行批注。
        year=ExtractYear('time'),
        month=ExtractMonth('time')
    ).values('year', 'month').annotate(
        total_price_sum=Sum('total_price')
    ).filter(year=current_year).order_by('month')
    months = list(range(1, 13))  # 生成1到12月的列表
    # 使用defaultdict来简化字典的创建，其中默认值为0
    monthly_sums = defaultdict(int)
    for item in queryset:
        monthly_sums[item['month']] = item['total_price_sum']
        # 将months列表转换为包含销售额的列表，如果某个月没有销售额则0
    monthly_sums_list = [monthly_sums[month] for month in months]
    # 将monthly_sums_list传递给模板
    # ---------------------------------------------------------------------------
    # 按月份的支出条形图
    queryset2 = InOrder.objects.annotate(  # 返回一个查询集，其中返回的对象已使用额外的数据或聚合进行批注。
        year=ExtractYear('time'),
        month=ExtractMonth('time')
    ).values('year', 'month').annotate(
        total_price_sum=Sum('total_price')
    ).filter(year=current_year).order_by('month')
    # 使用defaultdict来简化字典的创建，其中默认值为0
    monthly_sums2 = defaultdict(int)
    for item in queryset2:
        monthly_sums2[item['month']] = item['total_price_sum']
        # 将months列表转换为包含销售额的列表，如果某个月没有销售额则0
    monthly_sums_list2 = [monthly_sums2[month] for month in months]
    # 按月份的医保支付占比饼图
    # 用医保--------------------------------------------------------------------
    queryset3 = OutOrder.objects.filter(insurance=0).annotate(
        year=ExtractYear('time'),
        month=ExtractMonth('time')
    ).values('year', 'month').annotate(
        total_price_sum=Sum('total_price')
    ).filter(year=current_year).order_by('month')
    monthly_sums3 = defaultdict(int)
    for item in queryset3:
        monthly_sums3[item['month']] = item['total_price_sum']
    # datalist = [current_month]  # 月份，列表格式
    datalist = [current_month]
    yibaoka = [monthly_sums3[month] for month in datalist]
    # 用现金---------------------------------------------------------------
    queryset4 = OutOrder.objects.filter(insurance=1).annotate(
        year=ExtractYear('time'),
        month=ExtractMonth('time')
    ).values('year', 'month').annotate(
        total_price_sum=Sum('total_price')
    ).filter(year=current_year).order_by('month')
    monthly_sums4 = defaultdict(int)
    for item in queryset4:
        monthly_sums4[item['month']] = item['total_price_sum']
    xianjin = [monthly_sums4[month] for month in datalist]
    monthly_sums_list3 = yibaoka + xianjin  # 合并列表
    # 分类库存环形图------------------------------------------------------------------
    datalist2 = []
    qy1 = Drug.objects.filter(drug_type=1).annotate(
        storage_sum=Sum('storage')
    ).values_list('storage_sum', flat=True)  # values_list和flat=True来获取storage_sum的值
    datalist2 = datalist2 + list(qy1)
    qy2 = Drug.objects.filter(drug_type=2).annotate(
        storage_sum=Sum('storage')
    ).values_list('storage_sum', flat=True)
    datalist2 = datalist2 + list(qy2)
    qy3 = Drug.objects.filter(drug_type=3).annotate(
        storage_sum=Sum('storage')
    ).values_list('storage_sum', flat=True)
    datalist2 = datalist2 + list(qy3)
    qy4 = Drug.objects.filter(drug_type=4).annotate(
        storage_sum=Sum('storage')
    ).values_list('storage_sum', flat=True)
    datalist2 = datalist2 + list(qy4)
    qy5 = Drug.objects.filter(drug_type=5).annotate(
        storage_sum=Sum('storage')
    ).values_list('storage_sum', flat=True)
    datalist2 = datalist2 + list(qy5)

    context = {
        'monthly_sums_list2': monthly_sums_list2,
        'monthly_sums_list3': monthly_sums_list3,
        'monthly_sums_list': monthly_sums_list,
        'datalist2': datalist2,  # 分类库存环形图
        'search_value': search_value,  # 搜索值
        'search_value2': search_value2,  # 搜索值2
        'title': '统计信息',
        'active': 'count',
        'title2': current_year,  # 年份标题
        'title3': current_month,
    }
    return render(request, 'count.html', context)


# 警告信息json
def get_warnings(request):
    warnings_list = Warnings.objects.all().values('warning_type', 'time', 'count', 'in_id', 'drug_id')
    # 转换为JSON可序列化的格式
    warnings_json = list(warnings_list)
    return JsonResponse(warnings_json, safe=False)
