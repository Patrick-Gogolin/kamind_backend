from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from kanban_app.models import Board, Task, Comment
from kanban_app.api.permissions import IsTaskBoardMemberOrOwner, IsBoardMemberOrOwner, IsCommentAuthor
from django.db.models import Q, Count
from .serializers import BoardSerializer, BoardDetailSerializer, BoardUpdateSerializer, TaskSerializer, CommentSerializer
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.generics import DestroyAPIView, ListAPIView

class BoardListCreateView(ListCreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BoardUpdateSerializer
        return BoardDetailSerializer

class TaskCreateView(generics.CreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMemberOrOwner]

class TaskUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMemberOrOwner]

class TaskCommentListCreateView(ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMemberOrOwner]

    def get_queryset(self):
        task_id = self.kwargs.get('task_id')
        return Comment.objects.filter(task_id=task_id)
    
    def perform_create(self, serializer):
        task_id = self.kwargs.get('task_id')
        task = Task.objects.get(id=task_id)
        serializer.save(task=task)

class TaskCommentDestroyView(DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def get_object(self):
        task_id = self.kwargs.get('task_id')
        comment_id = self.kwargs.get('comment_id')
        return Comment.objects.get(id=comment_id, task=task_id)
    
class AssignedTasksListView(ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assignee=self.request.user).annotate(comments_count=Count('comments'))

class ToReviewTasksListView(ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(reviewer=self.request.user).annotate(comments_count=Count('comments'))
