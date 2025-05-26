from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from kanban_app.models import Board, Task, Comment
from kanban_app.api.permissions import IsTaskBoardMemberOrOwner, IsBoardMemberOrOwner, IsCommentAuthor
from django.db.models import Q, Count
from rest_framework.response import Response
from .serializers import BoardSerializer, BoardDetailSerializer, BoardUpdateSerializer, TaskSerializer, CommentSerializer
from rest_framework import generics
from rest_framework.generics import DestroyAPIView, ListAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

class BoardViewSet(ModelViewSet):
    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]

    def get_queryset(self):
        user = self.request.user
        action = self.action

        if action == 'list':
            return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
        else:
            return Board.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'create':
            return BoardSerializer
        elif self.action in ['update', 'partial_update']:
            return BoardUpdateSerializer
        return BoardDetailSerializer

class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMemberOrOwner]

    def list(self, request, *args, **kwargs):
        return Response({"detail": "Listing all Tasks is not allowd"}, status = 405)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='assigned-to-me')
    def assigned(self, request):
        tasks = Task.objects.filter(assignee=request.user).annotate(comments_count=Count('comments'))
        page = self.paginate_queryset(tasks)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

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
