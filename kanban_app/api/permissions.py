from rest_framework.permissions import BasePermission, SAFE_METHODS
from kanban_app.models import Board


class isBoardOwner(BasePermission):
    def has_permission(self,request,view):
        if request.method in SAFE_METHODS:
            return True
        
        if request.method == "DELETE":

            task = view.get_object()
            board = task.board

            return board.owner == request.user



class IsBoardMember(BasePermission):
    def has_permission(self, request, view):
        # Wenn es eine sichere Methode ist (z. B. GET), darf jeder zugreifen
        if request.method in SAFE_METHODS:
            return True

        if request.method == "PATCH":

            task = view.get_object()

            if not task.board.members.filter(id=request.user.id).exists():
                return False

        # Wenn der Benutzer Mitglied ist, gebe Zugriff
            return True

        elif request.method == "POST":
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
