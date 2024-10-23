from django import forms


class BootStrap:
    def __init__(self, *args, **kwargs):  # 初始化方法
        super().__init__(*args, **kwargs)
        # ↓重新定义init方法，super执行父类init方法，通过循环找到字段中的插件，给每个字段的插件设置attrs
        for name, field in self.fields.items():
            # 字段中有属性，保留原来的属性
            if field.widget.attrs:
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["placeholder"] = field.label
            else:
                field.widget.attrs = {
                    'class': 'form-control',
                    "placeholder": field.label
                }


class BootStrapModelForm(BootStrap, forms.ModelForm):  # 二重继承
    pass


class BootStrapForm(BootStrap, forms.Form):
    pass
