from django.urls import path
from . import views
from . import inquiry_views
from . import livechat_views as lc

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
    path('gov-platform/', views.gov_platform, name='gov_platform'),
    path('inquiry/', inquiry_views.check_internal_systems, name='inquiry'),
    path('api/inquiry/', inquiry_views.proxy_inquiry_api, name='inquiry_api'),

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
    path('dashboard/notifications-count/', views.dashboard_notifications_count, name='dashboard_notifications_count'),

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
    path('dashboard/users/<int:pk>/update-syndicate/', views.dashboard_user_update_syndicate, name='dashboard_user_update_syndicate'),

    # ── Medical Exams ──
    path('dashboard/medical-exams/', views.dashboard_medical_exams, name='dashboard_medical_exams'),
    path('dashboard/medical-exams/add/', views.dashboard_medical_exam_add, name='dashboard_medical_exam_add'),
    path('dashboard/medical-exams/<int:pk>/edit/', views.dashboard_medical_exam_edit, name='dashboard_medical_exam_edit'),
    path('dashboard/medical-exams/<int:pk>/delete/', views.dashboard_medical_exam_delete, name='dashboard_medical_exam_delete'),
    path('dashboard/medical-exams/<int:exam_pk>/image/<int:img_pk>/delete/', views.dashboard_medical_exam_image_delete, name='dashboard_medical_exam_image_delete'),

    # ── Institute ──
    path('dashboard/institute/', views.dashboard_institute, name='dashboard_institute'),
    path('dashboard/institute/add/', views.dashboard_institute_add, name='dashboard_institute_add'),
    path('dashboard/institute/<int:pk>/edit/', views.dashboard_institute_edit, name='dashboard_institute_edit'),
    path('dashboard/institute/<int:pk>/delete/', views.dashboard_institute_delete, name='dashboard_institute_delete'),
    path('run-migrations-secret/', views.run_migrations_view, name='run_migrations_secret'),
    path('seed-library-secret/', views.seed_library_view, name='seed_library'),
    path('seed-faqs-secret/', views.seed_faqs_view, name='seed_faqs'),
    path('media/db/<str:name>', views.serve_db_media, name='serve_db_media'),

    # ── Digital Library – Public ──
    path('api/upload-chunk/', views.upload_chunk_api, name='upload_chunk_api'),
    path('library/books/', views.library_books, name='library_books'),
    path('library/contracts/', views.library_contracts, name='library_contracts'),
    path('library/books/<int:pk>/action/', views.library_book_action, name='library_book_action'),
    path('library/contracts/<int:pk>/action/', views.library_contract_action, name='library_contract_action'),

    # ── Digital Library – Dashboard ──
    path('dashboard/library/', views.dashboard_library, name='dashboard_library'),
    path('dashboard/library/add/<str:section>/', views.dashboard_library_add, name='dashboard_library_add'),
    path('dashboard/library/edit/<str:section>/<int:pk>/', views.dashboard_library_edit, name='dashboard_library_edit'),
    path('dashboard/library/delete/<str:section>/<int:pk>/', views.dashboard_library_delete, name='dashboard_library_delete'),

    # ── Live Chat – User API ──
    path('api/chat/start/',         lc.chat_start,  name='chat_start'),
    path('api/chat/send/',          lc.chat_send,   name='chat_send'),
    path('api/chat/poll/',          lc.chat_poll,   name='chat_poll'),

    # ── Live Chat – Admin ──
    path('dashboard/livechat/',                              lc.dashboard_livechat,         name='dashboard_livechat'),
    path('dashboard/livechat/<str:session_key>/',            lc.dashboard_livechat_session, name='dashboard_livechat_session'),
    path('dashboard/livechat/<str:session_key>/join/',       lc.chat_admin_join,            name='chat_admin_join'),
    path('dashboard/livechat/<str:session_key>/reject/',     lc.chat_admin_reject,          name='chat_admin_reject'),
    path('dashboard/livechat/<str:session_key>/send/',       lc.chat_admin_send,            name='chat_admin_send'),
    path('dashboard/livechat/<str:session_key>/end/',        lc.chat_admin_end,             name='chat_admin_end'),
    path('dashboard/livechat/<str:session_key>/poll/',       lc.chat_admin_poll,            name='chat_admin_poll'),
    path('dashboard/livechat/waiting-count/',                lc.chat_admin_waiting_count,   name='chat_admin_waiting_count'),
]
