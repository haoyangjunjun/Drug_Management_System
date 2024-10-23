from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

'''中间件,测试
在setting中注册记得
'''

"""
        在视图处理请求之前调用。  
        用于检查用户是否已登录，并决定是否需要进行重定向。  
"""


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 排除login页面，不然就循环了   request.path_info  获取当前用户请求的URL
        if request.path_info in ["/login/", "/image_code/", '/admin_add2/']:
            return
        # 读取session信息，1已经登陆，0未登录
        info_dice = request.session.get("info")
        if info_dice:  # 用户已登录，继续处理请求
            return  # yes
        return redirect('/login/')  # no  # 用户未登录，重定向到登录页面

    def process_response(self, request, response):
        return response


"""  
                👆在视图处理完请求并返回response对象之后调用。  
                通常用于对response对象进行一些后处理操作。  
                返回原始的response对象（也就是说没用）。  
"""
