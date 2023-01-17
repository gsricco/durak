from django.db import models


class Item(models.Model):
    """
    Model stores information about an item
    """
    ITEM_CHOICES = (
        ('dollar', 'Dollar'),
        ('smile_bear', 'Bear'),
        ('smile_robot', 'Robot'),
        ('smile_vampire', 'Vampire'),
        ('smile_unicorn', 'Unicorn'),
        ('smile_lion', 'Lion'),
        ('smile_gnome', 'Gnome'),
        ('smile_rat', 'Rat'),
        ('smile_bull', 'Bull'),
        ('smile_card_warm', 'PockerCard'),
        ('smile_card_cold', 'RussianStyle'),# не нашёл в svg картинку
    )
    name = models.CharField(verbose_name='Название', max_length=255, unique=True)
    image = models.CharField(verbose_name='Изображение', max_length=50, default='amber_case', choices=ITEM_CHOICES)
    selling_price = models.PositiveIntegerField(verbose_name='Цена продажи', default=0)
    # chance_price = models.PositiveIntegerField(verbose_name='Цена для расчёта шансов', null=True,blank=True,default=0 )
    is_money = models.BooleanField(verbose_name='Предмет является кредитами', default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'


class Case(models.Model):
    """
    Model stores information about a case
    """
    CASE_CHOICES = (
        ('amber_case', 'Amber'),
        ('pearl_case', 'Pearl'),
        ('rubin_blue', 'Sapphire'),
        ('rubin_green', 'Emerald'),
        ('rubin_purple', 'Amethist'),
        ('rubin_red', 'Rubin'),
        ('rubin_turquoise', 'Diamond'),
    )
    name = models.CharField(verbose_name='Название', max_length=255)
    image = models.CharField(verbose_name='Изображение', max_length=50, default='amber_case', choices=CASE_CHOICES)
    user_lvl_for_open = models.PositiveIntegerField(verbose_name='Минимальный уровень открытия',null=True,blank=True)
    # grade = models.ForeignKey('Grade', verbose_name='Качество', on_delete=models.PROTECT)
    # avg_win = models.PositiveIntegerField(verbose_name='Средний выигрыш')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Кейс'
        verbose_name_plural = 'Кейсы'


class ItemForCase(models.Model):
    """
    Model stores information about an item in the specific case
    It creates many-to-many relation between Item and Case taking into account a chance of dropping an item
    """
    chance = models.DecimalField(verbose_name='Шанс', null=True,blank=True, max_digits=6, decimal_places=3 )
    item = models.ForeignKey('Item', verbose_name='Предмет', on_delete=models.CASCADE)
    case = models.ForeignKey('Case', verbose_name='Кейс', on_delete=models.PROTECT)

    def __str__(self):
        return f"<{self.item.name}> из кейса <{self.case.name}>"

    class Meta:
        verbose_name = 'Предмет в кейсе'
        verbose_name_plural = 'Предметы в кейсах'


class OwnedCase(models.Model):
    """
    Model stores information about users cases
    """
    case = models.ForeignKey('Case', verbose_name='Кейс', on_delete=models.PROTECT)
    owner = models.ForeignKey('accaunts.CustomUser', verbose_name='Владелец', on_delete=models.CASCADE)
    date_owned = models.DateTimeField(verbose_name='Дата выдачи', auto_now_add=True)
    date_opened = models.DateTimeField(verbose_name='Дата открытия', null=True, blank=True)
    item = models.ForeignKey('Item', verbose_name='Выпавший предмет', on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        # return f"{self.case.name}<{self.pk}> для {self.owner} выдан {self.date_owned}"
        return ''

    class Meta:
        verbose_name = 'Выданный кейс'
        verbose_name_plural = 'Выданные кейсы'
