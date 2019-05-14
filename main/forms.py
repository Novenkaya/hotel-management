from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from payment.models import CheckIn
from .models import Staff, Room
from .widgets import MySplitDateTime, FilteredSelectMultiple


class Signup(forms.Form):
    """
    Бұл тіркеу нысаны.
    """
    error_messages = {
        'password_mismatch': _("Два поля пароля не совпадают."),
        'id_not_found': _("Этот идентификатор недоступен."),
        'info_not_matched': _("Информация несовместима."),
        'username_exists': _("Имя пользователя уже существует."),
        'staff_username_exists': _("Эти сотрудники имеют учетную запись, к которой можно получить доступ."),
    }

    staff_id = forms.IntegerField(
        label=_('ID'),
        help_text=_("Введите код вашего сотрудника"),
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Введите свой идентификатор'),
            }
        )
    )
    first_name = forms.CharField(
        label=_("Аты"),
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Пожалуйста, введите ваше имя'),
            }
        )
    )
    middle_name = forms.CharField(
        label=_('Имя отца'),
        required=False,
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Пожалуйста, введите ваше имя'),
            }
        )
    )
    last_name = forms.CharField(
        label=_("Фамилия"),
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Введите свою фамилию'),
            }
        )
    )
    contact_no = forms.CharField(
        label=_('контакт'),
        max_length=15,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Введите номер контакта'),
            }
        )
    )
    email = forms.EmailField(
        label=_("Электронная почта"),
        max_length=50,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Пожалуйста, введите ваш адрес электронной почты'),
            }
        )
    )
    username = forms.CharField(
        label=_("имя пользователя"),
        max_length=32,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('имя пользователя'),
            }
        )
    )
    password1 = forms.CharField(
        label=_("пароль"),
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('пароль')
            }
        )
    )
    password2 = forms.CharField(
        label=_("Подтвердите ваш пароль"),
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Подтвердите ваш пароль')
            }
        ),
        help_text=_("Введите пароль выше, чтобы проверить."))

    def clean(self):
        staff_id = self.cleaned_data.get('staff_id')
        first_name = self.cleaned_data.get('first_name')
        middle_name = self.cleaned_data.get('middle_name')
        last_name = self.cleaned_data.get('last_name')
        contact_no = self.cleaned_data.get('contact_no')
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        s = Staff.objects.filter(staff_id__exact=staff_id)
        u = User.objects.filter(username__iexact=username)
        if s.count():
            st = Staff.objects.get(staff_id__exact=staff_id)
            if st.user:
                raise forms.ValidationError(
                    self.error_messages['staff_username_exists'],
                    code='staff_username_exits',
                )
            elif first_name != st.first_name or middle_name != st.middle_name or last_name != st.last_name or email != st.email_address or contact_no != st.contact_no:
                raise forms.ValidationError(
                    self.error_messages['info_not_matched'],
                    code='info_not_matched',
                )
        else:
            raise forms.ValidationError(
                self.error_messages['id_not_found'],
                code='id_not_found',
            )

        if u.count():
            raise forms.ValidationError(
                self.error_messages['username_exists'],
                code='username_exists',
            )

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )

    def save(self):
        user = User.objects.create(
            username=self.cleaned_data['username'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email'],
        )
        return user


class ReservationForm(forms.Form):
    """
    Это форма брони.
    """
    error_messages = {
        'date_time_error': 'Время прибытия',
    }
    first_name = forms.CharField(
        label=_("имя"),
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Введите имя'),
            }
        )
    )
    middle_name = forms.CharField(
        label=_('Отчество'),
        required=False,
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Введите имя'),
            }
        )
    )
    last_name = forms.CharField(
        label=_("Фамилия"),
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Введите имя'),
            }
        )
    )
    contact_no = forms.CharField(
        label=_('контакт'),
        max_length=15,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Введите контактный номер'),
            }
        )
    )
    email = forms.EmailField(
        label=_("Электронная почта"),
        max_length=50,
        required=False,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Пожалуйста, введите ваш адрес электронной почты'),
            }
        )
    )
    address = forms.CharField(
        label=_("адрес"),
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Введите адрес'),
            }
        )
    )
    no_of_children = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Введите количество детей'),
            }
        )
    )
    no_of_adults = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'placeholder': _('Пожалуйста, введите номер взрослого'),
            }
        )
    )
    rooms = forms.ModelMultipleChoiceField(
        queryset=Room.objects.filter(reservation__isnull=True),
        widget=FilteredSelectMultiple(
            is_stacked=True,
            verbose_name="Rooms",
            attrs={
                'class': 'form-control',
            },
        ),
    )
    expected_arrival_date_time = forms.SplitDateTimeField(
        widget=MySplitDateTime(
        )
    )

    expected_departure_date_time = forms.SplitDateTimeField(
        widget=MySplitDateTime(
        )
    )


class CheckInRequestForm(forms.ModelForm):
    class Meta:
        model = CheckIn
        fields = ['reservation']
        widgets = {'reservation': forms.HiddenInput()}


'''
    def clean_expected_arrival_date_time(self):
        expected_arrival_date_time = ' '.join(self.cleaned_data.get('expected_arrival_date_time'))
        expected_arrival_date_time = parse_datetime(expected_arrival_date_time)
        expected_arrival_date_time = pytz.timezone(TIME_ZONE).localize(expected_arrival_date_time, is_dst=None)
        return expected_arrival_date_time

    def clean_expected_departure_date_time(self):
        expected_departure_date_time = ' '.join(self.cleaned_data.get('expected_departure_date_time'))
        expected_departure_date_time = parse_datetime(expected_departure_date_time)
        expected_departure_date_time = pytz.timezone(TIME_ZONE).localize(expected_departure_date_time, is_dst=None)
        return expected_departure_date_time
'''

"""
class ReservationForm(forms.ModelForm):
    error_messages = {
        'number_error': 'Enter the number properly',
        'date_error': 'Departure should be after arrival',
    }
    first_name = forms.CharField(
        label=_("First Name"),
        max_length=50,
        widget=forms.TextInput()
    )
    middle_name = forms.CharField(
        label=_('Middle Name'),
        required=False,
        max_length=50,
        widget=forms.TextInput()
    )
    last_name = forms.CharField(
        label=_("Last Name"),
        max_length=50,
        widget=forms.TextInput()
    )
    contact_no = forms.CharField(
        label=_('Contact No'),
        max_length=15,
        widget=forms.TextInput()
    )
    email = forms.EmailField(
        label=_("Email"),
        max_length=50,
        widget=forms.EmailInput()
    )
    address = forms.CharField(
        label=_("Address"),
        max_length=50,
        widget=forms.TextInput()
    )

    class Meta:
        model = Reservation
        fields = (
            'no_of_children',
            'no_of_adults',
            'expected_arrival_date_time',
            'expected_departure_date_time',
        )

    def clean_no_of_children(self):
        if self.cleaned_data.get('no_of_children') < 0:
            raise forms.ValidationError(
                self.error_messages['number_error'],
                code='number_error',
            )

    def clean_no_of_adults(self):
        if self.cleaned_data.get('no_of_adults') <= 0:
            raise forms.ValidationError(
                self.error_messages['number_error'],
                code='number_error',
            )

    def clean_expected_departure_date_time(self):
        if self.cleaned_data.get('expected_departure_date_time') <= self.cleaned_data.get('expected_arrival_date_time'):
            raise forms.ValidationError(
                self.error_messages['date_error'],
                code='date_error',
            )

    def clean(self):
        pass

"""
