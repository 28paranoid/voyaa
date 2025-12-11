from django.urls import path
from . import views

app_name = 'calendar_app'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.user_signup, name='signup'),
    path('create-event/', views.create_event, name='create_event'),
    path('delete-event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('rsvp/<int:event_id>/<str:status>/', views.rsvp_event, name='rsvp_event'),
    path('settings/', views.settings_view, name='settings'),
    path('players/', views.player_list, name='player_list'),
    path('register-team/', views.register_team, name='register_team'),
    path('registrations/', views.admin_registrations, name='admin_registrations'),
    path('registrations/<int:reg_id>/edit/', views.edit_registration, name='edit_registration'),
    path('registrations/<int:reg_id>/delete/', views.delete_registration, name='delete_registration'),
]
