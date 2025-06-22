from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from clubs.models import Club, Event, ClubMembership, EventRegistration, UserProfile
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = 'Creates sample data for testing'

    def handle(self, *args, **kwargs):
        # Create admin user
        admin_username = 'admin'
        try:
            admin_user = User.objects.create_superuser(
                username=admin_username,
                email='admin@college.edu',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            UserProfile.objects.create(
                user=admin_user,
                bio='College Hub Administrator',
                department='Administration',
                role='admin'
            )
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin_username}'))
        except:
            admin_user = User.objects.get(username=admin_username)
            self.stdout.write(self.style.WARNING(f'Admin user exists: {admin_username}'))

        # Create faculty users
        faculty_data = [
            ('prof_kumar', 'Prof. Kumar', 'Computer Science'),
            ('prof_singh', 'Prof. Singh', 'Cultural Studies'),
            ('prof_patel', 'Prof. Patel', 'Sports Science'),
        ]

        faculty_users = []
        for username, name, dept in faculty_data:
            first_name, last_name = name.split(' ')
            try:
                faculty = User.objects.create_user(
                    username=username,
                    email=f'{username}@college.edu',
                    password='faculty123',
                    first_name=first_name,
                    last_name=last_name
                )
                UserProfile.objects.create(
                    user=faculty,
                    bio=f'{name} - {dept} Department Faculty',
                    department=dept,
                    role='faculty',
                    faculty_id=f'FAC{len(faculty_users) + 1:03d}'
                )
                faculty_users.append(faculty)
                self.stdout.write(self.style.SUCCESS(f'Created faculty user: {username}'))
            except:
                faculty_users.append(User.objects.get(username=username))
                self.stdout.write(self.style.WARNING(f'Faculty user exists: {username}'))

        # Create student users
        users = []
        for i in range(1, 6):
            username = f'student{i}'
            try:
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@college.edu',
                    password='student123',
                    first_name=f'Student{i}',
                    last_name='User'
                )
                UserProfile.objects.create(
                    user=user,
                    bio=f'I am a student who loves learning!',
                    department='Computer Science',
                    role='student',
                    student_id=f'STU{i:03d}'
                )
                users.append(user)
                self.stdout.write(self.style.SUCCESS(f'Created student user: {username}'))
            except:
                users.append(User.objects.get(username=username))
                self.stdout.write(self.style.WARNING(f'Student user exists: {username}'))

        # Create sample clubs with faculty advisors
        clubs = []
        club_data = [
            ('Programming Club', 'technical', 'A vibrant community of coding enthusiasts who meet regularly to work on exciting projects.', faculty_users[0]),
            ('Dance Club', 'cultural', 'Express yourself through various dance forms! Regular workshops and performances.', faculty_users[1]),
            ('Basketball Club', 'sports', 'Join our energetic basketball team! Regular practice and tournaments.', faculty_users[2]),
            ('Debate Club', 'academic', 'Develop your public speaking and critical thinking skills.', faculty_users[1]),
            ('Photography Club', 'social', 'Capture and share beautiful moments! Regular photo walks and exhibitions.', faculty_users[0])
        ]

        for name, category, description, faculty in club_data:
            club, created = Club.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'category': category
                }
            )
            clubs.append(club)
            if created:
                # Add faculty as advisor
                ClubMembership.objects.create(
                    user=faculty,
                    club=club,
                    role='leader'
                )
                # Add first student as club leader
                ClubMembership.objects.create(
                    user=users[0],
                    club=club,
                    role='coordinator'
                )
                self.stdout.write(self.style.SUCCESS(f'Created club: {name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Club exists: {name}'))

        # Add regular members
        for user in users[1:]:
            for club in clubs:
                ClubMembership.objects.get_or_create(
                    user=user,
                    club=club,
                    defaults={'role': 'member'}
                )

        # Create sample events
        now = timezone.now()
        event_data = [
            ('Python Workshop', clubs[0], now + datetime.timedelta(days=7),
             'Learn Python programming from basics to advanced topics. Bring your laptop!',
             'Computer Lab 101'),
            ('Dance Competition', clubs[1], now + datetime.timedelta(days=14),
             'Annual dance competition with amazing prizes!',
             'College Auditorium'),
            ('Basketball Tournament', clubs[2], now + datetime.timedelta(days=21),
             'Inter-college basketball tournament. Come support our team!',
             'Sports Complex'),
            ('Debate Championship', clubs[3], now + datetime.timedelta(days=28),
             'Annual debate championship with guest judges.',
             'Seminar Hall'),
            ('Photo Exhibition', clubs[4], now + datetime.timedelta(days=35),
             'Annual photography exhibition showcasing student work.',
             'Art Gallery')
        ]

        for title, club, date, description, location in event_data:
            event, created = Event.objects.get_or_create(
                title=title,
                defaults={
                    'description': description,
                    'date': date,
                    'location': location,
                    'club': club,
                    'capacity': 50,
                    'registration_deadline': date - datetime.timedelta(days=1)
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created event: {title}'))
                # Register some students for each event
                for user in users[:3]:
                    EventRegistration.objects.get_or_create(
                        user=user,
                        event=event
                    )
            else:
                self.stdout.write(self.style.WARNING(f'Event exists: {title}'))

        self.stdout.write(self.style.SUCCESS('Successfully created sample data'))
