from django.contrib import admin
from django.urls import path
from planner import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('new/', views.create_meeting, name='create_meeting'),
    path('add-input/', views.add_option_input, name='add_option_input'),

    # --- NOWA ŚCIEŻKA ---
    path('m/<uuid:meeting_id>/created/', views.meeting_success, name='meeting_success'),
    # --------------------

    path('m/<uuid:meeting_id>/', views.meeting_detail, name='meeting_detail'),
    path('m/<uuid:meeting_id>/results/', views.meeting_results, name='meeting_results'),
    path('vote/<int:option_id>/<str:choice>/', views.save_vote, name='vote'),
]