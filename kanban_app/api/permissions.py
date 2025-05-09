from rest_framework.permissions import BasePermission, SAFE_METHODS
from kanban_app.models import Board

class IsBoardMember(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        
        board_id = request.data.get('board')
        if not board_id:
            return False
        
        try:
            board = Board.objects.get(id=board_id)
        
        except Board.DoesNotExist:
            return False
        
        if not board.members.filter(id=request.user.id).exists():
            return False

        return True