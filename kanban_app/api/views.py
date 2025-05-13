from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from kanban_app.models import Board, Task
from kanban_app.api.permissions import IsTaskBoardMemberOrOwner, IsBoardMemberOrOwner
from django.db.models import Q
from .serializers import BoardSerializer, BoardDetailSerializer, BoardUpdateSerializer, TaskSerializer
from rest_framework.response import Response
from rest_framework import generics


class BoardListCreateView(ListCreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()# zeige die Boards, die dem eingeloggten User gehören oder bei denen er Member ist

    def perform_create(self, serializer):
        serializer.save()

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