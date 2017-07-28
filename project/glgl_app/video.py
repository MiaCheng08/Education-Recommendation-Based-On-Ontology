from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse, HttpResponseForbidden

from .models import *
from .knowledge import *

#播放视频 #√
def video_play(request, video_id):
	try:
		video = Video.objects.get(pk = video_id)
	except Video.DoesNotExist:
		raise Http404("Video does not exist")
	if (not request.user.is_authenticated() or not request.user.is_staff) and video.status != 0:
		return render(request, "glgl_app/video-notfound.html")
	comments = video.comment_set.all().order_by("-cdate")[:4]
	# ×××_set也是一种反向查询的方法 与数据库设计时用的related_name属性作用一样
	# 两者同时出现时 使用×××_set会报报错
	if not request.user.is_authenticated():
		graph = ontology_sparql()
		demand = float(graph.search_demand(video.tag))
		if demand >= 1.0:
			demand = "掌握（100%）"
		elif demand >= 0.6:
			demand = "理解（60%）"
		else:
			demand = "了解（20%）"
		description = graph.search_description(video.tag)
		videos_set = []
		videos = graph.search_resource(video.tag).split(",")
		for v in videos:
			id = v.split("_")[-1]
			if int(id) != int(video_id):
				vi = Video.objects.get(status=0, pk=id)  # 使用get而不是filter get的结果是Video类型，filter是QuerySet类型
				videos_set.append(vi)
		return render(request, 'glgl_app/video_anonymous.html', {'video': video,
												   'latest_comment': comments,
												   'demand': demand,
												   "description": description,
												   "videos": videos_set,
												   'video_type': video.video.name[-3:]})
	elif request.user.is_staff:
		graph = ontology_sparql()
		demand = float(graph.search_demand(video.tag))
		if demand >= 1.0:
			demand = "掌握（100%）"
		elif demand >= 0.6:
			demand = "理解（60%）"
		else:
			demand = "了解（20%）"
		description = graph.search_description(video.tag)
		return render(request, 'glgl_app/video_admin.html', {'video': video,
													   'demand': demand,
													   "description": description,
													   'latest_comment': comments,
													   'video_type': video.video.name[-3:]})  # [-3:]取后三个字符
	else:
		video.play += 1  # 设计的有bug
		video.save()
		graph = ontology_sparql()
		demand = float(graph.search_demand(video.tag))
		if demand >= 1.0:
			demand = "掌握（100%）"
		elif demand >= 0.6:
			demand = "理解（60%）"
		else:
			demand = "了解（20%）"
		description = graph.search_description(video.tag)
		videos_set = []
		videos = graph.search_resource(video.tag).split(",")
		for v in videos:
			id = v.split("_")[-1]
			if int(id) != int(video_id):
				vi = Video.objects.get(status=0, pk=id)  # 使用get而不是filter get的结果是Video类型，filter是QuerySet类型
				videos_set.append(vi)
		return render(request, 'glgl_app/video.html', {'video': video,
												   'latest_comment': comments,
												   'demand': demand,
												   "description": description,
												   "videos": videos_set,
												   'video_type': video.video.name[-3:]})

#视频通过 #√，这里为什么要用POST
@require_http_methods(["POST"])
def video_unblock(request, video_id):
	if not request.user.is_authenticated() or not request.user.is_staff:
		return HttpResponseForbidden()#禁止访问
	try:
		video = Video.objects.get(pk = video_id)
	except Video.DoesNotExist:
		return Http404("Video not found")
	video.status = 0
	video.title = request.POST["title"]  # 管理员可以修改这三项视频信息
	video.tag = request.POST["tag"]
	video.difficulty = request.POST["difficulty"]
	video.teacher = request.POST["teacher"]
	video.save()  # 保存管理员修改过的视频信息
	# 管理员审核通过后，就可以创建资源本体实例了
	graph = ontology_sparql()
	if create_video_ontology_instance(graph, video.tag, video.difficulty, video_id):
		return JsonResponse({'msg': "操作成功！"})
	else:
		return JsonResponse({'msg': "操作失败！"})

#视频封禁 #√
@require_http_methods(["POST"])
def video_ban(request, video_id):
	if not request.user.is_authenticated() or not request.user.is_staff:
		return HttpResponseForbidden()
	try:
		video = Video.objects.get(pk = video_id)
	except Video.DoesNotExist:
		return Http404("Video not found")
	video.status = 2
	video.save()
	return HttpResponse()

#添加评论 有一部分尝试失败 有时间再来！
@require_http_methods(['POST'])
def video_comment_add(request):
	if request.user.is_authenticated():
		try:
			video = Video.objects.get(pk = request.POST['video_id'])
			user = request.user
			content = request.POST['content']
			c = Comment(video = video, user = user, content = content)#Comment是导进来的类
			c.save()
		except Video.DoesNotExist:
			return JsonResponse(data = {'res': False, 'error': '发送失败！'})#在前端通过data.res获得False，以及data.error
			#但是我没有成功
		return JsonResponse(data = {'res': True })
	else:
		return JsonResponse(data = {'res': False, 'error': '用户没有权限！'})

#点赞 #√
@require_http_methods(["POST"])
def like(request, video_id):
	try:
		video = Video.objects.get(pk = video_id)
	except Video.DoesNotExist:
		return Http404("Video not found")
	if not request.user.userextraprofile in video.like_list.all():
	#not request.user in video.like_list.all(): 使用user类 老是iterable过不了关
		video.like += 1
		video.like_list.add(request.user.userextraprofile)
	video.save()
	return JsonResponse(data = {'like': video.like})#为什么要用JSON格式将数据发过去？
	#JsonResponse：to create a JSON-encoded response，
	#JsonResponse(data, encoder=DjangoJSONEncoder, safe=True, json_dumps_params=None, **kwargs)
	#The first parameter——data, should be a dict instance.
"""
JSON(JavaScript Object Notation) 是一种轻量级的数据交换格式。它基于ECMAScript的一个子集。
JSON采用完全独立于语言的文本格式，但是也使用了类似于C语言家族的习惯（包括C、C++、C#、Java、
JavaScript、Perl、Python等）。这些特性使JSON成为理想的数据交换语言。易于人阅读和编写，同时
也易于机器解析和生成(一般用于提升网络传输速率)。
JSON 语法是 JavaScript 对象表示语法的子集,书写格式是：名称/值对。"firstName":"John" 等价于firstName="John"
"""

#收藏 #√
@require_http_methods(["POST"])
def favorite(request, video_id):
	try:
		video = Video.objects.get(pk = video_id)
	except Video.DoesNotExist:
		return Http404("Video not found")
	if not request.user.userextraprofile in video.favorite_list.all():
		video.favorite += 1
		video.favorite_list.add(request.user.userextraprofile)
	video.save()
	return JsonResponse(data = {'favorite': video.favorite})

#增加播放量 #这个在urls.py中不存在，没有对应的路径，那么前段就不会想后端请求这个
@require_http_methods(['POST'])
def play_add(request):
	try:
		video = Video.objects.get(pk = request.POST['id'])
		video.play += 1
		video.save()
	except Video.DoesNotExist:
		return JsonResponse(data = {'res': False})
	return JsonResponse(data = {'res': True})

#反馈#√
@require_http_methods(["POST"])
def part_feed(request, video_id):
	if request.user.is_authenticated():
		try:
			video = Video.objects.get(pk = video_id)
			user = request.user
			feed = request.POST['feed']
			if feed == "True":
				p = PartFeedback(PVideo=video, PUser=user, pfeed = True)
				p.save()
			if feed == "False":
				p = PartFeedback(PVideo=video, PUser=user, pfeed = False)
				p.save()
		except Video.DoesNotExist:
			return JsonResponse(data={'res': False, 'error': '发送失败！'})
		return JsonResponse(data={'msg': "谢谢反馈！"})
	else:
		return JsonResponse(data={'msg': "谢谢反馈！"})