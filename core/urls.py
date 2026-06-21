from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # ── Public Pages ──
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('council/', views.council, name='council'),
    path('news/', views.news_list, name='news'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq_page, name='faq'),
    path('search/', views.search, name='search'),
    path('search/api/', views.search_api, name='search_api'),

    # ── New Services ──
    path('institute/', views.institute_page, name='institute'),
    path('forensic/', views.forensic_page, name='forensic'),
    path('medical-exams/<int:pk>/', views.medical_exam_detail, name='medical_exam_detail'),

    # ── Public Auth ──
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.user_profile, name='profile'),

    # ── Dashboard Auth ──
    path('dashboard/login/', views.dashboard_login, name='dashboard_login'),
    path('dashboard/logout/', views.dashboard_logout, name='dashboard_logout'),

    # ── Dashboard ──
    path('dashboard/', views.dashboard_home, name='dashboard_home'),
    path('dashboard/settings/', views.dashboard_settings, name='dashboard_settings'),

    path('dashboard/complaints/', views.dashboard_complaints, name='dashboard_complaints'),
    path('dashboard/complaints/<int:pk>/update/', views.dashboard_complaint_update, name='dashboard_complaint_update'),

    path('dashboard/news/', views.dashboard_news, name='dashboard_news'),
    path('dashboard/news/add/', views.dashboard_news_add, name='dashboard_news_add'),
    path('dashboard/news/<int:pk>/edit/', views.dashboard_news_edit, name='dashboard_news_edit'),
    path('dashboard/news/<int:pk>/delete/', views.dashboard_news_delete, name='dashboard_news_delete'),

    path('dashboard/council/', views.dashboard_council, name='dashboard_council'),
    path('dashboard/council/add/', views.dashboard_council_add, name='dashboard_council_add'),
    path('dashboard/council/<int:pk>/edit/', views.dashboard_council_edit, name='dashboard_council_edit'),
    path('dashboard/council/<int:pk>/delete/', views.dashboard_council_delete, name='dashboard_council_delete'),

    # ── Users ──
    path('dashboard/users/', views.dashboard_users, name='dashboard_users'),
    path('dashboard/users/<int:pk>/delete/', views.dashboard_user_delete, name='dashboard_user_delete'),
    path('dashboard/users/<int:pk>/change-password/', views.dashboard_user_change_password, name='dashboard_user_change_password'),

    # ── Medical Exams ──
    path('dashboard/medical-exams/', views.dashboard_medical_exams, name='dashboard_medical_exams'),
    path('dashboard/medical-exams/add/', views.dashboard_medical_exam_add, name='dashboard_medical_exam_add'),
    path('dashboard/medical-exams/<int:pk>/delete/', views.dashboard_medical_exam_delete, name='dashboard_medical_exam_delete'),
    path('dashboard/medical-exams/<int:exam_pk>/image/<int:img_pk>/delete/', views.dashboard_medical_exam_image_delete, name='dashboard_medical_exam_image_delete'),

    # ── Institute ──
    path('dashboard/institute/', views.dashboard_institute, name='dashboard_institute'),
    path('dashboard/institute/add/', views.dashboard_institute_add, name='dashboard_institute_add'),
    path('dashboard/institute/<int:pk>/edit/', views.dashboard_institute_edit, name='dashboard_institute_edit'),
    path('dashboard/institute/<int:pk>/delete/', views.dashboard_institute_delete, name='dashboard_institute_delete'),
    path('media/db/<str:name>', views.serve_db_media, name='serve_db_media'),
    path('run-migrations-secret/', views.run_migrations_view, name='run_migrations_view'),
]
