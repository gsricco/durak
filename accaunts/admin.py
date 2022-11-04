from django.contrib import admin
from .models import CustomUser, Level, UserAgent, DetailUser, ReferalUser, ReferalCode, GameID, Ban


# @admin.register(CustomUser)
# class CustomUserAdmin(admin.ModelAdmin):
#     list_display = 'username', 'experience', 'level', 'balance', 'email', 'ban'
#     list_editable = 'ban',
#     list_filter = 'ban',
#     search_fields = 'username',


admin.site.register(CustomUser)
admin.site.register(UserAgent)
admin.site.register(DetailUser)
admin.site.register(ReferalUser)
admin.site.register(ReferalCode)
admin.site.register(GameID)
admin.site.register(Ban)

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = 'level', 'experience_for_lvl', 'image'
    list_editable = 'experience_for_lvl', 'image'
    list_filter = 'level',
    search_fields = 'level',
