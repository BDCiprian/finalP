from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import UserProfile, WorkoutPlan
from .forms import UserRegistrationForm, ClientTrainerSelectForm, ReassignTrainerForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from datetime import date
from django.utils.timezone import now

def register(request):
    available_trainers = UserProfile.objects.filter(role='trainer', is_approved=True)
    trainers_exist = available_trainers.exists()
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        trainer_form = ClientTrainerSelectForm(request.POST) if trainers_exist else None
        if form.is_valid():
            

            role = form.cleaned_data['role']
            if role == 'client' and not trainers_exist:
                messages.error(request, "Momentan nu există antrenori disponibili. Înregistrarea ca client nu este posibilă.")
            else:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password1'])
                user.save()


                phone = form.cleaned_data['phone']
                profile = UserProfile.objects.create(user=user, role=role, phone=phone)

                if role == 'client':
                    if trainer_form and trainer_form.is_valid():
                        profile.trainer = trainer_form.cleaned_data['trainer']
                    profile.is_approved = True  # clienții nu au nevoie de aprobare
                    profile.save()
                    return redirect('login')

                elif role == 'trainer':
                    profile.is_approved = False  # antrenorii trebuie aprobați
                    profile.save()
                    return render(request, 'registration_pending.html')

    else:
        form = UserRegistrationForm()
        trainer_form = ClientTrainerSelectForm() if trainers_exist else None

    context = {
            'form': form,
            'trainer_form': trainer_form,
            'trainers_exist': trainers_exist,
        }
    return render(request, 'register.html', context)

def login_view(request):
    error = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            try:
                profile = UserProfile.objects.get(user=user)

                if user.is_staff or profile.role == 'admin':
                    login(request, user)
                    return redirect('admin_dashboard')

                if profile.role == 'trainer' and not profile.is_approved:
                    error = "Contul tău de antrenor nu a fost încă aprobat."
                else:
                    login(request, user)
                    if profile.role == 'trainer':
                        return redirect('trainer_dashboard')
                    else:
                        return redirect('client_dashboard')
            except UserProfile.DoesNotExist:
                error = "Profilul utilizatorului nu există."
        else:
            error = "Date de autentificare invalide."

    return render(request, 'login.html', {'error': error})


EXERCISES = [
    # Piept
    "Împins cu bara la piept (bench press)",
    "Împins cu gantere la piept",
    "Fluturări cu gantere",
    "Fluturări la cabluri",
    "Pec Deck",

    # Spate
    "Tracțiuni la bară fixă",
    "Ramat cu bara",
    "Ramat cu gantere",
    "Ramat la aparat",
    "Tracțiuni la helcometru",

    # Umeri
    "Împins militar cu bara",
    "Împins cu gantere deasupra capului",
    "Ridicări laterale cu gantere",
    "Ridicări frontale cu gantere",
    "Ridicări cu bara la bărbie",

    # Biceps
    "Flexii cu bara Z",
    "Flexii cu gantere alternante",
    "Flexii la cablu",
    "Flexii concentrate",
    "Flexii hammer",

    # Triceps
    "Extensii la helcometru",
    "Extensii cu gantera deasupra capului",
    "Flotări la paralele",
    "Kickback cu gantera",

    # Picioare
    "Genuflexiuni cu bara",
    "Presă pentru picioare",
    "Fandări cu gantere",
    "Extensii pentru cvadricepși",
    "Flexii pentru femurali",
    "Îndreptări românești",
    "Ridicări pe vârfuri (gambe)",

    # Abdomen
    "Abdomene clasice",
    "Crunch-uri",
    "Plank",
    "Plank lateral",
    "Ridicări de picioare",
    "Abdomene la aparat",

    # Cardio
    "Alergare pe bandă",
    "Bicicletă staționară",
    "Stepper",
    "Eliptică",
    "Sărituri cu coarda",
    "HIIT (intervale)",
    "Rowing machine",

    # Funcțional & Full body
    "Burpees",
    "Mountain climbers",
    "Kettlebell swing",
    "Box jumps",
    "Battle ropes",
    "Sled push/pull",
    "Bear crawl",

    # Mobilitate & Stretching
    "Stretching picioare",
    "Stretching spate",
    "Stretching umeri",
    "Yoga flow",
    "Mobilitate șolduri",
    "Rotiri trunchi",

    # Alte exerciții populare
    "Deadlift (îndreptări)",
    "Snatch",
    "Clean & Jerk",
    "Wall sit",
    "Jumping jacks",
    "Farmer's walk",
    "Scândura cu ridicare alternativă a brațelor",
    "Tors rotation"
]


@login_required
def trainer_dashboard(request):
    user = request.user
    profile = UserProfile.objects.get(user=user)

    if profile.role != 'trainer':
        return redirect('client_dashboard')

    # obține clienții care lucrează cu acest antrenor
    clients = UserProfile.objects.filter(role='client', trainer=profile)

    # salvează modificările trimise prin POST
    if request.method == 'POST':
        client_id = request.POST.get('client_id')
        date_str = request.POST.get('date')
        workout = request.POST.get('workout')

        client = User.objects.get(id=client_id)


        if date_str:
            selected_date = date.fromisoformat(date_str)

            if selected_date >= date.today():
                plan, created = WorkoutPlan.objects.update_or_create(
                    client=client,
                    date=selected_date,
                    defaults={'trainer': user, 'workout_description': workout}
                )
                messages.success(request, f'Planul de antrenament pentru {selected_date} a fost salvat cu succes.')
            else:
                messages.error(request, 'Nu poți adăuga un plan de antrenament pentru o dată din trecut.')

    # toate planurile existente pentru a le afișa în formulare
    workout_plans = WorkoutPlan.objects.filter(trainer=user, date__gte=now().date()).order_by('date')
    return render(request, 'trainer_dashboard.html', {
        'clients': clients,
        'plans': workout_plans,
        'today': date.today().isoformat(),
        'exercises': EXERCISES,
    })
@login_required
def client_dashboard(request):
    user = request.user
    profile = UserProfile.objects.get(user=user)

    if profile.role != 'client':
        return redirect('trainer_dashboard')

    workout_plans = WorkoutPlan.objects.filter(client=user).order_by('date')


    return render(request, 'client_dashboard.html', {
        'trainer': profile.trainer,
        'plans': workout_plans,
    })




@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def admin_dashboard(request):
    pending_trainers = UserProfile.objects.filter(role='trainer', is_approved=False)
    all_trainers = UserProfile.objects.filter(role='trainer')
    all_clients = UserProfile.objects.filter(role='client')
    
    context = {
        'pending_trainers': pending_trainers,
        'all_trainers': all_trainers,
        'all_clients': all_clients,
    }
    return render(request, 'admin_dashboard.html', context)

@user_passes_test(is_admin)
def approve_trainer(request, user_id):
    trainer = get_object_or_404(UserProfile, user__id=user_id, role='trainer')
    trainer.is_approved = True
    trainer.save()
    return redirect('admin_dashboard')

@user_passes_test(is_admin)
def reject_trainer(request, user_id):
    # șterge User și profilul asociat
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('admin_dashboard')

@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('admin_dashboard')

@login_required
def delete_workout(request, plan_id):
    plan = get_object_or_404(WorkoutPlan, id=plan_id)

    if plan.trainer == request.user:
        plan.delete()
        messages.success(request, "Planul de antrenament a fost șters cu succes.")
    else:
        messages.error(request, "Nu ai permisiunea să ștergi acest antrenament.")

    return redirect('trainer_dashboard')

@login_required
def reassign_trainer(request):
    profile = UserProfile.objects.get(user=request.user)

    if profile.role != 'client':
        return redirect('trainer_dashboard')

    if request.method == 'POST':
        form = ReassignTrainerForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('client_dashboard')
    else:
        form = ReassignTrainerForm(instance=profile)

    return render(request, 'reassign_trainer.html', {'form': form})


