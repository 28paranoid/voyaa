from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('player', 'Player'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='player')
    
    # Resolving clashes with default auth groups/permissions
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="calendar_users",
        related_query_name="calendar_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="calendar_users",
        related_query_name="calendar_user",
    )

class Team(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='teams', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Event(models.Model):
    TYPE_CHOICES = [
        ('match', 'Match'),
        ('practice', 'Practice'),
        ('meeting', 'Meeting'),
    ]
    
    title = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True) # Optional duration
    location = models.CharField(max_length=200, blank=True)
    teams = models.ManyToManyField(Team, related_name='events', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_event_type_display()})"

class RSVP(models.Model):
    STATUS_CHOICES = [
        ('attending', 'Attending'),
        ('unavailable', 'Unavailable'),
        ('pending', 'Pending'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rsvps')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'event']

    def __str__(self):
        return f"{self.user.username} - {self.event.title}: {self.status}"

class Branding(models.Model):
    logo = models.ImageField(upload_to='branding/', blank=True, null=True)
    primary_color = models.CharField(max_length=7, default='#c0705a') # Orange
    registration_open = models.BooleanField(default=False)  # Admin can toggle registration
    
    def save(self, *args, **kwargs):
        # Ensure singleton
        if not self.pk and Branding.objects.exists():
            return
        super().save(*args, **kwargs)

    def __str__(self):
        return "Site Branding"

class MatchRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_registrations')
    team_name = models.CharField(max_length=100, unique=True)
    discord_id = models.CharField(max_length=100)
    members = models.TextField(help_text="Comma-separated list of team members")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.team_name
