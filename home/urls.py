
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.loginPage, name='login'),
    path('validate/', views.validate, name='validate'),
    path('validate/dashboard/', views.dashboard, name='dashboard'),
    path('validate/dashboard/index/', views.index, name='index'),
    # path('validate/homepage/', views.homepage, name='homepage'),
    path('api/get-quiz/', views.get_quiz, name='get_quiz'),
    path('api/result/', views.result, name='result'),
    path('history/', views.history, name='history'),
    path('quiz/', views.quiz, name='quiz'),
    path('api/save-remaining-time/', views.save_remaining_time,
         name='save_remaining_time'),
    path('skipquiz/', views.skip_quiz, name='skipquiz'),
    path('save_time', views.save_time, name='save_time'),
    path('mylearning/', views.my_learning, name='mylearning'),
    path('final/', views.final, name='final'),
    path('logout/', views.user_logout, name='logout'),
]


admin.site.site_header = "Switch Tech System Admin"
admin.site.site_title = "Switch Tech System Admin Portal"
admin.site.index_title = "Welcome to Admin Portal"
