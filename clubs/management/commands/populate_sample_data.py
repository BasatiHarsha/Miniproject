from django.core.management.base import BaseCommand
from django.utils import timezone
from clubs.models import Club, Event, Member
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **kwargs):
        # Create sample clubs
        clubs_data = [
            {
                'name': 'Tech Innovators',
                'description': 'A club dedicated to exploring and creating new technologies. Join us for workshops, hackathons, and exciting tech projects!'
            },
            {
                'name': 'Art & Design Society',
                'description': 'Express your creativity through various forms of art. Weekly workshops, exhibitions, and collaborative projects.'
            },
            {
                'name': 'Sports Club',
                'description': 'Stay active and healthy with our diverse sports programs. Regular tournaments, training sessions, and fitness challenges.'
            },
            {
                'name': 'Environmental Club',
                'description': 'Working together to create a sustainable future. Join our eco-friendly initiatives and awareness campaigns.'
            }
        ]

        for club_data in clubs_data:
            club = Club.objects.create(**club_data)
            self.stdout.write(f'Created club: {club.name}')

            # Create members for each club
            member_roles = ['President', 'Vice President', 'Secretary', 'Treasurer', 'Member']
            for i, role in enumerate(member_roles, 1):
                member = Member.objects.create(
                    name=f'{club.name} {role}',
                    email=f'{role.lower().replace(" ", "")}@{club.name.lower().replace(" ", "")}.com',
                    club=club,
                    role=role
                )
                self.stdout.write(f'Created member: {member.name}')

        # Create sample events
        now = timezone.now()
        clubs = Club.objects.all()
        events_data = [
            {
                'title': 'Annual Tech Hackathon',
                'description': 'Join us for 24 hours of coding, innovation, and fun! Great prizes to be won.',
                'date': now + timedelta(days=7),
                'location': 'Main Campus Building',
                'club': clubs[0]
            },
            {
                'title': 'Art Exhibition',
                'description': 'Showcasing student artworks from various mediums. Everyone is welcome!',
                'date': now + timedelta(days=14),
                'location': 'College Art Gallery',
                'club': clubs[1]
            },
            {
                'title': 'Inter-College Sports Tournament',
                'description': 'Annual sports competition with neighboring colleges.',
                'date': now + timedelta(days=21),
                'location': 'College Sports Complex',
                'club': clubs[2]
            },
            {
                'title': 'Environment Day Workshop',
                'description': 'Learn about sustainable practices and participate in our campus clean-up drive.',
                'date': now + timedelta(days=3),
                'location': 'Green Zone',
                'club': clubs[3]
            }
        ]

        for event_data in events_data:
            event = Event.objects.create(**event_data)
            self.stdout.write(f'Created event: {event.title}')

        self.stdout.write(self.style.SUCCESS('Successfully added sample data'))
