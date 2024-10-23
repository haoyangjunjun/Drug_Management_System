from django.db import models


class Admin(models.Model):
    username = models.CharField(verbose_name="用户名", max_length=32)
    password = models.CharField(verbose_name="密码", max_length=64)


class Supplier(models.Model):
    name = models.CharField(verbose_name='供货商名', max_length=32)
    address = models.CharField(verbose_name='地址', max_length=64)

    def __str__(self):
        return self.name  # 输出对象显示名字


class Drug(models.Model):
    name = models.CharField(verbose_name='名称', max_length=32)
    price = models.FloatField(verbose_name='进货价', max_length=16)
    price2 = models.FloatField(verbose_name='售价', max_length=16)
    storage = models.IntegerField(verbose_name='库存量', default=0)
    quality_time = models.IntegerField(verbose_name='保质期(月)', default=36)
    insurance_choices = [
        (1, '是'),
        (2, '否'),
    ]
    # 添加药品种类字段
    drug_type_choices = [
        (1, '处方药'),
        (2, '非处方药'),
        (3, '中药'),
        (4, '保健品'),
        (5, '其他'),
    ]
    drug_type = models.IntegerField(choices=drug_type_choices, verbose_name='药品种类')
    insurance = models.IntegerField(choices=insurance_choices, verbose_name='是否纳入医保')
    supplier = models.ForeignKey(verbose_name='供货商', to='Supplier', to_field="id", on_delete=models.CASCADE)

    # restrict(约束):当在父表（即外键的来源表）中删除对应记录时，首先检查该记录是否有对应外键，如果有则不允许删除。
    def __str__(self):
        return self.name  # 输出对象显示名字


class InOrder(models.Model):
    time = models.DateTimeField(verbose_name='时间', auto_now_add=True)
    name = models.ForeignKey(Drug, verbose_name='名称', on_delete=models.RESTRICT)
    quantity = models.IntegerField(verbose_name='数量')
    production_date = models.DateTimeField(verbose_name='生产日期')
    total_price = models.IntegerField(verbose_name='总价', default=0)

    def __str__(self):
        return self.name  # 输出对象显示名字


class OutOrder(models.Model):
    time = models.DateTimeField(verbose_name='时间', auto_now_add=True)
    name = models.ForeignKey(Drug, verbose_name='名称', on_delete=models.RESTRICT)
    quantity = models.IntegerField(verbose_name='数量')
    total_price = models.IntegerField(verbose_name='总价', default=0)
    insurance = models.BooleanField(verbose_name='是否使用医保卡支付', choices=((True, '是'), (False, '否')))
    out_choices = [
        ('sale', '售出'),
        ('loss', '损耗（过保质期）'),
    ]
    out_type = models.CharField(verbose_name='方式', max_length=10, choices=out_choices)


class Warnings(models.Model):
    warning_choices = [
        ('little', '库存过少'),
        ('time', '即将过期'),
    ]
    warning_type = models.CharField(verbose_name='预警类型', max_length=10, choices=warning_choices)
    in_id = models.ForeignKey(InOrder, verbose_name='入库id', on_delete=models.CASCADE, null=True)
    drug_id = models.ForeignKey(Drug, verbose_name='药品id', on_delete=models.CASCADE, null=True)
    time = models.IntegerField(verbose_name='剩余时间', null=True)
    count = models.IntegerField(verbose_name='剩余数量', null=True)
