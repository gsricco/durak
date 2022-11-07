from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import CustomUser, Level, UserAgent, DetailUser, ReferalUser, ReferalCode, GameID, Ban, UserIP
from django.contrib.auth.models import Group


# class DetailUserInline(admin.TabularInline):
#     model = DetailUser
class UserAgentInline(admin.TabularInline):
    model = UserAgent
    extra = 0


class UserIPInline(admin.TabularInline):
    model = UserIP
    extra = 0


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = 'usernameinfo', 'preview', 'user_info', 'email', 'vk_url',
    search_fields = 'usernameinfo',
    inlines = [UserAgentInline, UserIPInline]
    readonly_fields = 'preview',

    def preview(self, obj):
        return mark_safe(f'<img src="{obj.avatar.url}" width="50" height="50">')

    preview.short_description = 'Аватар'


# @admin.register(UserAgent)
# class UserAgentAdmin(admin.ModelAdmin):
#     list_display = 'user', 'useragent'
#
#
# @admin.register(UserIP)
# class UserIPAdmin(admin.ModelAdmin):
#     list_display = 'user', 'userip'


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = 'level', 'experience_for_lvl', 'image', 'preview'
    list_editable = 'experience_for_lvl', 'image'
    list_filter = 'level',
    search_fields = 'level',
    readonly_fields = 'preview',

    def preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50">')
        else:
            return 'Нет аватара'

    preview.short_description = 'Аватар'


admin.site.unregister(Group)
admin.site.register(DetailUser)
admin.site.register(ReferalUser)
admin.site.register(ReferalCode)
admin.site.register(GameID)
admin.site.register(Ban)
