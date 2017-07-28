from django.shortcuts import render
from django.core import serializers
from django.http import HttpResponseRedirect, Http404, JsonResponse, HttpResponseBadRequest, QueryDict
from django.views.decorators.http import require_http_methods
from glgl_app.models import *
from itertools import chain
#search是在导航栏右边的搜索框——是form标签的action属性定义的路径从而被调用的，
#由路径在urls.py中找到对应的视图函数，从而到了这里

@require_http_methods(["GET"])
def search(request):
	v1 = Video.objects.filter(status = 0,
								title__icontains = request.GET["title_include"])
	v2 = Video.objects.filter(status=0,
							  teacher__icontains=request.GET["title_include"])
	#上面的代码并没有运行任何的数据库查询
	#要真正从数据库获得数据，你需要遍历queryset:
	videos = []
	for v in v1:
		videos.append(v)
	for v in v2:
		videos.append(v)
	return render(request, "glgl_app/video_set.html",
				  context = {"pageTitle": "搜索 "+ request.GET["title_include"],
                             "length":videos.__len__(),
				  'videos': videos})
							#title本是数据库中Video表的其中一个属性，后面用下划线加上“icontains”意味着title中含有
							# “title__icontains”该值的video
