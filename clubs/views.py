from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Club, Event, UserProfile, ClubMembership, EventRegistration
from .forms import (
    CustomUserCreationForm, UserProfileForm, EventRegistrationForm,
    ClubMembershipForm, EventCreateForm, ClubUpdateForm, LeaderAssignmentForm
)
from calendar import monthrange

User = get_user_model()

def home(request):
    query = request.GET.get('q')
    clubs = Club.objects.annotate(member_count=Count('members')).order_by('-member_count')[:3]
    upcoming_events = Event.objects.filter(
        date__gte=timezone.now()
    ).order_by('date')[:5]

    recommended_clubs = []
    recommended_events = []
    if request.user.is_authenticated:
        recommended_clubs = Club.get_recommended_clubs(request.user)
        recommended_events = Event.get_recommended_events(request.user)
    
    if query:
        clubs = Club.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
        upcoming_events = Event.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query)
        ).filter(date__gte=timezone.now()).order_by('date')
    
    context = {
        'clubs': clubs,
        'upcoming_events': upcoming_events,
        'recommended_clubs': recommended_clubs,
        'recommended_events': recommended_events,
    }
    return render(request, 'index.html', context)

def club_list(request):
    query = request.GET.get('q')
    if query:
        clubs = Club.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
    else:
        clubs = Club.objects.all()
    return render(request, 'clubs/club_list.html', {'clubs': clubs})

def club_detail(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    membership = None
    if request.user.is_authenticated:
        membership = ClubMembership.objects.filter(
            user=request.user,
            club=club
        ).first()
    
    context = {
        'club': club,
        'membership': membership,
    }
    return render(request, 'clubs/club_detail.html', context)

def event_list(request):
    events = Event.objects.filter(
        date__gte=timezone.now()
    ).order_by('date')
    return render(request, 'clubs/event_list.html', {
        'events': events,
        'now': timezone.now()
    })

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'clubs/event_detail.html', {
        'event': event,
        'now': timezone.now()
    })

def member_list(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    members = club.members.all()
    return render(request, 'clubs/member_list.html', {'club': club, 'members': members})

from django.db import transaction

def register(request):
    role = request.GET.get('role', 'student')  # Default to student registration
    
    if role != 'student':
        messages.error(request, 'Only student registration is allowed. Faculty and admin accounts are created by administrators.')
        return redirect('login')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)
        
        if form.is_valid() and profile_form.is_valid():
            try:
                with transaction.atomic():
                    # Create the user first
                    user = form.save()
                    
                    # Create new profile with role
                    profile = profile_form.save(commit=False)
                    profile.user = user
                    profile.role = 'student'
                    profile.student_id = f'STU{User.objects.count():04d}'
                    profile.save()
                    
                    # Important: Save the session before logging in
                    if not request.session.session_key:
                        request.session.save()
                        
                    # Log the user in
                    login(request, user)
                    request.session['role'] = 'student'  # Store role in session
                    request.session.modified = True  # Mark session as modified
                    
                    messages.success(request, f'Welcome to College Hub, {user.first_name}! Your student account has been created successfully.')
                    return redirect('dashboard')
                    
            except Exception as e:
                # If anything goes wrong, delete the user if it was created
                if 'user' in locals():
                    user.delete()
                messages.error(request, str(e) if settings.DEBUG else 'There was an error creating your account. Please try again.')
                return redirect('register')  # Redirect instead of continuing to render
    else:
        form = CustomUserCreationForm()
        profile_form = UserProfileForm()
    
    return render(request, 'registration/register.html', {
        'form': form,
        'profile_form': profile_form,
        'role': role
    })

@login_required
def profile_view(request):
    user = request.user
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        profile_form = UserProfileForm(instance=profile)

    # Get user's registered events
    registered_events = Event.objects.filter(
        registered_users=user,
        date__gte=timezone.now()
    ).order_by('date')
    
    # Get user's clubs
    user_clubs = Club.objects.filter(members=user)
    
    context = {
        'profile_form': profile_form,
        'profile': profile,
        'user': user,
        'upcoming_events': registered_events,
        'clubs_count': user_clubs.count(),
        'events_count': registered_events.count(),
        'user_clubs': user_clubs,
    }
    return render(request, 'clubs/profile.html', context)

@login_required
def dashboard(request):
    # Get upcoming events the user has registered for
    registered_events = Event.objects.filter(
        registered_users=request.user,
        date__gte=timezone.now()
    ).order_by('date')
    
    # Get clubs the user is a member of
    user_clubs = Club.objects.filter(members=request.user)
    
    # Get recommended clubs and events
    recommended_clubs = Club.get_recommended_clubs(request.user)
    recommended_events = Event.get_recommended_events(request.user)
    
    context = {
        'registered_events': registered_events,
        'user_clubs': user_clubs,
        'recommended_clubs': recommended_clubs,
        'recommended_events': recommended_events,
    }
    return render(request, 'dashboard.html', context)

@login_required
def join_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    
    # Check if user is already a member
    existing_membership = ClubMembership.objects.filter(
        user=request.user,
        club=club
    ).first()

    if existing_membership:
        if existing_membership.status == 'pending':
            messages.info(request, 'Your membership request is still pending.')
        elif existing_membership.status == 'approved':
            messages.info(request, 'You are already a member of this club.')
        else:
            # If previously rejected, create new request
            existing_membership.status = 'pending'
            existing_membership.save()
            messages.success(request, 'Your membership request has been submitted.')
    else:
        # Create new membership request
        ClubMembership.objects.create(
            user=request.user,
            club=club,
            role='member',
            status='pending'
        )
        messages.success(request, 'Your membership request has been submitted.')
    
    return redirect('club_detail', club_id=club_id)

@login_required
def leave_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    
    if request.method == 'POST':
        membership = ClubMembership.objects.filter(user=request.user, club=club)
        if membership.exists():
            membership.delete()
            messages.success(request, f'You have left {club.name}.')
        else:
            messages.warning(request, 'You are not a member of this club.')
    
    return redirect('club_detail', club_id=club.id)

@login_required
def register_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    next_page = request.GET.get('next', 'event_detail')
    
    if request.method == 'POST':
        if event.date < timezone.now():
            messages.error(request, 'This event has already passed.')
        elif event.registration_deadline and event.registration_deadline < timezone.now():
            messages.error(request, 'Registration deadline has passed.')
        elif event.is_full:
            messages.error(request, 'This event is full.')
        elif not EventRegistration.objects.filter(user=request.user, event=event).exists():
            EventRegistration.objects.create(
                user=request.user,
                event=event
            )
            messages.success(request, f'You have successfully registered for {event.title}!')
        else:
            messages.warning(request, 'You are already registered for this event.')
    
    # Return to the appropriate page
    if next_page == 'calendar':
        return redirect('calendar')
    elif next_page == 'dashboard':
        return redirect('dashboard')
    else:
        return redirect('event_detail', event_id=event.id)

@login_required
def cancel_event_registration(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if request.method == 'POST':
        registration = EventRegistration.objects.filter(user=request.user, event=event)
        if registration.exists():
            registration.delete()
            messages.success(request, f'Your registration for {event.title} has been cancelled.')
        else:
            messages.warning(request, 'You are not registered for this event.')
    
    return redirect('event_detail', event_id=event.id)

@login_required
def calendar_view(request):
    from datetime import datetime, timedelta
    from django.utils.timezone import make_aware
    import calendar
    
    # Get requested month or use current date
    month_param = request.GET.get('month')
    if month_param:
        try:
            current_date = datetime.strptime(month_param, '%Y-%m')
            current_date = make_aware(datetime(current_date.year, current_date.month, 1))
        except ValueError:
            current_date = timezone.now()
    else:
        current_date = timezone.now()
    
    # Calculate current, previous, and next month dates
    current_month_start = make_aware(datetime(current_date.year, current_date.month, 1))
    if current_date.month == 1:
        prev_month_start = make_aware(datetime(current_date.year - 1, 12, 1))
    else:
        prev_month_start = make_aware(datetime(current_date.year, current_date.month - 1, 1))
        
    if current_date.month == 12:
        next_month_start = make_aware(datetime(current_date.year + 1, 1, 1))
    else:
        next_month_start = make_aware(datetime(current_date.year, current_date.month + 1, 1))

    # Get events for current month
    current_month_events = Event.objects.filter(
        date__year=current_month_start.year,
        date__month=current_month_start.month
    ).order_by('date')

    # Get events for next month
    next_month_events = Event.objects.filter(
        date__year=next_month_start.year,
        date__month=next_month_start.month
    ).order_by('date')
    
    # Create calendar data
    cal = calendar.monthcalendar(current_date.year, current_date.month)
    
    # Get events organized by day
    events_by_day = {}
    for event in current_month_events:
        day = event.date.day
        if day not in events_by_day:
            events_by_day[day] = []
        events_by_day[day].append(event)

    context = {
        'current_month_events': current_month_events,
        'next_month_events': next_month_events,
        'prev_month': prev_month_start,
        'current_month': current_month_start,
        'next_month': next_month_start,
        'calendar_weeks': cal,
        'events_by_day': events_by_day,
        'weekdays': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    }
    return render(request, 'clubs/calendar.html', context)

def public_profile_view(request, username):
    user = get_object_or_404(User, username=username)
    context = {
        'profile_user': user,
        'registered_events': EventRegistration.objects.filter(user=user).select_related('event'),
        'user_clubs': ClubMembership.objects.filter(user=user).select_related('club')
    }
    return render(request, 'clubs/public_profile.html', context)

@login_required
def club_manage(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    user_profile = request.user.userprofile
    membership = ClubMembership.objects.filter(user=request.user, club=club).first()

    if not user_profile.can_manage_club(club):
        messages.error(request, "You don't have permission to manage this club.")
        return redirect('club_detail', club_id=club_id)

    # Get pending membership requests
    pending_memberships = ClubMembership.objects.filter(
        club=club,
        status='pending'
    ).select_related('user__userprofile')

    # Get all approved members
    members = ClubMembership.objects.filter(
        club=club,
        status='approved'
    ).select_related('user__userprofile')

    # Get all club events
    events = Event.objects.filter(club=club).order_by('-date')

    context = {
        'club': club,
        'pending_memberships': pending_memberships,
        'members': members,
        'events': events,
        'membership': membership,
    }

    # Add forms if user has appropriate permissions
    if user_profile.is_faculty_advisor(club) or user_profile.is_admin():
        from .forms import LeaderAssignmentForm
        context['leader_form'] = LeaderAssignmentForm(club)

    if user_profile.can_manage_events(club):
        from .forms import EventCreateForm
        context['event_form'] = EventCreateForm()

    if user_profile.can_manage_club(club):
        from .forms import ClubUpdateForm
        context['club_form'] = ClubUpdateForm(instance=club)

    return render(request, 'clubs/club_manage.html', context)

@login_required
def approve_member(request, club_id, membership_id):
    club = get_object_or_404(Club, id=club_id)
    membership = get_object_or_404(ClubMembership, id=membership_id, club=club)
    
    if not request.user.userprofile.can_manage_club(club):
        messages.error(request, "You don't have permission to approve members.")
        return redirect('club_detail', club_id=club_id)
    
    membership.status = 'approved'
    membership.approved_by = request.user
    membership.approved_date = timezone.now()
    membership.save()
    
    messages.success(request, f'{membership.user.get_full_name()} has been approved as a member.')
    return redirect('club_manage', club_id=club_id)

@login_required
def reject_member(request, club_id, membership_id):
    club = get_object_or_404(Club, id=club_id)
    membership = get_object_or_404(ClubMembership, id=membership_id, club=club)
    
    if not request.user.userprofile.can_manage_club(club):
        messages.error(request, "You don't have permission to reject members.")
        return redirect('club_detail', club_id=club_id)
    
    membership.status = 'rejected'
    membership.save()
    
    messages.success(request, f'Membership request from {membership.user.get_full_name()} has been rejected.')
    return redirect('club_manage', club_id=club_id)

@login_required
def make_leader(request, club_id, membership_id):
    club = get_object_or_404(Club, id=club_id)
    membership = get_object_or_404(ClubMembership, id=membership_id, club=club)
    
    if not request.user.userprofile.is_faculty_advisor(club):
        messages.error(request, "Only faculty advisors can assign club leaders.")
        return redirect('club_detail', club_id=club_id)
    
    membership.role = 'leader'
    membership.save()
    
    messages.success(request, f'{membership.user.get_full_name()} has been made a club leader.')
    return redirect('club_manage', club_id=club_id)

@login_required
def create_event(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    
    if not request.user.userprofile.can_manage_events(club):
        messages.error(request, "You don't have permission to create events.")
        return redirect('club_detail', club_id=club_id)
    
    if request.method == 'POST':
        form = EventCreateForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.club = club
            event.created_by = request.user
            event.save()
            messages.success(request, 'Event created successfully! Awaiting faculty approval.')
            return redirect('club_manage', club_id=club_id)
    
    messages.error(request, 'There was an error creating the event.')
    return redirect('club_manage', club_id=club_id)

@login_required
def approve_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if not request.user.userprofile.is_faculty_advisor(event.club):
        messages.error(request, "Only faculty advisors can approve events.")
        return redirect('event_detail', event_id=event_id)
    
    event.status = 'approved'
    event.approved_by = request.user
    event.approved_date = timezone.now()
    event.save()
    
    messages.success(request, f'Event "{event.title}" has been approved.')
    return redirect('club_manage', club_id=event.club.id)

@login_required
def reject_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if not request.user.userprofile.is_faculty_advisor(event.club):
        messages.error(request, "Only faculty advisors can reject events.")
        return redirect('event_detail', event_id=event_id)
    
    event.status = 'rejected'
    event.approved_by = None
    event.approved_date = None
    event.save()
    
    messages.success(request, f'Event "{event.title}" has been rejected.')
    return redirect('club_manage', club_id=event.club.id)

@login_required
def remove_member(request, club_id, membership_id):
    club = get_object_or_404(Club, id=club_id)
    membership = get_object_or_404(ClubMembership, id=membership_id, club=club)
    
    if not request.user.userprofile.can_manage_club(club):
        messages.error(request, "You don't have permission to remove members.")
        return redirect('club_detail', club_id=club_id)
    
    # Don't allow removing faculty advisors
    if membership.role == 'faculty_advisor':
        messages.error(request, "Faculty advisors cannot be removed from the club.")
        return redirect('club_manage', club_id=club_id)
    
    # Store user info for message
    user_name = membership.user.get_full_name()
    
    # Delete the membership
    membership.delete()
    
    messages.success(request, f'{user_name} has been removed from the club.')
    return redirect('club_manage', club_id=club_id)

@login_required
def update_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    
    if not request.user.userprofile.can_manage_club(club):
        messages.error(request, "You don't have permission to update this club.")
        return redirect('club_detail', club_id=club_id)
    
    if request.method == 'POST':
        form = ClubUpdateForm(request.POST, request.FILES, instance=club)
        if form.is_valid():
            form.save()
            messages.success(request, 'Club details have been updated successfully.')
        else:
            messages.error(request, 'There was an error updating the club details.')
    
    return redirect('club_manage', club_id=club_id)

@login_required
def delete_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    
    if not request.user.userprofile.can_delete_club(club):
        messages.error(request, "You don't have permission to delete this club.")
        return redirect('club_detail', club_id=club_id)
    
    if request.method == 'POST':
        confirm = request.POST.get('confirm')
        if confirm == 'DELETE':
            club_name = club.name
            club.delete()
            messages.success(request, f'The club "{club_name}" has been deleted.')
            return redirect('club_list')
        else:
            messages.error(request, 'Please type "DELETE" to confirm club deletion.')
    
    return redirect('club_manage', club_id=club_id)
