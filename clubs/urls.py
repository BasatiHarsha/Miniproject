from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('clubs/', views.club_list, name='club_list'),
    path('clubs/<int:club_id>/', views.club_detail, name='club_detail'),
    path('events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('clubs/<int:club_id>/members/', views.member_list, name='member_list'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        success_url='dashboard'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/<str:username>/', views.public_profile_view, name='public_profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Club and Event Registration
    # Club Management URLs
    path('clubs/<int:club_id>/manage/', views.club_manage, name='club_manage'),
    path('clubs/<int:club_id>/join/', views.join_club, name='join_club'),
    path('clubs/<int:club_id>/leave/', views.leave_club, name='leave_club'),
    path('clubs/<int:club_id>/members/<int:membership_id>/approve/', views.approve_member, name='approve_member'),
    path('clubs/<int:club_id>/members/<int:membership_id>/reject/', views.reject_member, name='reject_member'),
    path('clubs/<int:club_id>/members/<int:membership_id>/remove/', views.remove_member, name='remove_member'),
    path('clubs/<int:club_id>/members/<int:membership_id>/make-leader/', views.make_leader, name='make_leader'),
    path('clubs/<int:club_id>/update/', views.update_club, name='update_club'),
    path('clubs/<int:club_id>/delete/', views.delete_club, name='delete_club'),
    path('clubs/<int:club_id>/events/create/', views.create_event, name='create_event'),
    
    # Event Management URLs
    path('events/<int:event_id>/register/', views.register_event, name='register_event'),
    path('events/<int:event_id>/cancel/', views.cancel_event_registration, name='cancel_event_registration'),
    path('events/<int:event_id>/approve/', views.approve_event, name='approve_event'),
    path('events/<int:event_id>/reject/', views.reject_event, name='reject_event'),
    path('calendar/', views.calendar_view, name='calendar'),
]
