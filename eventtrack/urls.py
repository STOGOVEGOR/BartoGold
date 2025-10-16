from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('housekeep/', include('housekeep.urls')),
    # path('webhook/', views.webhook, name='webhook'),
    path('', views.index, name='index'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    # path('register/', views.register, name='register'),
    # path('take5/', views.take5, name='take5'),
    path('safe_acts/', views.safe_acts, name='safe_acts'),
    path('upload_xls/', views.upload_xls, name='upload_xls'),
    path('staff_status/', views.staff_status, name='staff_status'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # path('get_tanks_data/', views.get_tanks_data, name='get_tanks_data')
    # Define other routes similarly
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_ROOT, document_root=settings.MEDIA_ROOT)
