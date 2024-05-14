from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

urlpatterns = [
    # path('login/', views.user_login, name='user_login'),
    # path('logout/', views.user_logout, name='user_logout'),
    path('roomcleaning/', views.roomcleaning, name='roomcleaning'),
    path('roomcleaning_add/', views.roomcleaning_add, name='roomcleaning_add'),
    path('survey_add/', views.survey_add, name='survey_add'),
    # Define other routes similarly
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_ROOT, document_root=settings.MEDIA_ROOT)
