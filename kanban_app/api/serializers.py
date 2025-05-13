from rest_framework import serializers
from ..models import Board, Task
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']
    
    def get_fullname(self, obj):
        fullname = obj.first_name + " " + obj.last_name
        return fullname

class TaskSerializer(serializers.ModelSerializer):
    assignee_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority',
            'assignee_id', 'reviewer_id', 'assignee', 'reviewer',
            'due_date'
        ]
        read_only_fields = ['id', 'assignee', 'reviewer']
    
    def validate(self, data):
        request_user = self.context['request'].user
        board = data.get('board')

        if not board:
            task = self.context['view'].get_object()
            board = task.board
            print(board)

        if not board.members.filter(id=request_user.id).exists():
            raise serializers.ValidationError("Not a member of the board")

        assignee_id = data.get('assignee_id')
        reviewer_id = data.get('reviewer_id')

        if assignee_id and not board.members.filter(id=assignee_id).exists():
            raise serializers.ValidationError("Assignee is not a member of the board")
        
        if reviewer_id and not board.members.filter(id=reviewer_id).exists():
            raise serializers.ValidationError("Reviewer is not a member of the board")
        
        return data
    
    def create(self, validated_data):
        print(validated_data)
        assignee_id = validated_data.pop('assignee_id', None)
        reviewer_id = validated_data.pop('reviewer_id', None)

        assignee = User.objects.get(id=assignee_id) if assignee_id else None
        reviewer = User.objects.get(id=reviewer_id) if reviewer_id else None

        task = Task.objects.create(**validated_data, assignee=assignee, reviewer=reviewer)
        return task

class BoardSerializer(serializers.ModelSerializer):
    members = serializers.ListField( 
        child=serializers.IntegerField(),
        write_only=True) #Ein Feld namens members, das eine Liste von Zahlen (IDs der Benutzer) erwartet. Es ist write_only, d. h. es wird nur beim Schreiben (z. B. Erstellen) verwendet, nicht beim Auslesen
    
    member_count = serializers.SerializerMethodField(read_only=True)# Ein Feld, das später berechnet wird – hier die Anzahl der Mitglieder. Es ist nur zum Lesen gedacht.
    ticket_count = serializers.SerializerMethodField(read_only=True)# Ein weiteres berechnetes Feld: die Anzahl der „Tickets“ (z. B. Aufgaben) auf dem Board.
    tasks_to_do_count = serializers.SerializerMethodField(read_only=True)# Noch zwei berechnete Felder, derzeit aber noch nicht implementiert – Rückgabe ist einfach 0.
    tasks_high_prio_count = serializers.SerializerMethodField(read_only=True)# Noch zwei berechnete Felder, derzeit aber noch nicht implementiert – Rückgabe ist einfach 0.
    #owner_id = serializers.IntegerField(source='owner.id', read_only=True)# Zeigt die ID des Besitzers des Boards an. Sie wird automatisch aus owner.id gelesen.

    class Meta: #Hier sagen wir: Dieser Serializer basiert auf dem Modell Board und gibt genau diese Felder aus.
        model = Board
        fields = [
            'id', 'title', 'members',
            'member_count', 'ticket_count',
            'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id'
        ]

    def get_member_count(self, obj): #Zählt, wie viele Mitglieder das Board hat.
        return obj.members.count()
    
    def get_ticket_count(self, obj): #Zählt, wie viele „Tickets“ mit dem Board verknüpft sind (wenn es welche gibt).
        return obj.tasks.count()
    
    def get_tasks_to_do_count(self, obj): #Hier ist Platz für zukünftige Logik, z. B. um offene Aufgaben zu zählen.
        return obj.tasks.filter(status='todo').count()
    
    def get_tasks_high_prio_count(self, obj): #Auch hier: Kann später angepasst werden, um z. B. Aufgaben mit hoher Priorität zu zählen.
        return obj.tasks.filter(priority='high').count()

    def create(self, validated_data):#Diese Methode wird aufgerufen, wenn ein neues Board erstellt wird:, validated_data enthält alle geprüften Daten, die vom Client gesendet wurden (z. B. per API)
        members_ids = validated_data.pop('members')#pop('members') holt sich den Eintrag 'members' und entfernt ihn gleichzeitig aus validated_data, Weil wir members nicht direkt an Board.objects.create() übergeben wollen, sondern es manuell später
        owner = self.context['request'].user #gibt den aktuell eingeloggten Benutzer zurück – also den Ersteller des Boards.
        if owner.id not in members_ids:
            members_ids.append(owner.id)
        users = User.objects.filter(id__in=members_ids)
        if len(users) != len(set(members_ids)):
            raise serializers.ValidationError("Ein oder mehrere benutzer existieren nicht")
        board = Board.objects.create(title=validated_data['title'], owner=owner)#Ein neues Board-Objekt wird erstellt.,title wird aus dem verbleibenden validated_data geholt., owner ist der aktuelle Benutzer (aus Zeile 2).
        board.members.set(users)# board.members ist eine ManyToMany-Beziehung., .set(...) ersetzt die bestehenden Mitglieder mit einer neuen Liste von Benutzern. User.objects.filter(id__in=members_ids) sucht alle Benutzer, deren ID in der Liste members_ids enthalten ist.
        return board

class BoardDetailSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    class Meta:
        model = Board
        fields = [
            'id', 'title', 'owner_id', 'members', 'tasks'
        ]

class BoardUpdateSerializer(serializers.ModelSerializer):
    members = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    owner_data = UserSerializer(source='owner', read_only=True)
    members_data = UserSerializer(source='members', many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'owner_data', 'members_data']

    def update(self, instance, validated_data):
        members_ids = validated_data.pop('members', [])

        owner_id = instance.owner.id
        if owner_id not in members_ids:
            members_ids.append(owner_id)

        users = User.objects.filter(id__in=members_ids)
        if len(users) != len(set(members_ids)):
            raise serializers.ValidationError("Ein oder mehrere Benutzer Ids sind ungültig")
        
        instance.title = validated_data.get('title', instance.title)
        instance.save()
        instance.members.set(users)
        return instance
