from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.login_view, name='login'),
    path('trainer/', views.trainer_dashboard, name='trainer_dashboard'),
    path('client/', views.client_dashboard, name='client_dashboard'),
    path('logout/', views.logout_view, name='logout'),  
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve-trainer/<int:user_id>/', views.approve_trainer, name='approve_trainer'),
    # ruta nouă pentru respingere antrenor
    path('reject_trainer/<int:user_id>/', views.reject_trainer, name='reject_trainer'),

    # rute pentru ștergere antrenor/client
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('delete_workout/<int:plan_id>/', views.delete_workout, name='delete_workout'),
    path('reassign_trainer/', views.reassign_trainer, name='reassign_trainer'),

]
