from django.shortcuts import render
from django.utils import timezone

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import UserRegistrationForm
from .forms import MovieForm
from .forms import LoginForm
from .models import User
from .models import Movie1
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import Session
from .models import Booking
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
@login_required
@csrf_exempt
def book_seat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            user_id = request.user.id  # Предполагая, что пользователь аутентифицирован
            selected_seats = data.get('selected_seats', [])

            session = get_object_or_404(Session, id=session_id)
            user = get_object_or_404(User, id=user_id)

            for seat_info in selected_seats:
                row_number = seat_info.get('row')
                seat_number = seat_info.get('seat')

                # Create a booking record
                Booking.objects.create(
                    user=user,
                    session=session,
                    row_number=row_number,
                    seat_number=seat_number,
                    status='purchased'
                )

            return JsonResponse({'success': True})

        except Exception as e:
            print(e)  # Выводим информацию об ошибке в консоль
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

def add_movie(request):
    if request.user.role != 'admin':
        return redirect('home')  # Предположим, что у вас есть представление 'home'

    if request.method == 'POST':
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
            movie = form.save(commit=False)
            movie.save()
            return redirect('home')  # Предположим, что у вас есть представление 'home'
    else:
        form = MovieForm()
    return render(request, 'add_movie.html', {'form': form})

def load_movies(request):
    movies = Movie1.objects.all()
    data = [{'title': movie.title, 'poster': movie.poster.url} for movie in movies]
    return JsonResponse(data, safe=False)
def movie_list(request):
    movies = Movie1.objects.all()
    return render(request, 'home.html', {'movies': movies})



import json


def movie_details(request, movie_id):
    movie = get_object_or_404(Movie1, pk=movie_id)
    sessions = Session.objects.filter(movie=movie)

    if request.method == 'POST':
        session_id = request.POST.get('session_id')
        row_number = request.POST.get('row_number')
        seat_number = request.POST.get('seat_number')
        status = request.POST.get('status')
        user = request.user

        booking = Booking.objects.create(
            user=user,
            session_id=session_id,
            row_number=row_number,
            seat_number=seat_number,
            status=status
        )

        session = Session.objects.get(pk=session_id)
        session.available_seats -= 1
        session.save()

        return JsonResponse({'success': True})

    booked_seats = {}
    for session in sessions:
        bookings = Booking.objects.filter(session=session)
        booked_seats[session.id] = [{'row': booking.row_number, 'seat': booking.seat_number} for booking in bookings]

    context = {
        'movie': movie,
        'sessions': sessions,
        'booked_seats': booked_seats
    }
    return render(request, 'movie_details.html', context)
@csrf_exempt
def book_seat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            user_id = request.user.id  # Assuming the user is authenticated
            selected_seats = data.get('selected_seats', [])

            session = get_object_or_404(Session, id=session_id)
            user = get_object_or_404(User, id=user_id)

            for seat_info in selected_seats:
                row_number = seat_info.get('row')
                seat_number = seat_info.get('seat')

                # Create a booking record
                Booking.objects.create(
                    user=user,
                    session=session,
                    row_number=row_number,
                    seat_number=seat_number,
                    status='purchased'
                )

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

def my_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            # Действия для администратора
            return render(request, 'admin_page.html')
        else:
            # Действия для обычного пользователя
            return render(request, 'normal_user_page.html')
    else:
        # Если пользователь не аутентифицирован, перенаправляем его на страницу входа
        return redirect('login.html')

def create_account(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Начало сессии для пользователя
            login(request, user)
            return redirect('home')  # Перенаправление на домашнюю страницу
    else:
        form = UserRegistrationForm()
    return render(request, 'registration.html', {'form': form})

def add_movie(request):
    return render(request, 'add_movie.html')
from django.contrib.auth import get_user_model

def authorization3(request):
    message = ''
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        # Фильтрация пользователей по email и паролю
        users = User.objects.filter(email=email, password=password)
        if users.exists():
            # Получение первого пользователя из отфильтрованного списка
            user = users.first()
            # Логин пользователя
            login(request, user)
            # Ваша логика с сеансами
            # Например, обновление даты последнего входа
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])

            if user.is_superuser:
                # Если пользователь администратор, перенаправляем на страницу администратора
                return redirect('admin:index')
            else:
                # Если пользователь не администратор, перенаправляем на другую страницу
                return redirect('home')  # Измените 'home' на URL вашей целевой страницы
        else:
            message = 'Invalid email or password.'
    return render(request, 'authorization.html', {'message': message})


def user_logout(request):
    logout(request)
    return redirect('home')  # Перенаправление на главную страницу или любую другую страницу
