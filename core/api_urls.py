from django.urls import path, include

urlpatterns = [
    path('', include('user_auth_app.api.urls')),
    path('', include('kanban_app.api.urls'))
]