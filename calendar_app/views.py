from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Event, Team, Branding, RSVP, User, MatchRegistration
from .forms import SignUpForm, LoginForm, EventForm, BrandingForm, MatchRegistrationForm # We will need to create these forms

# Placeholder for forms - creating minimal inline for now or separate file later. 
# For now, I'll rely on generic views or manual form handling to speed up, 
# but best practice is forms.py. I'll create forms.py next.

def user_login(request):
    if request.method == 'POST':
        # Simple manual auth for speed, or use AuthenticationForm
        from django.contrib.auth.forms import AuthenticationForm
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('calendar_app:dashboard')
    else:
        from django.contrib.auth.forms import AuthenticationForm
        form = AuthenticationForm()
    
    branding = Branding.objects.first()
    return render(request, 'calendar_app/login.html', {'form': form, 'branding': branding})

def user_logout(request):
    logout(request)
    return redirect('calendar_app:login')

def user_signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully! Welcome.")
            return redirect('calendar_app:dashboard')
    else:
        form = SignUpForm()
    
    branding = Branding.objects.first()
    return render(request, 'calendar_app/signup.html', {'form': form, 'branding': branding})

@login_required
def dashboard(request):
    events = Event.objects.all().order_by('start_time')
    user_rsvps = RSVP.objects.filter(user=request.user).values_list('event_id', 'status')
    rsvp_dict = {event_id: status for event_id, status in user_rsvps}
    
    # Annotate events for template usage without custom filters
    for event in events:
        event.user_status = rsvp_dict.get(event.id)
    
    # Calendar Logic
    import calendar
    from django.utils import timezone
    import datetime
    
    # Get year and month from request or default to now
    now = timezone.now()
    try:
        year = int(request.GET.get('year', now.year))
        month = int(request.GET.get('month', now.month))
    except ValueError:
        year = now.year
        month = now.month
        
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    # Calculate Next/Prev Month
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    # Create valid date objects for the grid to compare with events
    # We want a list of weeks, where each day has {day: int, events: []}
    calendar_weeks = []
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append({'day': 0, 'events': []})
            else:
                # Find events on this day
                day_events = [e for e in events if e.start_time.year == year and e.start_time.month == month and e.start_time.day == day]
                week_data.append({'day': day, 'events': day_events})
        calendar_weeks.append(week_data)

    branding = Branding.objects.first()
    if not branding:
        branding = Branding.objects.create(primary_color='#00ff9d')

    context = {
        'events': events,
        'branding': branding,
        'rsvp_dict': rsvp_dict,
        'is_admin': request.user.role == 'admin' or request.user.is_superuser,
        'calendar_weeks': calendar_weeks,
        'month_name': month_name,
        'year': year,
        'next_month': next_month,
        'next_year': next_year,
        'prev_month': prev_month,
        'prev_year': prev_year,
    }
    return render(request, 'calendar_app/dashboard.html', context)

@login_required
def create_event(request):
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, "Unauthorized")
        return redirect('calendar_app:dashboard')
        
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Event created successfully!")
            return redirect('calendar_app:dashboard')
    else:
        form = EventForm()
    return render(request, 'calendar_app/create_event.html', {'form': form})

@login_required
def rsvp_event(request, event_id, status):
    event = get_object_or_404(Event, id=event_id)
    rsvp, created = RSVP.objects.get_or_create(user=request.user, event=event)
    if status in ['attending', 'unavailable']:
        rsvp.status = status
        rsvp.save()
    return redirect('calendar_app:dashboard')

@login_required
def settings_view(request):
    if request.user.role != 'admin' and not request.user.is_superuser:
        return redirect('calendar_app:dashboard')
    
    branding = Branding.objects.first()
    if not branding:
        branding = Branding.objects.create(primary_color='#00ff9d')
    
    if request.method == 'POST':
        form = BrandingForm(request.POST, instance=branding)
        if form.is_valid():
            form.save()
            messages.success(request, "Branding updated!")
            return redirect('calendar_app:settings')
    else:
        form = BrandingForm(instance=branding)
        
    return render(request, 'calendar_app/settings.html', {'branding_form': form, 'branding': branding})

@login_required
def delete_event(request, event_id):
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, "Unauthorized")
        return redirect('calendar_app:dashboard')
    
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        event.delete()
        messages.success(request, "Event deleted successfully!")
    
    return redirect('calendar_app:dashboard')

@login_required
def player_list(request):
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, "Unauthorized")
        return redirect('calendar_app:dashboard')
    
    players = User.objects.filter(role='player').order_by('username')
    branding = Branding.objects.first()
    
    context = {
        'players': players,
        'branding': branding,
    }
    return render(request, 'calendar_app/player_list.html', context)

@login_required
def register_team(request):
    branding = Branding.objects.first()
    
    # Check if user already registered
    existing_registration = MatchRegistration.objects.filter(user=request.user).first()
    if existing_registration:
        context = {
            'branding': branding,
            'registration': existing_registration,
            'already_registered': True,
        }
        return render(request, 'calendar_app/register_team.html', context)
    
    # Check if registration is open
    if not branding or not branding.registration_open:
        messages.error(request, "Team registration is currently closed.")
        return redirect('calendar_app:dashboard')
    
    if request.method == 'POST':
        form = MatchRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.user = request.user
            registration.save()
            
            # Show success page
            context = {
                'branding': branding,
                'registration': registration,
                'just_registered': True,
            }
            return render(request, 'calendar_app/register_team.html', context)
    else:
        form = MatchRegistrationForm()
    
    context = {
        'form': form,
        'branding': branding,
    }
    return render(request, 'calendar_app/register_team.html', context)

@login_required
def admin_registrations(request):
    if request.user.role != 'admin' and not request.user.is_superuser:
        messages.error(request, "Unauthorized")
        return redirect('calendar_app:dashboard')
    
    registrations = MatchRegistration.objects.all()
    branding = Branding.objects.first()
    
    context = {
        'registrations': registrations,
        'branding': branding,
    }
    return render(request, 'calendar_app/admin_registrations.html', context)

@login_required
def edit_registration(request, reg_id):
    if request.user.role != 'admin' and not request.user.is_superuser:
        return redirect('calendar_app:dashboard')
    
    registration = get_object_or_404(MatchRegistration, id=reg_id)
    
    if request.method == 'POST':
        # Handle AJAX inline edit
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
            # Update single field
            for field in ['team_name', 'discord_id', 'members']:
                if field in request.POST:
                    setattr(registration, field, request.POST[field])
            registration.save()
            from django.http import JsonResponse
            return JsonResponse({'status': 'success'})
        
        # Handle form submission
        form = MatchRegistrationForm(request.POST, instance=registration)
        if form.is_valid():
            form.save()
    
    return redirect('calendar_app:admin_registrations')

@login_required
def delete_registration(request, reg_id):
    if request.user.role != 'admin' and not request.user.is_superuser:
        return redirect('calendar_app:dashboard')
    
    registration = get_object_or_404(MatchRegistration, id=reg_id)
    
    if request.method == 'POST':
        registration.delete()
        messages.success(request, "Registration deleted successfully!")
    
    return redirect('calendar_app:admin_registrations')
