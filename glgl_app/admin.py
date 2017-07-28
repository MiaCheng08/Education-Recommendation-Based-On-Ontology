from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import *

# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class UserExtraProfileInline(admin.StackedInline):
    model = UserExtraProfile
    can_delete = False
    verbose_name = 'Extra Personal Info'
    verbose_name_plural = 'Extra Personal Infos'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserExtraProfileInline,)

class HistoryAdmin(admin.ModelAdmin):
    list_display = ['HUser', 'hdate', 'HVideo', 'hscore', 'hchange', 'dummy']

class PartFeedbackAdmin(admin.ModelAdmin):
    list_display = ['PVideo', 'PUser', 'pdate', 'pfeed']

class GraphFeedbackAdmin(admin.ModelAdmin):
    list_display = ['GUser', 'gdate', 'gfeed']
# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.register(Video)#因为register函数的参数限制到2个，所以干脆一个一个来
admin.site.register(Notification)
admin.site.register(Comment)
admin.site.register(History, HistoryAdmin)
admin.site.register(PartFeedback, PartFeedbackAdmin)
admin.site.register(GraphFeedback, GraphFeedbackAdmin)
"""
开源代码原本的代码 我依照官网改了改 2017.02.26
from django.contrib import admin
from .models import *

admin.AdminSite.site_header = 'Giligili' # 在admin界面最上面显示的文字
admin.site.register(Video)
admin.site.register(Notification)
admin.site.register(Comment)
admin.site.register(UserExtraProfile)

now that we've registered Video、Notification、Comment和UserExtraProfile
Django knows that it should be displayed on the admin index page
"""

