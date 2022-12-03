from django import forms
from django.db.models import Max
from django.forms import ValidationError
from psycopg2 import DataError
from accaunts.models import CustomUser, Level
from psycopg2.extras import NumericRange


class UserEditName(forms.ModelForm):
    """Форма для изменении имени в profil пользователя"""
    username = forms.CharField(max_length=20, widget=forms.TextInput(
        attrs={'class': "form__input form profile-settings__name", 'type': "text", }))

    class Meta:
        model = CustomUser
        fields = 'username',


class LevelForm(forms.ModelForm):
    """Форма для работы с уровнями, добавляющая поле для увеличения количества опыта до следующего уровня"""
    experience_to_add = forms.IntegerField(label='Изменить опыт для получения следующего уровня на', initial=0)

    def __init__(self, *args, **kwargs):
        super(LevelForm, self).__init__(*args, **kwargs)

        if self.initial.get('level') == '' or self.initial.get('level') is None:

            last_level = Level.objects.aggregate(Max('level'))
            init_level = 1
            init_range = NumericRange(0, 1000)

            if last_level:
                last_level_val = last_level['level__max']
                last_range = Level.objects.get(level=last_level_val)

                init_level = last_level_val + 1
                upper = last_range.experience_range.upper if last_range.experience_range.upper else 0
                init_range = NumericRange(
                    upper, 
                    upper + 1000
                )

            self.initial['level'] = init_level
            self.initial['experience_range'] = init_range
        elif self.initial.get('level') == 0:
            if not self.initial['experience_range']:
                init_range = NumericRange(
                    0, 
                    0
                )
                self.initial['experience_range'] = init_range
            


    def save(self, commit=True):
        super().save(commit)
        experience_to_add = self.cleaned_data.get('experience_to_add', 0)
        if experience_to_add != 0:
            lower = self.instance.experience_range.lower if self.instance.experience_range.lower else 0
            upper = self.instance.experience_range.upper if self.instance.experience_range.upper else 0
            new_experience_range = NumericRange(
                lower, 
                upper + experience_to_add
            )

            if new_experience_range.lower >= new_experience_range.upper:
                raise DataError('Неправильно указано изменение значения опыта для получения уровня.')

            levels = list(
                Level.objects.filter(experience_range__fully_gt=self.instance.experience_range) \
                    .order_by('experience_range')
            )

            self.instance.experience_range = new_experience_range

            if levels:
                # Обновляется количество опыта для получения следующего уровня для текущего и всех последующих
                # уровней.
                # Если опыт добавляется, то каждый следующий уровень также требует больше опыта (то же количество).
                # Если опыт отнимается, то это происходит только для текущего уровня
                coef = 1 if experience_to_add > 0 else 0

                new_experience_range = NumericRange(
                    self.instance.experience_range.upper, 
                    self.instance.experience_range.upper \
                        + levels[0].experience_range.upper - levels[0].experience_range.lower \
                        + experience_to_add * 2 * coef
                )
                levels[0].experience_range = new_experience_range

                for i, level in enumerate(levels[1:], start=0):
                    new_experience_range = NumericRange(
                        levels[i].experience_range.upper,
                        levels[i].experience_range.upper \
                            + level.experience_range.upper - level.experience_range.lower \
                            + experience_to_add * (i + 3) * coef
                    )
                    level.experience_range = new_experience_range

                Level.objects.bulk_update(levels, ['experience_range'])
            else:
                self.instance.save()

        return self.instance

    class Meta:
        model = Level
        fields = ['level', 'experience_range', 'experience_to_add', 'case', 'amount', 'img_name']

    
