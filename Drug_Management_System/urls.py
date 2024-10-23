from django.urls import path
from app1.views import drug, login, admin, count, supplier

urlpatterns = [
    # 主页
    path('', drug.home),
    # 药品
    path('drug_list/', drug.drug_list),
    path('drug_add/', drug.drug_add),
    path('drug_edit/<int:nid>/', drug.drug_edit),
    path('drug_delete/<int:nid>/', drug.drug_delete),
    # 供货商
    path('supplier_list/', supplier.supplier_list),
    path('supplier_add/', supplier.supplier_add),
    path('supplier_edit/<int:nid>/', supplier.supplier_edit),
    path('supplier_delete/<int:nid>/', supplier.supplier_delete),
    # 出库
    path('sale_list/', drug.sale_list),
    path('sale_add/', drug.sale_add),
    path('sale_delete/<int:nid>/', drug.sale_delete),
    path('in_list/', drug.in_list),
    path('in_add/', drug.in_add),
    path('in_delete/<int:nid>/', drug.in_delete),
    # path('sale_edit/<int:nid>/', drug.sale_edit),
    # 管理员
    path('admin_list/', admin.admin_list),
    path('admin_add/', admin.admin_add),
    path('admin_edit/<int:nid>/', admin.admin_edit),
    path('admin_delete/<int:nid>/', admin.admin_delete),
    path('admin_reset/<int:nid>/', admin.admin_reset),
    # 登录
    path('login/', login.login),
    path('logout/', login.logout),
    path('image_code/', login.image_code),
    path('admin_add2/', login.admin_add),
    # 统计
    path('count/', count.out_order_summary_view),
    #警告
    path('warning/',count.get_warnings)
]
