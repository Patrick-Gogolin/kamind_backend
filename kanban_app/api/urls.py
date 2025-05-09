from django.urls import path
from .views import BoardListCreateView, BoardDetailView, TaskCreateView

urlpatterns = [
    path('boards/', BoardListCreateView.as_view(), name='board-list-create'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='single-board-view'),
    path('tasks/', TaskCreateView.as_view(), name="task-create")

]