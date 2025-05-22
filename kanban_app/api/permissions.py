from rest_framework.permissions import BasePermission, SAFE_METHODS
from kanban_app.models import Board


class IsTaskBoardMemberOrOwner(BasePermission):


    def has_object_permission(self, request, view, obj):
        board = obj.board

        if request.method == 'DELETE':
            return (
                board.owner == request.user or
                obj.created_by == request.user
            )

        return (
            board.owner == request.user or
            board.members.filter(id=request.user.id).exists()
        )
    
    def has_permission(self,request,view):
        if request.method == "POST":
            board_id = request.data.get('board')
            if not board_id:
                return False
            
            try: board = Board.objects.get(id=board_id)
            except Board.DoesNotExist:
                return False
            return (
                board.owner == request.user or
                board.members.filter(id=request.user.id).exists()
            )
        return True
    
    
class IsBoardMemberOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):

        if request.method == 'DELETE':
            return obj.owner == request.user
        
        return (
            obj.owner == request.user or
            obj.members.filter(id=request.user.id).exists()
        )
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
        
