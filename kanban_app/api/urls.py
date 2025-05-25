from django.urls import path
from .views import BoardListCreateView, BoardDetailView, TaskCreateView, TaskUpdateDestroyView, TaskCommentListCreateView, TaskCommentDestroyView, AssignedTasksListView,ToReviewTasksListView

urlpatterns = [
    path('boards/', BoardListCreateView.as_view(), name='board-list-create'),
    path('boards/<int:pk>/', BoardDetailView.as_view(), name='single-board-view'),
    path('tasks/', TaskCreateView.as_view(), name="task-create"),
    path('tasks/assigned-to-me/', AssignedTasksListView.as_view(), name='assigned-tasks'),
    path('tasks/reviewing/', ToReviewTasksListView.as_view(), name='reviewed-tasks'),
    path('tasks/<int:pk>/', TaskUpdateDestroyView.as_view(), name="task-update-destroy"),
    path('tasks/<int:task_id>/comments/', TaskCommentListCreateView.as_view(), name='task-comments'),
    path('tasks/<int:task_id>/comments/<int:comment_id>/', TaskCommentDestroyView.as_view(), name='comment-delete'),
]