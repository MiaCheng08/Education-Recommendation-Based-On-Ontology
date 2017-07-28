from django.conf.urls import url,include

from .import views
from .import models
from .import video
from .import search
from .import knowledge

from django.conf import settings
from django.conf.urls.static import static

from apscheduler.schedulers.background import BackgroundScheduler

def update_video_quality():
    graph = knowledge.ontology_sparql()
    videos = models.Video.objects.filter(status = 0)
    total_play = 0#用来归一化
    total_like = 0  # 用来归一化
    total_favorite = 0  # 用来归一化
    for v in videos:
        total_play += v.play
        total_like += v.like
        total_favorite += v.favorite
    for v in videos:
        try:
            play_num = float(v.play / total_play)
        except ZeroDivisionError:
            play_num = 0
        try:
            like_num = float(v.like / total_like)
        except ZeroDivisionError:
            like_num = 0
        try:
            favorite_num = float(v.like / total_favorite)
        except ZeroDivisionError:
            favorite_num = 0
        quality = float(play_num * 0.35 + like_num * 0.25 + favorite_num * 0.4)
        if quality > 0:
            #更新本体
            graph.update_video_quality("id_" + str(v.id), round(quality, 2))
            #更新关系数据库
            v.quality = round(quality, 2)
            v.save()

scheduler = BackgroundScheduler()
#This will get you a BackgroundScheduler with a MemoryJobStore named
#“default” and a ThreadPoolExecutor named “default” with a default maximum thread count of 10.
scheduler.add_job(update_video_quality, 'interval', seconds=600)
scheduler.start()

urlpatterns = [
    # ex:/
    url(r'^$', views.index, name='index'),
    #管理员首页，即今日统计
    #url(r'^adminindex/$', views.admin_index),  # add by cby 2017-04-14

    url(r'^getfeedbackdata/$', views.get_feedback_data),  # add by cby 2017-04-22

    #完整的学习方案
    url(r'^allpath/$', views.all_path),  # add by cby 2017-03-31

    url(r'^graphfeed/$', views.graph_feed),  # add by cby 2017-04-21
    # ex:/videoset/
    url(r'^videoset/$', views.video_set),
    # ex:/register/
    url(r'^register/', models.register, name='register'),
    # ex:/login/
    url(r'^login/', models.login, name='login'),
    # ex:/logout/
    url(r'^logout/', models.logout, name='logout'),
    # ex:/homepage/history
    #url(r'^homepage/(?P<user_id>[0-9]+)/', views.homepage),
    url(r'^homepage/(?P<user_id>[0-9]+)/', include([
        url(r'^$', views.homepage),
        url(r'^history/$', views.history),
    ])),# add by cby 2017-04-19

    # ex:/home/ 提供用户查看自己的信息并可以修改
    url(r'^home/', views.home, name='home'),
    # ex:/profile/
    url(r'^profile/', models.profile),

    url(r'^video/(?P<video_id>[0-9]+)/', include([
        url(r'^$', video.video_play),
        url(r'^auditpassvideo/$', models.audit_pass_video),  # add by cby 2017-04-13
        url(r'^unblockvideo/$', video.video_unblock),
        url(r'^banvideo/$', video.video_ban),
        url(r'^likethis/$', video.like),
        url(r'^favoritethis/$', video.favorite),
        # 以上三个通过js调用，当情况是：即使是使用JS，在django的MTV模式中没有模板，
        # 但是仍需要urls来指向一个后端脚本view来承担运算
        url(r'^morecomments/$', views.more_comments),
        url(r'^showpartpath/$', views.show_part_path),  # add by cby 2017-04-05
        url(r'^updateuserontology/$', models.update_user_ontology),  # add by cby 2017-04-17
        url(r'^updateuserontologysilent/$', models.update_user_ontology_silent),  # add by cby 2017-05-06
        url(r'^partfeed/$', video.part_feed),  # add by cby 2017-04-21
    ])),#上面这些放在了include里面的函数，在调用视图函数时，和继承并捕获前面路径的video_id值，一并传入视图函数中

    url(r'^send-comment/$', video.video_comment_add),#放到上面的include里面比较合理吧

    url(r'^upload/$', models.upload),
    # ex:/about/
    url(r'^about/', views.aboutus, name='about'),

    url(r'^setpassword/', models.setPassword),

    url(r'^setpassword-suc/', views.setPasswordSuc),

    #url(r'(?P<video_id>[0-9]+)/morecomments/$', views.more_comments),

    url(r'^search/', search.search),

    url(r'^check/', views.checkpage),#查看待审核视频

    url(r'^banvideo/', views.banpage),#查看已封禁的视频

#以下两个是由前端的JS请求来的
    url(r'^showtree/$', views.showtree),#add by cby 2017-03-24

    url(r'^showallpath/$', views.show_all_path),  # add by cby 2017-04-10

#知识点测试相关路径
    #注册成功之初，提供两种测试方式
    url(r'^testmode/$', views.testmode),  # add by cby 2017-04-07

    #用户非首次进行知识点测试，只能进行精确知识点测试
    url(r'^knowledge_test/$', views.knowledge_test),  # add by cby 2017-04-06

    #由前端的JS请求来的
    url(r'^getallknowledge/$', views.get_all_knowledge),  # add by cby 2017-04-06

    url(r'^getknowledgenodummy/$', views.get_knowledge_no_dummy),  # add by cby 2017-05-02
    #由前端的JS请求来的 无论是哪一种测试方式，最终都将结果提交到此处进行用户掌握程度的录入
    url(r'^submittestresults/(?P<mode>[0-9]+)/$', models.load_test_result),  # add by cby 2017-04-06

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# This helper function works only in debug mode and only if the given prefix is local
# (e.g. /media/) and not a URL (e.g. http://media.example.com/).
"""
url(r'^homepage/(?P<user_id>[0-9]+)/', include([
    url(r'^$', views.homepage)
])),  # 在这里为什么不直接调用views.homepage呢
"""