from django.db import models


class Item(models.Model):
    """
    Model stores information about an item
    """
    name = models.CharField(verbose_name='Название', max_length=255)
    image = models.ImageField(verbose_name='Изображение', upload_to='items', null=True, blank=True)
    selling_price = models.PositiveIntegerField(verbose_name='Цена продажи', default=0)
    chance_price = models.PositiveIntegerField(verbose_name='Цена для расчёта шансов', default=0)
    is_money = models.BooleanField(verbose_name='Предмет является кредитами', default=False)

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
    image = models.ImageField(verbose_name='Изображение', upload_to='grades/img/', null=True, blank=True)
    min_lvl = models.PositiveIntegerField(verbose_name='Минимальный уровень')

    def __str__(self):
        return f"{self.name}, минимальный уровень: {self.min_lvl}"

    class Meta:
        verbose_name = 'Уровень кейса'
        verbose_name_plural = 'Уровни кейсов'


class Case(models.Model):
    """
    Model stores information about a case
    """
    name = models.CharField(verbose_name='Название', max_length=255)
    grade = models.ForeignKey('Grade', verbose_name='Качество', on_delete=models.PROTECT)
    avg_win = models.PositiveIntegerField(verbose_name='Средний выигрыш')

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
        return f"<{self.item.name}> из кейса <{self.case.name}>"

    class Meta:
        verbose_name = 'Предмет в кейсе'
        verbose_name_plural = 'Предметы в кейсах'


class OwnedCase(models.Model):
    """
    Model stores information about users cases
    """
    case = models.ForeignKey('Case', verbose_name='Кейс', on_delete=models.PROTECT)

    owner = models.ForeignKey('accaunts.CustomUser', verbose_name='Владелец', on_delete=models.PROTECT)

    date_owned = models.DateTimeField(verbose_name='Дата получения', auto_now_add=True)
    date_opened = models.DateTimeField(verbose_name='Дата открытия', null=True, blank=True)
    item = models.ForeignKey('Item', verbose_name='Выпавший предмет', on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return f"{self.case.name}<{self.pk}> для {self.owner}"

    class Meta:
        verbose_name = 'Выданный кейс'
        verbose_name_plural = 'Выданные кейсы'


class Reward(models.Model):
    level = models.ForeignKey('accaunts.Level', verbose_name='Уровень', on_delete=models.CASCADE)
    case = models.ForeignKey('Case', verbose_name='Кейс', on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(verbose_name='Количество кейсов', default=1)

    def __str__(self) -> str:
        return f"Кейс <{self.case.name}> ({self.amount} ед.) на уровне {self.level.level}"

    class Meta:
        verbose_name = 'Награды на уровне'
        verbose_name_plural = 'Награды на уровнях'


class GivenReward(models.Model):
    reward = models.ForeignKey('Reward', verbose_name='Награда на уровне', on_delete=models.PROTECT)
    user = models.ForeignKey('accaunts.CustomUser', verbose_name='Пользователь', on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name='Дата выдачи', auto_now_add=True)

    def save(self, *args, **kwargs):
        # метод save не вызывается, когда объекты создаются через bulk_create
        # при добавлении награды за уровень из админки, сразу произойдёт начисление кейсов
        self.give_rewards(save_immediately=True)
        return super().save(*args, **kwargs)

    def give_rewards(self, save_immediately: bool=False) -> list:
        """Начисляет связанному пользователю награду из связанного объекта Reward

        Args:
            save_immediately (bool, optional): Сохранять начисленные кейсы в БД внутри метода или нет. Defaults to False.

        Returns:
            list: список с объектами начисленных кейсов
        """
        # Список с начисленными кейсами
        owned_cases = []
        for _ in range(self.reward.amount):
            # создаёт начисление кейса и закидывает в список
            new_owned_case = OwnedCase(case=self.reward.case, owner=self.user)
            owned_cases.append(new_owned_case)

        print(f"Give reward to user: {self}")

        # сохраняет начисленные кейсы в БД
        if save_immediately and owned_cases:
            OwnedCase.objects.bulk_create(owned_cases)

        # возвращает начисленные кейсы (если их нужно будет сохранить позже, в одном bulk_create с другими, например)
        return owned_cases

    def __str__(self):
        return f"Награда <{self.reward}> для пользователя <{self.user.pk}>:<{self.date}>"

    class Meta:
        verbose_name = 'Выданная награда за уровень'
        verbose_name_plural = 'Выданные награды за уровни'
