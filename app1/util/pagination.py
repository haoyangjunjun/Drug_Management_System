from django.utils.safestring import mark_safe

""""
分页系统
    page_object = Pagination(request, queryset)
    return
        'queryset': page_object.page_queryset,
        'page_string': page_object.html()
html部分
        <nav aria-label="Page navigation">
            <ul class="pagination">
                {{ page_string }}
            </ul>
        </nav>
        
html修改后为：
        <nav aria-label="Page navigation">
            <ul class="pagination">
                {{ page_string }}
                <li>
                    <form style="float: left;margin-left: -1px" method="get">
                        <input name="q" value="{{ search_value }}" type="hidden">
                        <input name="page"
                               style="position: relative;float:left;display: inline-block;width: 80px;border-radius: 0;"
                               type="text" class="form-control" placeholder="页码">
                        <button style="border-radius: 0" class="btn btn-default" type="submit">跳转</button>
                    </form>
                </li>
            </ul>
        </nav>
"""


class Pagination(object):

    def __init__(self, request, queryset, page_size=8, page_param="page", plus=5):
        """
        :param request: 请求的对象
        :param queryset: 符合条件的数据（根据这个数据给他进行分页处理）
        :param page_size: 每页显示多少条数据
        :param page_param: 在URL中传递的获取分页的参数，例如：/pretty/list/?page=12
        :param plus: 显示当前页的 前或后几页（页码）
        """

        import copy
        query_dict = copy.deepcopy(request.GET)
        query_dict._mutable = True
        self.query_dict = query_dict

        self.page_param = page_param
        page = request.GET.get(page_param, "1")

        if page.isdecimal():  # 如果只有十进制字符，则返回True，否则为False。
            page = int(page)
        else:
            page = 1

        self.page = page
        self.page_size = page_size

        self.start = (page - 1) * page_size
        self.end = page * page_size

        self.page_queryset = queryset[self.start:self.end]

        total_count = queryset.count()
        total_page_count, div = divmod(total_count, page_size)
        if div:
            total_page_count += 1
        self.total_page_count = total_page_count
        self.plus = plus
        # 新增功能--------页码数超出判断
        # 如果请求的页码超出总页数，返回总页数
        # 二次修改，bug不断
        if page < 1 or page > total_page_count > 0:
            self.page = total_page_count
            self.page_size = page_size

            self.start = (self.page - 1) * page_size
            self.end = self.page * page_size

            self.page_queryset = queryset[self.start:self.end]

            total_count = queryset.count()
            total_page_count, div = divmod(total_count, page_size)
            if div:
                total_page_count += 1
            self.total_page_count = total_page_count
            self.plus = plus

    def html(self):
        # 计算出，显示当前页的前5页、后5页
        if self.total_page_count <= 2 * self.plus + 1:
            # 数据库中的数据比较少，都没有达到11页。
            start_page = 1
            end_page = self.total_page_count
        else:
            # 数据库中的数据比较多 > 11页。

            # 当前页<5时（小极值）
            if self.page <= self.plus:
                start_page = 1
                end_page = 2 * self.plus + 1
            else:
                # 当前页 > 5
                # 当前页+5 > 总页面
                if (self.page + self.plus) > self.total_page_count:
                    start_page = self.total_page_count - 2 * self.plus
                    end_page = self.total_page_count
                else:
                    start_page = self.page - self.plus
                    end_page = self.page + self.plus

        # 页码
        page_str_list = []

        self.query_dict.setlist(self.page_param, [1])
        page_str_list.append('<li><a href="?{}">首页</a></li>'.format(self.query_dict.urlencode()))

        # 上一页
        if self.page > 1:
            self.query_dict.setlist(self.page_param, [self.page - 1])
            prev = '<li><a href="?{}">上一页</a></li>'.format(self.query_dict.urlencode())
        else:
            self.query_dict.setlist(self.page_param, [1])
            prev = '<li><a href="?{}">上一页</a></li>'.format(self.query_dict.urlencode())
        page_str_list.append(prev)

        # 页面
        for i in range(start_page, end_page + 1):
            self.query_dict.setlist(self.page_param, [i])
            if i == self.page:
                ele = '<li class="active"><a href="?{}">{}</a></li>'.format(self.query_dict.urlencode(), i)
            else:
                ele = '<li><a href="?{}">{}</a></li>'.format(self.query_dict.urlencode(), i)
            page_str_list.append(ele)

        # 下一页
        if self.page < self.total_page_count:
            self.query_dict.setlist(self.page_param, [self.page + 1])
            prev = '<li><a href="?{}">下一页</a></li>'.format(self.query_dict.urlencode())
        else:
            self.query_dict.setlist(self.page_param, [self.total_page_count])
            prev = '<li><a href="?{}">下一页</a></li>'.format(self.query_dict.urlencode())
        page_str_list.append(prev)

        # 尾页
        self.query_dict.setlist(self.page_param, [self.total_page_count])
        page_str_list.append('<li><a href="?{}">尾页</a></li>'.format(self.query_dict.urlencode()))

        search_string = """
        
            """

        page_str_list.append(search_string)
        page_string = mark_safe("".join(page_str_list))
        return page_string
