from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    # Өріс параметрінің атауы бірегей идентификатор болғандықтан бірегей болуы керек.
    # мысалы, Егер индекс бетінің еренсілтемесін пайдаланғыңыз келсе, қатқыл кодталған url сияқты пайдаланбаңыз
    # href = «/ main /» өзгертілген секілді, біз оның барлық көріністерін өзгертуіміз керек.
    # оны шешу үшін, атау өрісінен мәнді пайдаланыңыз. жоғарыдағы мысал үшін пайдаланыңыз
    # href="{% url 'index' %}
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('rooms/', views.RoomListView.as_view(), name='rooms'),  # Бөлмелер тізімі
    path('reservations/', views.ReservationListView.as_view(), name='reservations'),  # Брондау тізімі
    # <int:pk> URL мекенжайында жіберілген дәлелді қабылдайды.
    path('room/<int:pk>', views.RoomDetailView.as_view(), name='room-detail'),  # Әр бөлмедегі бөлшектер
    # Әрбір брондау туралы толық ақпарат
    path('reservation/<str:pk>', views.ReservationDetailView.as_view(), name='reservation-detail'),
    path('customer/<str:pk>', views.CustomerDetailView.as_view(), name='customer-detail'),  # Әр тапсырыс берушінің бөлшектері
    path('staff/<str:pk>', views.StaffDetailView.as_view(), name='staff-detail'),  # Қызметкерлер туралы толық ақпарат
    path('profile/', login_required(views.ProfileView.as_view()), name='profile'),
    path('guests/', views.GuestListView.as_view(), name='guest-list'),
    path('reserve/', views.reserve, name='reserve'),  # Брондау үшін
]
