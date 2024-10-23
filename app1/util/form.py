from app1 import models
from django.core.exceptions import ValidationError
from django import forms
from app1.util.bootstrap import BootStrapModelForm
from app1.util.encrypt import md5


class DrugModelForm(BootStrapModelForm):
    class Meta:
        model = models.Drug
        fields = ["name","drug_type", "price", "price2", "insurance", "quality_time", "supplier"]


class AdminModelForm(BootStrapModelForm):
    # 定义一个字段confirm_password，用于输入确认密码
    confirm_password = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput  # 密码显示为*
    )

    # 配置模型表单 元信息
    class Meta:
        model = models.Admin
        fields = ["username", "password", "confirm_password"]  # 指定表单中要包含的字段
        widgets = {
            "password": forms.PasswordInput(render_value=True)  # 取消默认清空 render_value=True
        }

    def clean_password(self):  # 在表单验证时处理password字段
        pwd = self.cleaned_data.get("password")
        return md5(pwd)  # 对密码进行MD5加密

    def clean_confirm_password(self):  # 钩子函数，密码一致校验

        # 从cleaned_data字典中获取password和confirm_password字段的值
        pwd = self.cleaned_data.get("password")
        confirm = md5(self.cleaned_data.get("confirm_password"))
        if confirm != pwd:
            raise ValidationError("密码不一致，重新输入")
        return confirm


class AdminEditModelForm(BootStrapModelForm):
    class Meta:
        model = models.Admin
        fields = ['username']


class AdminResetModelForm(BootStrapModelForm):
    confirm_password = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput(render_value=True)  # 密码*
    )

    class Meta:
        model = models.Admin
        fields = ['password', 'confirm_password']  # 就这和上边不一样，其他都一样
        widgets = {
        }

    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        md5_pwd = md5(pwd)
        # 检验数据库里密码与新输入密码一致
        exists = models.Admin.objects.filter(id=self.instance.pk, password=md5_pwd).exists()  # pk为当前行id
        if exists:
            raise ValidationError("新密码不能与原密码相同")
        return md5_pwd

    def clean_confirm_password(self):  # 钩子函数，密码一致校验
        pwd = self.cleaned_data.get("password")
        confirm = md5(self.cleaned_data.get("confirm_password"))
        if confirm != pwd:
            raise ValidationError("密码不一致，重新输入")
        return confirm


class LoginForm(BootStrapModelForm):  # 使用bootstrap.py
    code = forms.CharField(
        label="请在60秒内输入验证码",
        widget=forms.TextInput(),
        required=True
    )

    class Meta:
        model = models.Admin
        fields = ['username', 'password', 'code']  # 就这和上边不一样，其他都一样
        widgets = {
            "password": forms.PasswordInput(render_value=True)  # 更改默认清空render_value=True
        }

    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)

    def __init__(self, *args, **kwargs):  # 初始化方法
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if field.widget.attrs:
                field.widget.attrs["class"] = "form_input"  # 为了form_input这碟醋包的饺子
                field.widget.attrs["placeholder"] = field.label
            else:
                field.widget.attrs = {
                    'class': 'form_input',
                    "placeholder": field.label
                }


class SupplierModelForm(BootStrapModelForm):
    class Meta:
        model = models.Supplier
        fields = "__all__"


class SaleModelForm(BootStrapModelForm):
    class Meta:
        model = models.OutOrder
        # fields = "__all__"
        fields = ['name', 'quantity', 'insurance', 'out_type']


class InModelForm(BootStrapModelForm):
    class Meta:
        model = models.InOrder
        fields = ['name', 'quantity', 'production_date']

    # def total_price(self):
    #     name = self.cleaned_data.get("name")
    #     a = models.Drug.objects.filter(name=name).price2
    #     quantity = self.cleaned_data.get("quantity")
    #     total_price = a*quantity
    #     return total_price

    # def total_price(self):
    #     name = self.cleaned_data.get("name")
    #     if name:  # 确保name存在
    #         try:
    #             # 使用get方法来获取Drug对象，如果找不到会抛出Drug.DoesNotExist异常
    #             drug = models.Drug.objects.get(name=name)
    #             price2 = drug.price2  # 获取price2属性
    #             quantity = self.cleaned_data.get("quantity", 0)  # 确保quantity存在，否则默认为0
    #             total_price = price2 * quantity
    #             return total_price
    #         except models.Drug.DoesNotExist:
    #             # 如果找不到对应name的Drug对象，则返回适当的错误或者None
    #             return None  # 或者抛出一个异常，取决于您的需求
    #     else:
    #         # 如果name不存在，则返回适当的错误或者None
    #         return None  # 或者抛出一个异常，取决于您的需求
