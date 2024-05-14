from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import os
from shutil import copyfile
from django.db.models.signals import post_save
from django.dispatch import receiver
class User(AbstractUser):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('admin', 'Администратор'),
    ]
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='user')



class Movie1(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    poster = models.ImageField(upload_to='movie_posters', null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    genre = models.CharField(max_length=100, null=True, blank=True)
    director = models.CharField(max_length=100, null=True, blank=True)
    screenplay = models.CharField(max_length=100, null=True, blank=True)
    producer = models.CharField(max_length=100, null=True, blank=True)
    cinematography = models.CharField(max_length=100, null=True, blank=True)
    composer = models.CharField(max_length=100, null=True, blank=True)
    production_designer = models.CharField(max_length=100, null=True, blank=True)
    editor = models.CharField(max_length=100, null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    def __str__(self):
        return self.title

class Session(models.Model):
    movie = models.ForeignKey(Movie1, on_delete=models.CASCADE, null=True, blank=True)
    start_datetime = models.DateTimeField()
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    STATUS_CHOICES = [
        ('purchased', 'Куплен'),
        ('canceled', 'Отменен'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    row_number = models.IntegerField()
    seat_number = models.IntegerField()
    ticket_count = models.IntegerField(default = 1)
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie1, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    rating = models.IntegerField()


@receiver(post_save, sender=Booking)
def increment_ticket_count(sender, instance, created, **kwargs):
    if created:  # Проверяем, создана ли новая запись
        instance.ticket_count += 1  # Увеличиваем значение ticket_count на 1
        instance.save()  # Сохраняем изменения в объекте Session


@receiver(post_save, sender=Movie1)
def save_movie_poster(sender, instance, **kwargs):
    if instance.poster:  # Проверяем, что у фильма есть постер
        # Путь к папке медиа файлов
        media_folder = os.path.join(settings.BASE_DIR, 'media', 'movie_posters')
        # Создаем папку медиа файлов, если она не существует
        os.makedirs(media_folder, exist_ok=True)
        # Путь к файлу изображения в папке медиа файлов
        poster_name = instance.poster.name[-1]
        image_path = os.path.join(media_folder, poster_name)
        # Копируем файл изображения в папку медиа файлов
        copyfile(instance.poster.path, image_path)