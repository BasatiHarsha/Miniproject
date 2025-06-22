from django.contrib import admin
from .models import Club, Event, ClubMembership, EventRegistration, UserProfile

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_at', 'get_member_count')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    
    def get_member_count(self, obj):
        return obj.members.count()
    get_member_count.short_description = 'Members'

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'club', 'date', 'location', 'get_registration_count')
    list_filter = ('club', 'date')
    search_fields = ('title', 'description', 'location')
    
    def get_registration_count(self, obj):
        return obj.registered_users.count()
    get_registration_count.short_description = 'Registrations'

@admin.register(ClubMembership)
class ClubMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'club', 'role', 'joined_date')
    list_filter = ('role', 'joined_date', 'club')
    search_fields = ('user__username', 'user__email', 'club__name')

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'registered_at')
    list_filter = ('registered_at', 'event')
    search_fields = ('user__username', 'user__email', 'event__title')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department')
    list_filter = ('department',)
    search_fields = ('user__username', 'user__email', 'bio')
