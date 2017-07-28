from django.contrib import auth
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User
from django.db import models
from django import forms
from django.views.decorators.http import require_http_methods
import django.utils.timezone as timezone
import os

from .knowledge import *


# 用户额外信息——对系统自带的User类进行扩展：采用新建一个profile model，并与User建立一对一关系
class UserExtraProfile(models.Model):
    user = models.OneToOneField(User)  # User是系统自带的类/model
    headimage = models.ImageField(upload_to='headimages',
                                  default='default/default_headimage.jpg')  # 头像
    description = models.CharField(max_length=50, default='')  # 个人描述
    testornot = models.BooleanField(default=False)  # add by cby 2017-04-07 识别用户是否进行过测试，当创建了知识体系时，将其置为True

    def __str__(self):
        return self.user.username  # access user model 里面的只需通过User model即可


# 视频
class Video(models.Model):
    title = models.CharField(max_length=100, default='title')  # 标题
    video = models.FileField(upload_to='videos')  # 视频文件
    cover = models.ImageField(upload_to='covers',
                              default='default/default_headimage.jpg')  # 封面
    description = models.CharField(max_length=200, default='空')  # 描述
    uploader = models.ForeignKey(User, related_name='uploader')  # UP主

    teacher = models.CharField(max_length=5, default='空')  # 讲师 add by cby 2017-04-20
    tag = models.CharField(max_length=30, default='')  # 知识点 add by cby 2017-04-11
    difficulty = models.FloatField(default=0) #视频相对大纲难度 add by cby 2017-04-11
    quality = models.FloatField(default=0)  # 视频难度 add by cby 2017-04-28

    play = models.IntegerField(default=0)  # 播放数

    like = models.IntegerField(default=0)  # 点赞数
    like_list = models.ManyToManyField(UserExtraProfile)  # 点赞列表

    time = models.DateTimeField(auto_now=False, auto_now_add=True)  # 上传时间
    status = models.IntegerField(default=0)  # 状态——用来标记视频是否被管理员禁封

    # add by 2017-04-04
    favorite = models.IntegerField(default=0)  # 收藏数
    favorite_list = models.ManyToManyField(UserExtraProfile, related_name="favorite_list")  # 收藏列表
    # end add by cby

    def __str__(self):
        return self.title

    def get_absolute_url(self):  # ——相当于在这里给视频创建了url
        return '/video/%u' % self.pk  # pk是主码，并未在上面定义
        # 另外 video前有‘/’说明不继承之前的，没了就要继承之前的
        # 需要经视频的主码self.pk存入视频本体中，视频质量信息则从本体中取出来


# 评论
class Comment(models.Model):
    user = models.ForeignKey(User)  # 评论者
    video = models.ForeignKey(Video)  # 评论视频
    # 因为设置了多对一的关系，使得在浏览器请求视频时，
    # video会自动反向查询并将结果形成comment_set放在video中
    content = models.CharField(max_length=400)  # 内容
    cdate = models.DateTimeField(default=timezone.now)  # 评论时间，

    # 一旦创建该类的实例，cdate就保存一个当前时间，所以在创建实例时只需要将前三项赋值即可

    # ForeignKey意味着多对一
    # Comment VS User：Many To One ：一个用户可以对应多条评论，但一条评论只能对应一个用户
    # Comment VS Video：Many To One ：一个视频可以有多条评论，但一条评论只能对应一个视频
    # 感觉数据库设计很重要，尤其是梳理表与表之间的关系

    def __str__(self):
        return self.user.username


# 消息提醒 目前还没有用到，以后会用
class Notification(models.Model):
    NContent = models.CharField(max_length=50)
    NUser = models.ForeignKey(UserExtraProfile)#b不要只和UserExtraProfile关联


# 历史记录 用来记录用户的学习进度和情况add by cby 2017-04-19
class History(models.Model):
    HUser = models.ForeignKey(User)  # 该条历史执行者
    HVideo = models.ForeignKey(Video)  # 视频
    hscore = models.FloatField(default=0)  # 当时执行者打分score
    hchange = models.FloatField(default=0)  # 当时该视频对应的知识点的achieve改变量change

    hdate = models.DateTimeField(default=timezone.now)  # 历史创建的时间

    dummy = models.BooleanField(default=False)  # add by cby 2017-05-06 用来区分呢是否是拟打分

    def __str__(self):
        return self.HUser.username


# 部分学习方案的反馈 add by cby 2017-04-21
class PartFeedback(models.Model):
    PVideo = models.ForeignKey(Video)  #反馈对象视频
    PUser = models.ForeignKey(User) #该条反馈执行者
    pfeed = models.BooleanField(default=False)
    pdate = models.DateTimeField(default=timezone.now)  # 反馈时间

    def __str__(self):
        return self.PVideo.title

# 知识图谱的反馈 add by cby 2017-04-21
class GraphFeedback(models.Model):
    GUser = models.ForeignKey(User)  # 该条反馈执行者
    gfeed = models.BooleanField(default=False)
    gdate = models.DateTimeField(default=timezone.now)  # 反馈时间

    def __str__(self):
        return self.GUser.username


# 上传视频表单——这是一个表单模型，为什么要用表单呢，因为表单多了一些系统自带的验证
class VideoUploadForm(forms.ModelForm):  # 继承自forms.ModelForm 上传过来的数据先存到这个数据表中，再在视图函数中
    class Meta:
        model = Video  # 复用
        fields = ['title', 'description', 'cover', 'video', 'tag', 'difficulty', 'teacher']
        # 将Video类中的部分filed放出来让他们成为接口——当前表单的字段，限定属性


# 关于表单模型与普通模型的区别 参看http://www.cnblogs.com/hhh5460/p/4526613.html
# 当前这个模型是复用在models里已经设计好了的类Video(就是数据库的表)，利用这个类的（部分）信息
# （此例中使用了'title', 'description', 'cover', 'video', 'tag', 'category'）
# 来作为该表单的模型。复用方法就是在子类Meta中 进行model和fields的赋值

# 注册
def register(request, error_msg=""):  # 给变量先赋值个空字符串，这样就不需要外来一定要传进来参数
    if request.user.is_authenticated():  # 先验证访问者的当前状态，若已登陆 就跳回个人信息
        # 只有再逻辑出现错误时才会发生这种情况，我觉得这部分写的有点浪费，后期试试tests文件
        return HttpResponseRedirect("/homepage/")
    if request.method == 'POST':
        input_is_valid = False
        # 收集信息，未填则为空
        username = request.POST['username'] if request.POST['username'] else ""
        password1 = request.POST['password1'] if request.POST['password1'] else ""
        password2 = request.POST['password2'] if request.POST['password2'] else ""
        email = request.POST['email'] if request.POST['email'] else ""
        description = request.POST['description'] if request.POST['description'] else ""
        # 判断是否达成注册条件
        error_msg = "错误"  # 和input_is_valid一样先提前写着
        if not username:
            error_msg = "请输入用户名"
        elif not (password1 and password2):
            error_msg = "请输入密码"
        elif not email:
            error_msg = "请输入邮箱"
        elif not description:
            error_msg = "请输入个人描述"
        elif password1 != password2:
            error_msg = "两次密码不一致"
        elif len(password1) < 6:
            error_msg = "密码长度小于6位"
        elif User.objects.filter(username=username):
            error_msg = "用户名已经存在"
            username = ""  # 擦去
        elif User.objects.filter(email=email):
            error_msg = "邮箱已经注册"
            email = ""  # 擦去
        else:
            # 可注册
            input_is_valid = True
            user = User.objects.create_user(username=username,
                                            password=password1,
                                            email=email)  # 这三项是User类必需的
            user.save()
            thisProfile = UserExtraProfile(user=user,
                                           description=description)  # 怎么搞的这三项成立必填项呢？默认设置？
            thisProfile.save()
            return HttpResponseRedirect("/login/")#注册成功跳到登陆界面 以新身份登陆
            #return render(request, "glgl_app/login.html", context={"username": username})
        if not input_is_valid:
            # 注册信息有误
            return render(request, "glgl_app/register.html", {'error': error_msg,
                                                              'username': username,
                                                              'email': email})
    else:
        return render(request, "glgl_app/register.html")


# 知识点测试结果写入用户本体中
def load_test_result(request, mode, error_msg=""):
    if request.user.is_authenticated():
        if request.method == 'POST':
            user_id = "id" + str(request.user.id)# 用用户id创建实例
            graph = ontology_sparql(dataset="user", userid=user_id)
            u_profile = User.objects.get(username=request.user.username).userextraprofile#不是'UserExtraProfile' 而是userextraprofile
            #mode1、2和3都是用户本体未建立的情况才出现的,所以用户add不用update，此时用update会where查询不到任何东西
            if mode == "1":  # 快速模式 零基础
                if graph.create_user_instance():
                    if graph.add_same_achieve(0.0):
                        u_profile.testornot = True
                        u_profile.save(update_fields=['testornot'])
                        return HttpResponseRedirect("/homepage/%s/" % str(request.user.id))
                    else:
                        return render(request, "glgl_app/knowledge_test.html",
                                      context={"error_msg": "用户知识体系创建失败，请重新进行测试"})
                else:
                    return render(request, "glgl_app/knowledge_test.html",
                                  context={"error_msg": "用户知识体系创建失败，请重新进行测试"})
            elif mode == "2":
                if graph.create_user_instance():
                    if graph.add_same_achieve(0.2):
                        u_profile.testornot = True
                        u_profile.save(update_fields=['testornot'])
                        return HttpResponseRedirect("/homepage/%s/" % str(request.user.id))
                    else:
                        return render(request, "glgl_app/knowledge_test.html",
                                      context={"error_msg": "用户知识体系创建失败，请重新进行测试"})
                else:
                    return render(request, "glgl_app/knowledge_test.html",
                                  context={"error_msg": "用户知识体系创建失败，请重新进行测试"})
            elif mode == "3":
                if graph.create_user_instance():
                    if graph.add_same_achieve(1.0):
                        u_profile.testornot = True
                        u_profile.save(update_fields=['testornot'])
                        return HttpResponseRedirect("/homepage/%s/" % str(request.user.id))
                    else:
                        return render(request, "glgl_app/knowledge_test.html",
                                      context={"error_msg": "用户知识体系创建失败，请重新进行测试"})
                else:
                    return render(request, "glgl_app/knowledge_test.html",
                                  context={"error_msg": "用户知识体系创建失败，请重新进行测试"})
            elif mode == "4": #进入该模式必须是用户本体achieve属性值全为0
                results = request.POST['results']  #从request中取出来的是字符串
                if not u_profile.testornot: #判断用户是首次测试时
                    if graph.create_user_instance():  # 为用户创建用户本体实例
                        if not graph.add_same_achieve(0.0):  # 初始化用户掌握程度
                            return render(request, "glgl_app/knowledge_test.html",
                                          context={"error_msg": "用户知识体系创建失败，请重新进行测试"})
                    else:
                        return render(request, "glgl_app/knowledge_test.html",
                                      context={"error_msg": "用户知识体系创建失败，请重新进行测试"})
                if not results == "":  # 确定确实有结果传进来
                    if u_profile.testornot:#判断用户是非首次测试时
                        if graph.delete_all_achieve():#要先清除
                            if not graph.add_same_achieve(0.0):#再初始化
                                return render(request, "glgl_app/knowledge_test.html",
                                              context={"error_msg": "用户知识体系创建失败，请重新进行测试"})
                        else:
                            return render(request, "glgl_app/knowledge_test.html",
                                          context={"error_msg": "用户知识体系创建失败，请重新进行测试"})
                    results = results.split(",")  # 拆分出来是数组
                    try:
                        for knowledge in results:  # 目前knowledge是字符串
                            knowledge = knowledge.split(":")  # 变为数组 前一元素是知识点名字，后一元素为结果
                            graph.update_user_achieve(knowledge[0], float(knowledge[1]))
                        if not u_profile.testornot:
                            u_profile.testornot = True
                            u_profile.save(update_fields=['testornot'])
                        return render(request, "glgl_app/weighted_tree_user.html")
                    except:
                        return render(request, "glgl_app/knowledge_test.html",
                                      context={"error_msg": "测试结果录入失败，请重新进行测试"})
                else:
                    if not u_profile.testornot:
                        u_profile.testornot = True
                        u_profile.save(update_fields=['testornot'])
                    return render(request, "glgl_app/weighted_tree_user.html")
        else:
            return render(request, "glgl_app/knowledge_test.html",
                          context={"error_msg": "测试结果提交失败，请重新进行测试"})
    else:
        return HttpResponseRedirect("/register/")


#在前端的JS中被请求
@require_http_methods(["POST"])
def update_user_ontology(request, video_id):
    score = float(request.POST["score"])
    user_id = str(request.user.id)
    user_id = "id" + user_id  # 为用户id创建实例
    math_graph = ontology_sparql(dataset="math")#与视频相关的、demand相关的要用math
    user_graph = ontology_sparql(dataset="user", userid=user_id)#与achieve相关的要用user
    video = Video.objects.get(pk = video_id)

    rankforuser = [1.0, 0.6, 0.2, 0.0]
    #rankforvideo = [1.0, 0.6, 0.2]
    adco = [2.5, 1.5, 1]
    msg = "你的知识体系发生以下改变,请刷新学习方案查看方案是否进行了调整:"
    #step1 将该项数据源转化为用户对当前知识点的掌握程度的变化量 因此需要判断当前学习的视频难度与用户掌握程度是否匹配
    #knowledge = math_graph.search_knowledge(videoid)#取知识点 要用tag 不能在本体中查询，因为有很多知识点共用一个资源
    knowledge = video.tag
    achieve = float(user_graph.search_achieve(knowledge))#取用户等级
    difficulty = float(video.difficulty)#取视频等级
    if achieve < 0.2:
        user_rank = 3
    elif achieve < 0.6:
        user_rank = 2
    elif achieve < 1.0:
        user_rank = 1
    else:
        user_rank = 0

    if difficulty > 0.6:
        video_rank = 0
    elif difficulty > 0.2:
        video_rank = 1
    else:
        video_rank = 2

    if user_rank == 0:#已经加满了，除非学习效果是100%，否则都是退步
        if score >= 1.0:  # 若学习效果为100% 用户掌握程度不变
            return JsonResponse({'msg': "你对该知识点的掌握非常牢固，你的知识体系没有改变"})
        else:  # 若学习效果低于100% 改变用户掌握程度以匹配视频难度
            change = rankforuser[video_rank + 1] - achieve  # 先降低用户掌握程度
            change += float(score * difficulty / adco[video_rank])
            #if change == 0: 能进else里面的change都是负的 设计分值的时候 不会让学习效果不达100%的跨过整个梯度
            #    return JsonResponse({'msg': "你对该知识点的掌握非常牢固，你的知识体系没有改变"})

        # 记录用户对视频的学习情况
        if create_history(request.user.id, video_id, score, change):
            # do something 去报告给后台吧
            pass
    else:
        if (user_rank - 1) == video_rank:#用户按照方案学习
            change = score * difficulty / adco[video_rank]
        elif (user_rank - 1) > video_rank:#用户学了高难度视频
            if score >= 1.0:#若学习效果为100% 改变用户掌握程度以匹配视频难度
                change = rankforuser[video_rank + 1] - achieve#先抬高用户掌握程度 抬高的过程成程度变化量产生了
                change += score * difficulty / adco[video_rank]
            else:#若学习效果低于100%  忽视用户与视频的不同级状态 以视频难度为准选择进阶系数，将数据直接代入数据源转化公式中进行计算
                change = score * difficulty / adco[video_rank]
        else:#用户学了低难度视频
            if score >= 1.0:  # 若学习效果为100% 用户掌握程度不变
                change = 0
            else:#若学习效果低于100% 改变用户掌握程度以匹配视频难度
                change = rankforuser[video_rank + 1] - achieve#先降低用户掌握程度
                change += float(score * difficulty / adco[video_rank])

        #记录用户对视频的学习情况
        if create_history(request.user.id, video_id, score, change):
            # do something 去报告给后台吧
            pass

        if change == 0:
            if score == 0:
                return JsonResponse({'msg': "该次学习没有收获，不要放弃，继续努力！"})
            else:
                return JsonResponse({'msg': "你的知识体系未改变，请继续努力！"})

    #step2:设置扩散阈值，以及停止条件 沿着本体结构将chenge传递给其他 沿着subclass关系而不是ak和sk关系
    threshold = 0.05#以后的实验慢慢试一试来确定 先定为0.05
    loss_factor = 0.9#以后的实验慢慢试一试来确定 先定为0.9
    initiation = knowledge #扩散起始点，该系统每个视频仅对应一个知识点
    already_activated = []
    per_already_activated = []
    d = {}
    d.setdefault("name", initiation)
    d.setdefault("activation_value", change)
    already_activated.append(d)
    if change > 0:
        msg += "\n%s(+)" % knowledge
    else:
        msg += "\n%s(-)" % knowledge
    if abs(change) > threshold:#要考虑到chenge有正有负
        d.setdefault("up", True)
        d.setdefault("next", True)
        per_already_activated.append(d)
        already_activated, msg = spreading_activate(user_graph, threshold, loss_factor, already_activated, per_already_activated, msg)
    if reload_part_user_ontology(already_activated, user_graph):
        return JsonResponse({'msg': msg})
    else:
        return JsonResponse({'msg': "打分提交失败，请重试！"})

#在前端的JS中被请求
@require_http_methods(["POST"])
def update_user_ontology_silent(request, video_id):
    ratio = float(request.POST["ratio"])
    video = Video.objects.get(pk=video_id)
    history = History.objects.filter(HVideo = video, dummy = False)
    i = 0
    total = 0
    for h in history:
        i += 1
        total += h.hscore
    if total > 0:
        score = float(total / i) * ratio
        update_score(request, video_id, video, score)

def update_score(request, video_id, video, score):
    user_id = str(request.user.id)
    user_id = "id" + user_id  # 为用户id创建实例
    user_graph = ontology_sparql(dataset="user", userid=user_id)#与achieve相关的要用user

    rankforuser = [1.0, 0.6, 0.2, 0.0]
    adco = [2.5, 1.5, 1]
    msg = "你的知识体系发生以下改变,请刷新学习方案查看方案是否进行了调整:"
    #step1 将该项数据源转化为用户对当前知识点的掌握程度的变化量 因此需要判断当前学习的视频难度与用户掌握程度是否匹配
    knowledge = video.tag
    achieve = float(user_graph.search_achieve(knowledge))#取用户等级
    difficulty = float(video.difficulty)#取视频等级
    if achieve < 0.2:
        user_rank = 3
    elif achieve < 0.6:
        user_rank = 2
    elif achieve < 1.0:
        user_rank = 1
    else:
        user_rank = 0

    if difficulty > 0.6:
        video_rank = 0
    elif difficulty > 0.2:
        video_rank = 1
    else:
        video_rank = 2

    if user_rank == 0:#已经加满了，除非学习效果是100%，否则都是退步
        if score >= 1.0:  # 若学习效果为100% 用户掌握程度不变
            return True
        else:  # 若学习效果低于100% 改变用户掌握程度以匹配视频难度
            change = rankforuser[video_rank + 1] - achieve  # 先降低用户掌握程度
            change += float(score * difficulty / adco[video_rank])
            #if change == 0: 能进else里面的change都是负的 设计分值的时候 不会让学习效果不达100%的跨过整个梯度
            #    return JsonResponse({'msg': "你对该知识点的掌握非常牢固，你的知识体系没有改变"})

        # 记录用户对视频的学习情况
        if create_history(request.user.id, video_id, score, change, dummy=True):
            # do something 去报告给后台吧
            pass
    else:
        if (user_rank - 1) == video_rank:#用户按照方案学习
            change = score * difficulty / adco[video_rank]
        elif (user_rank - 1) > video_rank:#用户学了高难度视频
            if score >= 1.0:#若学习效果为100% 改变用户掌握程度以匹配视频难度
                change = rankforuser[video_rank + 1] - achieve#先抬高用户掌握程度 抬高的过程成程度变化量产生了
                change += score * difficulty / adco[video_rank]
            else:#若学习效果低于100%  忽视用户与视频的不同级状态 以视频难度为准选择进阶系数，将数据直接代入数据源转化公式中进行计算
                change = score * difficulty / adco[video_rank]
        else:#用户学了低难度视频
            if score >= 1.0:  # 若学习效果为100% 用户掌握程度不变
                change = 0
            else:#若学习效果低于100% 改变用户掌握程度以匹配视频难度
                change = rankforuser[video_rank + 1] - achieve#先降低用户掌握程度
                change += float(score * difficulty / adco[video_rank])

        #记录用户对视频的学习情况
        if create_history(request.user.id, video_id, score, change, dummy=True):
            # do something 去报告给后台吧
            pass

        if change == 0:
            if score == 0:
                return True
            else:
                return True

    #step2:设置扩散阈值，以及停止条件 沿着本体结构将chenge传递给其他 沿着subclass关系而不是ak和sk关系
    threshold = 0.05#以后的实验慢慢试一试来确定 先定为0.05
    loss_factor = 0.9#以后的实验慢慢试一试来确定 先定为0.9
    initiation = knowledge #扩散起始点，该系统每个视频仅对应一个知识点
    already_activated = []
    per_already_activated = []
    d = {}
    d.setdefault("name", initiation)
    d.setdefault("activation_value", change)
    already_activated.append(d)
    if change > 0:
        msg += "\n%s(+)" % knowledge
    else:
        msg += "\n%s(-)" % knowledge
    if abs(change) > threshold:#要考虑到chenge有正有负
        d.setdefault("up", True)
        d.setdefault("next", True)
        per_already_activated.append(d)
        already_activated, msg = spreading_activate(user_graph, threshold, loss_factor, already_activated, per_already_activated, msg)
    if reload_part_user_ontology(already_activated, user_graph):
        return True
    else:
        return True

def spreading_activate(graph, threshold, loss_factor, already_activated, per_already_activated, msg):
    waiting_to_spreading = []
    for activated in per_already_activated:
        if activated["up"]:#先向上找
            temp = graph.search_father_knowledge(activated["name"])
            if temp and (temp not in [x["name"] for x in already_activated]):#每个节点只允许被激励一次 确定父知识点存在
                weight = float(graph.search_weight(activated["name"]))
                activation_value = activated["activation_value"] * weight * loss_factor
                if abs(activation_value) > 0:#穿过去的激励值大于0才算激励了其他点，在这里是temp 也要考虑到有正有负
                    d = {}
                    d.setdefault("name", temp)
                    d.setdefault("activation_value", activation_value)
                    already_activated.append(d)
                    if activation_value > 0:
                        msg += "\n%s(+)" % temp
                    else:
                        msg += "\n%s(-)" % temp
                if abs(activation_value) > threshold:#对于父知识点 不具备传递temp 激励值大于阈值才有资格向其他点传递
                    d.setdefault("up", True)
                    d.setdefault("next", False)
                    waiting_to_spreading.append(d)
        if activated["next"]:#向下找
            temp_set = graph.search_subClass(activated["name"])
            for temp in temp_set:
                if temp not in [x["name"] for x in already_activated]:
                    weight = float(graph.search_weight(temp))
                    activation_value = activated["activation_value"] * weight * loss_factor
                    if abs(activation_value) > 0:  # 穿过去的激励值大于0才算激励了其他点，在这里是temp
                        d = {}
                        d.setdefault("name", temp)
                        d.setdefault("activation_value", activation_value)
                        already_activated.append(d)
                        if activation_value > 0:
                            msg += "\n%s(+)" % temp
                        else:
                            msg += "\n%s(-)" % temp
                    if abs(activation_value) > threshold:  # 对于temp 激励值大于阈值才有资格向其他点传递
                        d.setdefault("up", False)
                        d.setdefault("next", True)
                        waiting_to_spreading.append(d)
    if waiting_to_spreading.__len__() > 0:
        spreading_activate(graph, threshold, loss_factor, already_activated, waiting_to_spreading, msg)
    return already_activated, msg#不返回msg的话，主函数运行在该函数后，msg在这个函数里面的变化将无效
#用户观看完视频并打分，分值经过扩散激活算法传递到其他知识点后，形成知识点更新更新集合
#该函数仅内部调用

def reload_part_user_ontology(update_set, graph) -> object:
    try:
        for knowledge in update_set:
            change = knowledge["activation_value"] + float(graph.search_achieve(knowledge["name"]))
            graph.update_user_achieve(knowledge["name"], change)
        return True
    except:
        return "更新结果录入失败，请重新进行测试"

def create_history(user_id, video_id, score, change, dummy = False):
    video = Video.objects.get(pk=video_id)
    user = User.objects.get(pk = user_id)
    h = History(HUser=user, HVideo=video, hscore=score, hchange=change, dummy=dummy)  # 记录
    h.save()
    return True

# 登录 登陆以后在后台上就将authenticated user attach to the current session
def login(request, error_msg=""):
    error_msg = ''
    # 这个判断存在的作用是针对那些已登陆但又点击了登陆的请求
    if request.user.is_authenticated():
        return HttpResponseRedirect("/home/")

    # 只接受由POST传过来的登录请求，在用户唯有登陆时访问login路径时不是用的POST方式（跳入else里面），
    if request.method == 'POST':  # 用请求方式来区分请求表单和验证表单两种状态，好方法
        username = request.POST['username']
        # request.POST is a dictionary-like object that lets you access submitted data by key name
        # In this case the key is username
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        # authenticate函数：If the given credentials are valid, return a User object.身份验证，返回的是一个user对象
        if user is not None:
            if user.is_active:  # 若提交的数据验证成功，进一步确认该用户是否被管理员激活，具有“活动性”
                auth.login(request, user)
                if user.is_staff:#app系统与admin系统如何更切合，待改
                    return HttpResponseRedirect("/")
                else:
                      # 这个login函数是系统的 将用户（即user对象）传递进去之后的事情就不要管了
                    # 该函数的结果就是该用户attach进session中了，而且现在的状态变成了authenticated
                    # add by cby 2017.02.25  return HttpResponseRedirect("/home/")登陆成功后跳转到信息页面使用起来怪怪的
                    if user.userextraprofile.testornot:  # 已进行过测试
                        return HttpResponseRedirect("/homepage/" + str(user.id))
                    else:
                        return HttpResponseRedirect("/testmode/")
                        # end add
            else:
                error_msg = '该用户无法正常使用'
                return render(request, "glgl_app/login.html", {'username': username, 'error_msg': error_msg})
        else:
            error_msg = '用户名或密码错误'
            return render(request, "glgl_app/login.html", {'username': username, 'error_msg': error_msg})
    else:
        return render(request, "glgl_app/login.html")


# 登出
def logout(request):
    auth.logout(request)
    # 系统自带的logout，It takes an HttpRequest object and has no return value.
    return render(request, "glgl_app/logout.html")


# 个人信息
"""
这里有一项重要的改动，那就是用户知识体系信息的计算得出，
但是profile并不是唯一需要用户知识体系的地方，测试环节也需要
"""


def profile(request, error_msg=''):
    if request.user.is_authenticated():  # 正式修改个人信息之前惯例先确认当前用户是登录状态，即以验证了
        if request.method == 'POST':
            # 收集信息，若无则空
            #username = request.POST['username']
            password = request.POST['password'] if request.POST['password'] else ""
            headimage = request.FILES['headimage'] if request.FILES['headimage'] else ""
            description = request.POST['description'] if request.POST['description'] else ""
            user = auth.authenticate(username=request.user.username, password=password)
            if user is not None:
                if user.is_active:
                    input_is_valid = False  # 在验证结束之前 这个flag要置为False
                    if not description:  # 当个人描述为空时
                        error_msg = "请输入个人描述"  # ——不要
                    # 不检查头像 是因为form自动帮我们？以上两步就是使得我们在admin界面上一旦修改就必须全部填写的原因吗
                    else:
                        # 调整个人信息
                        input_is_valid = True  # 前面几项过去 说明用户提交的表单内容全面且合法，
                        # 此时这个flag可以置为True了。然后开始保存表单数据到数据库
                        profile = user.userextraprofile
                        profile.headimage = headimage
                        profile.description = description
                        profile.save()  # 若干项全部送入缓冲区后在一次性save
                        return render(request, "glgl_app/profile.html", {'context': '信息更改成功'})
                    if not input_is_valid:
                        return render(request, "glgl_app/profile.html", {'context': error_msg})
                else:
                    error_msg = '该用户无法正常使用'
                    return render(request, "glgl_app/profile.html", {'context': error_msg})
            else:
                error_msg = '密码错误'
                return render(request, "glgl_app/profile.html", {'context': error_msg})
        else:
            return render(request, "glgl_app/profile.html")
    else:
        return render(request, "glgl_app/notlogin.html")


# 重设密码——留着
def setPassword(request, error_msg=""):
    if request.user.is_authenticated():
        if request.method == 'POST':
            input_is_valid = False
            password = request.POST['password'] if request.POST['password'] else ""
            newpassword1 = request.POST['newpassword1'] if request.POST['newpassword1'] else ""
            newpassword2 = request.POST['newpassword2'] if request.POST['newpassword2'] else ""
            # 判断是否达成重设条件
            error_msg = "错误"
            if not password:
                error_msg = "请输入原密码"
            elif not newpassword1:
                error_msg = "请输入新密码"
            elif not newpassword2:
                error_msg = "请确认新密码"
            elif newpassword1 != newpassword2:
                error_msg = "两次密码不一致"
            elif len(newpassword1) < 6:
                error_msg = "密码长度小于6位"
            elif request.user.check_password(password) == False:
                error_msg = "密码错误"
            else:
                # 可重设
                input_is_valid = True
                request.user.set_password(newpassword1)  # .set_password调用django提供的函数
                request.user.save()  # 读写了数据库，需要保存一下
                return HttpResponseRedirect("/setpassword-suc")  # 重定向，提示重置成功，用JS更好点 后期再说
            if not input_is_valid:
                return render(request, "glgl_app/setpassword.html", {'error': error_msg})
        else:
            return render(request, "glgl_app/setpassword.html")
    else:
        error_msg = "请先登录"
        return render(request, "glgl_app/login.html", {'error_msg': error_msg})


# 上传视频
@require_http_methods(["GET", "POST"])
def upload(request):
    if request.user.is_authenticated():
        if request.method == 'GET':
            return render(request, 'glgl_app/upload.html',
                          {'form': VideoUploadForm(initial={'title': "",
                                                            'description': "",
                                                            'teacher': "",
                                                            'tag': "",
                                                            'demand': "",
                                                            'difficulty': ""})})
            # Form.initial 在表单未绑定的情况下，为表单字段设置初始值 eg:f=ContactForm(initial={'subject':'Hi there'})
        else:
            # 上传视频条件达成
            form = VideoUploadForm(request.POST, request.FILES)  # 将包含了VideoUploadForm表单中字段的东西全都传进去
            # 自己对号入座，形成表单实例
            if form.is_valid():  # 表单再提交前check来一下，要django系统再来一遍？系统验证什么？
                """is_valid()：
                Returns True if the form has no errors. Otherwise, False. If errors are
                being ignored, returns False.
                """
                video = form.save(commit=False)  # 将表单对象赋值给video，但并不向数据库真正提交数据
                # video与form是什么关系：form复用了video的一部分

                if not request.user.is_staff:# 管理员上传的视频无需审核
                    video.status = 4
                video.uploader = request.user  # 表单form中没有
                video.save()  # 向数据库提交基本信息
                form.save_m2m()  # 保存关联信息：由于之前使用了commit=False，影响了关联信息的保存，所以这里需要调用form.save_m2m()
                if request.user.is_staff:
                    graph = ontology_sparql()
                    if not create_video_ontology_instance(graph, video.tag, video.difficulty, video.id, already = []):
                        return render(request, 'glgl_app/upload.html', {'error': form.errors, 'form': form})
                    return render(request, 'glgl_app/upload.html',
                                  {'form': VideoUploadForm(initial={'title': "",
                                                                    'description': "",
                                                                    'teacher': "",
                                                                    'tag': "",
                                                                    'demand': "",
                                                                    'difficulty': ""})})
                return render(request, 'glgl_app/upload_success.html')
            else:
                # 表单有误
                return render(request, 'glgl_app/upload.html', {'error': form.errors, 'form': form})
                # form.errors:"Returns an ErrorDict for the data provided for the form"
    else:
        # 未登录
        return render(request, "glgl_app/login.html", {'error': "请登陆"})


def audit_pass_video(request, video_id):
    if request.user.is_authenticated():
        if request.method == 'GET':
            return render(request, 'glgl_app/video/%s.html' % video_id)
        else:
            if request.user.is_staff:
                video = Video.objects.get(pk = video_id) # 将表单对象赋值给video，但并不向数据库真正提交数据
                video.status = 0
                video.title = request.POST["title"]#管理员可以修改这三项视频信息
                video.tag = request.POST["tag"]
                video.difficulty = request.POST["difficulty"]
                video.teacher = request.POST["teacher"]
                video.save()  # 保存管理员修改过的视频信息
                #管理员审核通过后，就可以创建资源本体实例了
                graph = ontology_sparql()
                if create_video_ontology_instance(graph, video.tag, video.difficulty, video_id):
                    return JsonResponse({'msg': "操作成功！"})
                else:
                    return JsonResponse({'msg': "操作失败！"})
            else:
                return JsonResponse({'msg': "请以管理员身份操作！"})
                # form.errors:"Returns an ErrorDict for the data provided for the form"
    else:
        # 未登录 待改
        return JsonResponse({'msg': "请以管理员身份登陆！"})
#管理员在管理界面，查看视频，主要信息包括视频标题、tag、difficulty 可修改 审核通过后，创建资源本体实例

def create_video_ontology_instance(graph, tag, difficulty, video_id, already = []):
    if create_video_ontology_instance_cell(graph, tag, difficulty, video_id):
        already.append(tag)
        father = graph.search_father_knowledge(tag)
        if father and father not in already:
            if not create_video_ontology_instance(graph, father, difficulty, video_id, already=already):
                return False

        equivalent = graph.search_equivalent_knowledge(tag)
        if equivalent:
            for equi in equivalent:
                if equi not in already:
                    if not create_video_ontology_instance(graph, equi, difficulty, video_id, already=already):
                        return False
        return True
    else:
        return False

def create_video_ontology_instance_cell(graph, tag, difficulty, video_id):
    if graph.create_video_instance(tag, "id_" + str(video_id)):#可以用: _但不能用#
        if graph.add_video_difficulty("id_" + str(video_id), float(difficulty)):
            if graph.add_video_quality("id_" + str(video_id), 0.0):
                return True
            else:
                return False
        else:
            return False
    else:
        return False