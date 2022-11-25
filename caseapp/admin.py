from django.contrib import admin
from .models import Case, OwnedCase, Item, ItemForCase, Grade

admin.site.register(Case)
admin.site.register(OwnedCase)
admin.site.register(Item)
admin.site.register(ItemForCase)
admin.site.register(Grade)
# admin.site.register(Reward)
# admin.site.register(GivenReward)
