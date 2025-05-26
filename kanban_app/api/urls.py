from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import TaskCommentListCreateView, TaskCommentDestroyView, AssignedTasksListView,ToReviewTasksListView, BoardViewSet,TaskViewSet

router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='board')
router.register(r'tasks', TaskViewSet, basename='tasks')

urlpatterns = [
    #path('tasks/assigned-to-me/', AssignedTasksListView.as_view(), name='assigned-tasks'),
    path('tasks/reviewing/', ToReviewTasksListView.as_view(), name='reviewed-tasks'),
    path('tasks/<int:task_id>/comments/', TaskCommentListCreateView.as_view(), name='task-comments'),
    path('tasks/<int:task_id>/comments/<int:comment_id>/', TaskCommentDestroyView.as_view(), name='comment-delete'),
] + router.urls