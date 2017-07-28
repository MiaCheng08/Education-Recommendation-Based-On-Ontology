from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.http import Http404, JsonResponse
from .models import *
from .knowledge import *
import datetime
import time
# "require_http_methods " is a Decorator to make a view only accept particular request methods
#@符号是装饰器的语法糖，在定义函数的时候使用，避免再一次赋值操作

#首页，知识图谱的展示
@require_http_methods(["GET"])#√
def index(request):
	if request.user.is_authenticated() and request.user.is_staff:
		return render(request, "glgl_app/admin_index.html")
	else:
		return render(request, "glgl_app/weighted_tree.html")

@require_http_methods(["GET"])#√
def admin_index(request):
	return render(request, "glgl_app/admin_index.html")

@require_http_methods(["GET"])#√
def get_feedback_data(request):
	d = {}
	d.setdefault("partpath", get_partpath_feedback_data(request))
	d.setdefault("graph", get_graph_feedback_data(request))
	d.setdefault("watch", get_watching(request))
	return JsonResponse(d)

def get_partpath_feedback_data(request):
	try:
		start = request.GET["start"].split("/")
		end = request.GET["end"].split("/")
		start_date = datetime.date(int(start[2]), int(start[0]), int(start[1]))
		end_date = datetime.date(int(end[2]), int(end[0]), int(end[1])) + datetime.timedelta(days=1)
		yes = PartFeedback.objects.filter(pfeed=True, pdate__range=(start_date, end_date)).count()
		no = PartFeedback.objects.filter(pfeed=False, pdate__range=(start_date, end_date)).count()
	except KeyError:
		yes = PartFeedback.objects.filter(pfeed=True).count()
		no = PartFeedback.objects.filter(pfeed=False).count()

	data = []
	total = yes + no
	if total > 0:
		if yes > 0:
			y = {}
			y.setdefault("indexLabel", "有用")
			y.setdefault("y", yes)
			data.append(y)
		if no > 0:
			d = {}
			d.setdefault("indexLabel", "无用")
			d.setdefault("y", no)
			data.append(d)
		return {"data": data, "msg": "ok"}
	else:
		return {"msg": "暂无反馈数据"}

def get_graph_feedback_data(request):
	try:
		start = request.GET["start"].split("/")
		end = request.GET["end"].split("/")
		start_date = datetime.date(int(start[2]), int(start[0]), int(start[1]))
		end_date = datetime.date(int(end[2]), int(end[0]), int(end[1])) + datetime.timedelta(days=1)#加一 才能把用户选的这一天给包进来
		yes = GraphFeedback.objects.filter(gfeed=True, gdate__range=(start_date, end_date)).count()
		no = GraphFeedback.objects.filter(gfeed=False, gdate__range=(start_date, end_date)).count()
	except KeyError:
		yes = GraphFeedback.objects.filter(gfeed=True).count()
		no = GraphFeedback.objects.filter(gfeed=False).count()

	data = []
	total = yes + no
	if total > 0:
		if yes > 0:
			y = {}
			y.setdefault("indexLabel", "有用")
			y.setdefault("y", round(yes, 2))
			data.append(y)
		if no > 0:
			d = {}
			d.setdefault("indexLabel", "无用")
			d.setdefault("y", round(no, 2))
			data.append(d)
		return {"data": data, "msg": "ok"}
	else:
		return {"msg": "暂无反馈数据"}

def get_watching(request):
	play = Video.objects.filter(status = 0).order_by("-play")[:10]
	like = Video.objects.filter(status=0).order_by("-like")[:10]
	favorite = Video.objects.filter(status=0).order_by("-favorite")[:10]

	data = {}

	if play.count() > 0:
		data.setdefault("playmsg", "ok")
		data.setdefault("play", [])
		for p in play:
			d = {}
			d.setdefault("label", p.title)
			d.setdefault("y", p.play)
			data["play"].append(d)
	else:
		data.setdefault("playmsg", "暂无反馈数据")

	if like.count() > 0:
		data.setdefault("likemsg", "ok")
		data.setdefault("like", [])
		for l in like:
			d = {}
			d.setdefault("label", l.title)
			d.setdefault("y", l.like)
			data["like"].append(d)
	else:
		data.setdefault("likemsg", "暂无反馈数据")

	if favorite.count() > 0:
		data.setdefault("favoritemsg", "ok")
		data.setdefault("favorite", [])
		for f in favorite:
			d = {}
			d.setdefault("label", f.title)
			d.setdefault("y", f.favorite)
			data["favorite"].append(d)
	else:
		data.setdefault("favoritemsg", "暂无反馈数据")

	return data

#在前端的JS中被请求 知识图谱的本体数据查询
@require_http_methods(["GET"])#√
def showtree(request):
	nodes = {}
	graph = ontology_sparql(dataset="math")#传入的参数是用来指定Sparql作用的数据范围——具体是哪一个dataset

	graph.weighted(nodes, "函数")#graph.tree_weightedtree(nodes, "math")
	return JsonResponse(nodes)#JsonResponse是将字典变为JSON格式？


#在个人页面请求完整的学习方案
@require_http_methods(["GET"])#√
def all_path(request):
	return render(request, "glgl_app/weighted_tree_user.html")

#在前端的JS中被请求
@require_http_methods(["GET"])#√
def show_all_path(request):
	nodes = {}
	user_id = "id" + str(request.user.id)
	graph = ontology_sparql(dataset="user", userid=user_id)
	graph.weighted_user(nodes, "函数")#第二个参数规定树的起点
	return JsonResponse(nodes)

#在前端的JS中被请求
@require_http_methods(["GET"])#√
def show_part_path(request, video_id):
	if request.user.is_authenticated():
		now = Video.objects.get(pk = video_id).tag
		#now = math_graph.search_knowledge(video_id)#当前正在学习的知识点
		if not now:
			return JsonResponse(data={'access': True, 'get': False})#知识点获取失败

		to_study_set = []

		user_id = "id" + str(request.user.id)
		user_graph = ontology_sparql(dataset="user", userid=user_id)
		math_graph = ontology_sparql()
		#判断是否是傀儡
		if math_graph.search_equi(now) == "yes":
			now = math_graph.search_equivalent_knowledge(now)
		# 确定学习起点
		start = user_graph.get_learning_start(now)
		#确定好学习起点，选择后续知识点
		user_graph.get_part_path(start, now, to_study_set)
		nodes = []
		#根据形成的学习路径，找合适的资源，填补路径，完善部分学习方案
		x = 200
		y = 30
		for node in to_study_set:
			if node != "math":
				math_graph.filling_path(nodes, node, x, y)
				math_graph.myid += 1
				y += 40
		return JsonResponse(data = {'access': True, 'get': True, 'nodes': nodes})#JsonResponse是将字典变为JSON格式？
	else:
		return JsonResponse(data={'access': False})  # JsonResponse是将字典变为JSON格式？

@require_http_methods(["GET"])#√
def testmode(request):
	return render(request, "glgl_app/testmode.html")#计划以悬浮窗口的形式出现在注册成功后的注册页面

#在前端的JS中被请求
@require_http_methods(["GET"])#√
def knowledge_test(request):
	return render(request, "glgl_app/knowledge_test.html")

#在前端的JS中被请求
@require_http_methods(["GET"])#√
def get_all_knowledge(request):
	knowledge_set = {}
	graph = ontology_sparql()#传入的参数是用力啊指定Sparql作用的数据范围——具体是哪一个dataset
	graph.all_knowledge(knowledge_set, "math")
	return JsonResponse(knowledge_set)#JsonResponse是将字典变为JSON格式？

#在前端的JS中被请求
@require_http_methods(["GET"])#√
def get_knowledge_no_dummy(request):
	knowledge_set = {}
	graph = ontology_sparql()
	graph.all_knowledge_except_dummy(knowledge_set, "math")#要确保第二个参数不是dummy
	return JsonResponse(knowledge_set)

#在前端的JS中被请求
@require_http_methods(["POST"])#√
def video_set(request):
	videos = request.POST["videos"].split(",")
	knowledge = request.POST["knowledge"]
	videos_set = []
	for video in videos:
		if video:
			id = video.split("_")[-1]
			video = Video.objects.get(status = 0, pk = id)#使用get而不是filter get的结果是Video类型，filter是QuerySet类型
			videos_set.append(video)

	return render(request, "glgl_app/video_set.html",
				context = {"videos": videos_set,
						   "length": videos_set.__len__(),
						   "pageTitle": knowledge})

#在进入home之前应有login，在model中，在login之前应该有register，也在model中

#进入其他人的个人主页
@require_http_methods(["GET"])#√
def homepage(request, user_id):
	try:
		user = User.objects.get(pk = user_id)
	except User.DoesNotExist:
		raise Http404("User does not exist")
	if request.user.is_authenticated():
		if int(user_id) == int(request.user.id):
			histories = user.history_set.all().order_by("-hdate")
			favorites = user.userextraprofile.favorite_list.all()
			return render(request, 'glgl_app/homepage.html',
						context = {'user': user,
								   'histories': histories,
								   'favorites': favorites,
									'video_set': user.uploader.all().filter(status = 0).order_by("-time")})
		else:
			return render(request, 'glgl_app/homepage_visitor.html',
						  context={'user': request.user,
								   "target": user,
								   'video_set': user.uploader.all().filter(status=0).order_by("-time")})
	else:
		return render(request, 'glgl_app/homepage_visitor.html',
					  context={'user': request.user,
							   "target": user,
							   'video_set': user.uploader.all().filter(status=0).order_by("-time")})
def history(request, user_id):
	user = User.objects.get(pk = user_id)
	histories = user.history_set.all().order_by("-hdate")
	history_set = []
	for h in histories:
		d = {}
		time = timezone.localtime(h.hdate).strftime("%Y-%m-%d %H:%M:%S")
		d.setdefault("date", time)
		d.setdefault("change", round(h.hchange, 2))
		d.setdefault("score", round(h.hscore, 2))

		video = h.HVideo
		d.setdefault("knowledge", video.tag)
		title = video.title + "," + str(video.pk)
		d.setdefault("title", title)
		history_set.append(d)
	return JsonResponse(data={'history_set': history_set})


#个人信息，在该界面上可以补充修改自己的信息，并表单提交
@require_http_methods(["GET"])#√
def home(request):
	if request.user.is_authenticated():
		return render(request, "glgl_app/profile.html")
	else:
		return render(request, "glgl_app/notlogin.html")

#查看封禁视频集合，应放在管理员系统中
@require_http_methods(["GET"])#√
def checkpage(request):
	if not request.user.is_staff:
		return render(request, 'glgl_app/notadmin.html')
	else:
		return render(request, 'glgl_app/check.html',
					  context = {'checking_videos': Video.objects.filter(status = 4).order_by("time")})

#封禁视频，应放在管理员系统中
@require_http_methods(["GET"])#√
def banpage(request):
	if not request.user.is_staff:
		return render(request, 'glgl_app/notadmin.html')
	else:
		return render(request, 'glgl_app/banvideo.html',
						context = {'checking_videos': Video.objects.filter(status = 2).order_by("time")})

#查看更多视频评论
@require_http_methods(["GET"])#√ 在video.html中被调用
def more_comments(request, video_id):
	if not request.user.is_authenticated:
		return render(request, 'glgl_app/video.html')
	else:
		video = Video.objects.get(pk = video_id)#传进来个这个真是有点多余 不止这一处
		comments = video.comment_set.all().order_by("-cdate")
		return render(request, 'glgl_app/more_comments.html',
					  context = {'video':video, 'all_comment': comments})

#密码修改成功，提示成功 这个麻烦，要改掉
@require_http_methods(["GET"])#√
def setPasswordSuc(request):
	return render(request, "glgl_app/setpassword-suc.html")

def aboutus(request):#√
	return render(request,'glgl_app/about.html')

#反馈#√
@require_http_methods(["POST"])
def graph_feed(request):
	if request.user.is_authenticated():
		try:
			user = request.user
			feed = request.POST['feed']
			if feed == "True":
				g = GraphFeedback(GUser=user, gfeed = True)
				g.save()
			if feed == "False":
				g = GraphFeedback(GUser=user, gfeed = False)
				g.save()
		except Video.DoesNotExist:
			return JsonResponse(data={'res': False, 'error': '发送失败！'})
		return JsonResponse(data={'msg': "谢谢反馈！"})
	else:
		return JsonResponse(data={'msg': "谢谢反馈！"})