from django.db import models


class Item(models.Model):
    """
    Model stores information about an item
    """
    name = models.CharField(verbose_name='Название', max_length=255)
    image = models.ImageField(verbose_name='Изображение', upload_to='items')
    selling_price = models.IntegerField(verbose_name='Цена продажи')
    chance_price = models.IntegerField(verbose_name='Цена для расчёта шансов')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'


class Grade(models.Model):
    """
    Model represents grade of a case
    """
    name = models.CharField(verbose_name='Название', max_length=255)
    image = models.ImageField(verbose_name='Изображение', upload_to='grades', null=True, blank=True)
    min_lvl = models.IntegerField(verbose_name='Минимальный уровень')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Уровень кейса'
        verbose_name_plural = 'Уровни кейсов'


class Case(models.Model):
    """
    Model stores information about a case
    """
    name = models.CharField(verbose_name='Название', max_length=255)
    grade = models.ForeignKey('Grade', verbose_name='Качество', on_delete=models.PROTECT)
    avg_win = models.IntegerField(verbose_name='Средний выигрыш')

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
    chance = models.DecimalField(verbose_name='Вероятность выпадения', max_digits=6, decimal_places=3)
    item = models.ForeignKey('Item', verbose_name='Предмет', on_delete=models.CASCADE)
    case = models.ForeignKey('Case', verbose_name='Кейс', on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.item.name} from {self.case.name}"

    class Meta:
        verbose_name = 'Предмет в кейсе'
        verbose_name_plural = 'Предметы в кейсах'


class OwnedCase(models.Model):
    """
    Model stores information about users cases
    """
    case = models.ForeignKey('Case', verbose_name='Кейс', on_delete=models.CASCADE)

    # owner = models.ForeignKey('User', on_delete=models.PROTECT)
    owner = models.IntegerField(verbose_name='Владелец')

    date_owned = models.DateTimeField(verbose_name='Дата получения', auto_now_add=True)
    date_opened = models.DateTimeField(verbose_name='Дата открытия', null=True, blank=True)
    item = models.ForeignKey('Item', verbose_name='Выпавший предмет', on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return f"{self.case.name} for {self.owner}"

    class Meta:
        verbose_name = 'Кейс пользователя'
        verbose_name_plural = 'Кейсы пользователей'
