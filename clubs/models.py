from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count

class Club(models.Model):
    CATEGORY_CHOICES = [
        ('technical', 'Technical'),
        ('cultural', 'Cultural'),
        ('sports', 'Sports'),
        ('academic', 'Academic'),
        ('social', 'Social'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='social')
    image = models.ImageField(upload_to='club_images/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='club_thumbnails/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(
        User,
        through='ClubMembership',
        through_fields=('club', 'user'),
        related_name='joined_clubs'
    )

    def get_registered_count(self):
        return self.members.count()

    @classmethod
    def get_recommended_clubs(cls, user):
        # Get user's interests based on their current clubs
        user_interests = cls.objects.filter(members=user).values_list('category', flat=True)
        
        # Find popular clubs in same categories that user hasn't joined
        recommended = cls.objects.exclude(members=user)\
            .filter(category__in=user_interests)\
            .annotate(member_count=Count('members'))\
            .order_by('-member_count')[:5]
        
        # If no recommendations based on interests, return popular clubs
        if not recommended:
            recommended = cls.objects.exclude(members=user)\
                .annotate(member_count=Count('members'))\
                .order_by('-member_count')[:5]
        return recommended

    def __str__(self):
        return self.name

class ClubMembership(models.Model):
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('leader', 'Leader'),
        ('faculty_advisor', 'Faculty Advisor'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    joined_date = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_memberships')
    approved_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'club')

    def __str__(self):
        return f"{self.user.username} - {self.club.name} ({self.role})"
        
    def is_active(self):
        return self.status == 'approved'

    def is_leader(self):
        return self.role == 'leader' and self.status == 'approved'

    def is_faculty_advisor(self):
        return self.role == 'faculty_advisor' and self.status == 'approved'

class Event(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='events')
    image = models.ImageField(upload_to='event_images/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='event_thumbnails/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_events')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_events')
    approved_date = models.DateTimeField(null=True, blank=True)
    registered_users = models.ManyToManyField(User, through='EventRegistration')
    capacity = models.PositiveIntegerField(default=0)  # 0 means unlimited
    registration_deadline = models.DateTimeField(null=True, blank=True)
    
    @property
    def is_full(self):
        return self.capacity > 0 and self.registered_users.count() >= self.capacity

    @classmethod
    def get_recommended_events(cls, user):
        # Get user's clubs
        user_clubs = Club.objects.filter(members=user)
        
        # Find upcoming events from user's clubs that they haven't registered for
        from django.utils import timezone
        recommended = cls.objects.filter(
            club__in=user_clubs,
            date__gt=timezone.now()
        ).exclude(
            registered_users=user
        ).order_by('date')[:5]
        
        # If no recommendations from user's clubs, return popular upcoming events
        if not recommended:
            recommended = cls.objects.filter(
                date__gt=timezone.now()
            ).exclude(
                registered_users=user
            ).annotate(
                reg_count=Count('registered_users')
            ).order_by('-reg_count')[:5]
        
        return recommended

    def __str__(self):
        return self.title

class EventRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'event')

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    department = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    faculty_id = models.CharField(max_length=50, blank=True, null=True)
    student_id = models.CharField(max_length=50, blank=True, null=True)
    interests = models.ManyToManyField('Club', related_name='interested_users', blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def is_faculty(self):
        return self.role == 'faculty'

    def is_admin(self):
        return self.role == 'admin'

    def is_student(self):
        return self.role == 'student'

    def is_club_leader(self, club=None):
        if club:
            return ClubMembership.objects.filter(
                user=self.user, 
                club=club, 
                role='leader',
                status='approved'
            ).exists()
        return ClubMembership.objects.filter(
            user=self.user, 
            role='leader',
            status='approved'
        ).exists()

    def is_club_faculty_advisor(self, club=None):
        if club:
            return ClubMembership.objects.filter(
                user=self.user, 
                club=club, 
                role='faculty_advisor',
                status='approved'
            ).exists()
        return ClubMembership.objects.filter(
            user=self.user, 
            role='faculty_advisor',
            status='approved'
        ).exists()

    def get_led_clubs(self):
        return Club.objects.filter(
            clubmembership__user=self.user, 
            clubmembership__role='leader',
            clubmembership__status='approved'
        )

    def get_advised_clubs(self):
        return Club.objects.filter(
            clubmembership__user=self.user, 
            clubmembership__role='faculty_advisor',
            clubmembership__status='approved'
        )

    def can_manage_club(self, club):
        # Admin can manage all clubs
        if self.is_admin():
            return True
        # Faculty can manage clubs they advise
        if self.is_faculty() and self.is_club_faculty_advisor(club):
            return True
        # Club leaders can manage their clubs
        return self.is_club_leader(club)

    def can_approve_members(self, club):
        return self.can_manage_club(club)

    def can_manage_events(self, club):
        return self.can_manage_club(club)

    def can_create_club(self):
        return self.is_admin() or self.is_faculty()

    def can_delete_club(self, club):
        return self.is_admin() or (self.is_faculty() and self.is_club_faculty_advisor(club))
