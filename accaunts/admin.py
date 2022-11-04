from django.contrib import admin
from .models import CustomUser, Level, UserAgent, DetailUser, ReferalUser, ReferalCode, GameID, Ban
from django.contrib.auth.models import Group


class DetailUserInline(admin.TabularInline):
    model = DetailUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = 'username', 'email',
    search_fields = 'username',
    inlines = [DetailUserInline, ]



@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = 'level', 'experience_for_lvl', 'image'
    list_editable = 'experience_for_lvl', 'image'
    list_filter = 'level',
    search_fields = 'level',




admin.site.unregister(Group)
# admin.site.register(CustomUser)
admin.site.register(UserAgent)
# admin.site.register(DetailUser)
admin.site.register(ReferalUser)
admin.site.register(ReferalCode)
admin.site.register(GameID)
admin.site.register(Ban)