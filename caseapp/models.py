from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=255)
    selling_price = models.IntegerField()
    chance_price = models.IntegerField()


class Grade(models.Model):
    name = models.CharField(max_length=255)
    min_lvl = models.IntegerField()


class Case(models.Model):
    name = models.CharField(max_length=255)
    grade = models.ForeignKey('Grade', on_delete=models.PROTECT)
    number_of_cases = models.IntegerField()
    avg_win = models.IntegerField()


class ItemForCase(models.Model):
    chance = models.DecimalField(max_digits=6, decimal_places=3)
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    case = models.ForeignKey('Case', on_delete=models.PROTECT)


class OwnedCase(models.Model):
    case = models.ForeignKey('Case', on_delete=models.CASCADE)

    # owner = models.ForeignKey('User', on_delete=models.PROTECT)
    owner = models.IntegerField()

    date_owned = models.DateTimeField(auto_now_add=True)
    date_opened = models.DateTimeField(null=True)
    item = models.ForeignKey('Item', on_delete=models.PROTECT)
