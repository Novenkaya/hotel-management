from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404  # Үлгіде көрсету үшін
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views import generic

from .forms import Signup, ReservationForm, CheckInRequestForm
from .models import Room, Reservation, Customer, Staff  # Import Models


def index(request):
    """
Это вид шедевра.
    Эта функция основана на представлении.
    """
    page_title = _("Дипломный проект Көркем") # Беттің тақырыбы және тақырып үшін
    total_num_rooms = Room.objects.all().count()
    available_num_rooms = Room.objects.exclude(reservation__isnull=False).count()
    total_num_reservations = Reservation.objects.all().count()
    total_num_staffs = Staff.objects.all().count()
    total_num_customers = Customer.objects.all().count()
    if total_num_reservations == 0:
        last_reserved_by = Reservation.objects.none()
    else:
        last_reserved_by = Reservation.objects.get_queryset().latest('reservation_date_time')

    return render(
        request,
        'index.html',
        # контекст үлгіге жіберілген.
        # үлгілерде айнымалы ретінде пайдаланылады
        # қай жерде болса, келесі функцияның айнымалысы болады
        {
            'title': page_title,
            'total_num_rooms': total_num_rooms,
            'available_num_rooms': available_num_rooms,
            'total_num_reservations': total_num_reservations,
            'total_num_staffs': total_num_staffs,
            'total_num_customers': total_num_customers,
            'last_reserved_by': last_reserved_by,
        }
    )


@transaction.atomic
def signup(request):
    title = "Зарегистрироваться"
    if request.user.is_authenticated:
        request.session.flush()
    if request.method == 'POST':
        form = Signup(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    staffs_group = get_object_or_404(Group, name__iexact="Staffs")
                    form.save()
                    staff_id = form.cleaned_data['staff_id']
                    username = form.cleaned_data['username']
                    s = get_object_or_404(Staff, staff_id__exact=staff_id)
                    s.user = get_object_or_404(User, username__iexact=username)
                    s.user.set_password(form.cleaned_data['password1'])
                    s.user.groups.add(staffs_group)
                    s.user.save()
                    s.save()
            except IntegrityError:
                raise Http404
            return redirect('index')
    else:
        form = Signup()

    return render(
        request,
        'signup.html', {
            'form': form, 'title': title},
    )


@permission_required('main.add_reservation', 'login', raise_exception=True)
@transaction.atomic
def reserve(request):
    title = "Включить бронирование"
    reservation = Reservation.objects.none()
    if request.method == 'POST':
        reservation_form = ReservationForm(request.POST)
        if reservation_form.is_valid():
            try:
                with transaction.atomic():
                    customer = Customer(
                        first_name=reservation_form.cleaned_data.get('first_name'),
                        middle_name=reservation_form.cleaned_data.get('middle_name'),
                        last_name=reservation_form.cleaned_data.get('last_name'),
                        email_address=reservation_form.cleaned_data.get('email'),
                        contact_no=reservation_form.cleaned_data.get('contact_no'),
                        address=reservation_form.cleaned_data.get('address'),
                    )
                    customer.save()
                    staff = request.user
                    reservation = Reservation(
                        staff=get_object_or_404(Staff, user=staff),
                        customer=customer,
                        no_of_children=reservation_form.cleaned_data.get('no_of_children'),
                        no_of_adults=reservation_form.cleaned_data.get('no_of_adults'),
                        expected_arrival_date_time=reservation_form.cleaned_data.get('expected_arrival_date_time'),
                        expected_departure_date_time=reservation_form.cleaned_data.get('expected_departure_date_time'),
                        reservation_date_time=timezone.now(),
                    )
                    reservation.save()
                    for room in reservation_form.cleaned_data.get('rooms'):
                        room.reservation = reservation
                        room.save()
            except IntegrityError:
                raise Http404
            return render(
                request,
                'reserve_success.html', {
                    'reservation': reservation,
                }
            )
    else:
        reservation_form = ReservationForm()

    return render(
        request,
        'reserve.html', {
            'title': title,
            'reservation_form': reservation_form,
        }
    )


def reserve_success(request):
    pass


# Generic ListView немесе DetailView үшін, әдепкі үлгілерді үлгілерде / {{app_name}} / {{template_name}}
# Әдепкі бойынша template_name = modelName_list || modelName_detail.
# мысалы room_list, room_detail
# @ permission_required ('main.can_view_staff')
class RoomListView(PermissionRequiredMixin, generic.ListView):
    """
Посмотреть список номеров.
Создает общий элемент списка.
    """
    model = Room  # Листинг объектілерін моделін таңдайды
    paginate_by = 5  # Бұл қанша объектілердің көмегімен жасалуы керек
    title = _("Список номеров")  # Бұл тақырып және тақырып үшін пайдаланылады
    permission_required = 'main.can_view_room'

# Әдепкіде тек үлгі нысандары контекст ретінде жіберіледі
# Дегенмен, қосымша мәтінмән extra_context өрісі арқылы берілуі мүмкін
# Мұнда тақырып атауы берілді.
    extra_context = {'title': title}

# Әдепкі бойынша:
# template_name = room_list
# егер оны өзгерткіңіз келсе, өріс үлгісін қолданыңыз
# мұнда мұны жасамаңыз, себебі ол әдепкі бойынша орындалады.
# өз көзқарастарыңыз үшін оны жасай аласыз.

    def get_queryset(self):
        filter_value = self.request.GET.get('filter', 'all')
        if filter_value == 'all':
            filter_value = 0
        elif filter_value == 'avail':
            filter_value = 1
        try:
            new_context = Room.objects.filter(availability__in=[filter_value, 1])
        except ValidationError:
            raise Http404(_("Ложный фильтр доказательство предоставляется."))
        return new_context

    def get_context_data(self, **kwargs):
        context = super(RoomListView, self).get_context_data(**kwargs)
        context['filter'] = self.request.GET.get('filter', 'all')
        return context


class RoomDetailView(PermissionRequiredMixin, generic.DetailView):
    """
Посмотреть детали комнаты
Создает полнофункциональный вид
    """
    # The remaining are same as previous.
    model = Room
    title = _("Информация о номере")
    permission_required = 'main.can_view_room'
    extra_context = {'title': title}


class ReservationListView(PermissionRequiredMixin, generic.ListView, generic.FormView):
    """
Просмотр списка покупок.
Создает общий элемент списка.
        """
    model = Reservation
    # queryset өрісі сұрау арқылы көрсетілетін нысандарды таңдайды.
    # Мұнда нысандар кему тәртібімен резервтеу күнінің уақытымен көрсетіледі
    queryset = Reservation.objects.all().order_by('-reservation_date_time')
    title = _("Список бронирования")
    paginate_by = 5
    allow_empty = True
    form_class = CheckInRequestForm
    success_url = reverse_lazy('check_in-list')
    permission_required = 'main.can_view_reservation'
    extra_context = {'title': title}

    @transaction.atomic
    def form_valid(self, form):
        try:
            with transaction.atomic():
                checkin = form.save(commit=False)
                checkin.user = self.request.user
                checkin.save()
        except IntegrityError:
            raise Http404
        return super().form_valid(form)


class ReservationDetailView(PermissionRequiredMixin, generic.DetailView):
    """
Смотрите детали вашего бронирования
Создает полнофункциональный вид
    """
    model = Reservation
    title = _("Информация о бронировании")
    permission_required = 'main.can_view_reservation'
    raise_exception = True
    extra_context = {'title': title}


class CustomerDetailView(PermissionRequiredMixin, generic.DetailView):
    """
Посмотреть подробную информацию о клиенте
Создает полнофункциональный вид
    """
    model = Customer
    title = _("Информация для клиентов")
    permission_required = 'main.can_view_customer'
    raise_exception = True
    extra_context = {'title': title}


class StaffDetailView(PermissionRequiredMixin, generic.DetailView):
    """
Больше информации о сотрудниках
Создает полнофункциональный вид
    """
    model = Staff
    title = _("Информация о персонале")
    permission_required = 'main.can_view_staff_detail'
    extra_context = {'title': title}


class ProfileView(generic.TemplateView):
    template_name = 'profile.html'
    title = "Профиль"
    extra_context = {'title': title}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['information'] = get_object_or_404(Staff, user=self.request.user)
            context['user_information'] = self.request.user
        else:
            raise Http404("Вы не авторизованы")
        return context


class GuestListView(PermissionRequiredMixin, generic.ListView):
    """
Смотрите список гостей отеля.
    """
    model = Customer
    paginate_by = 5
    allow_empty = True
    queryset = Customer.objects.all().filter(Q(reservation__checkin__isnull=False),
                                             Q(reservation__checkin__checkout__isnull=True))
    permission_required = 'main.can_view_customer'
    template_name = 'main/guest_list.html'
    title = 'Список гостей'
    context_object_name = 'guest_list'
    extra_context = {'title': title}
