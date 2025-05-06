from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from ..models import Board
from .serializers import BoardSerializer
from rest_framework.response import Response
from rest_framework import generics

class BoardListCreateView(ListCreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Board.objects.filter(owner=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save()