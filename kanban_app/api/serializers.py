from rest_framework import serializers
from ..models import Board
from django.contrib.auth.models import User



class BoardSerializer(serializers.ModelSerializer):
    members = serializers.ListField( #Ein Feld namens members, das eine Liste von Zahlen (IDs der Benutzer) erwartet. Es ist write_only, d. h. es wird nur beim Schreiben (z. B. Erstellen) verwendet, nicht beim Auslesen
        child=serializers.IntegerField(),
        write_only=True
    )
    
    member_count = serializers.SerializerMethodField(read_only=True)# Ein Feld, das später berechnet wird – hier die Anzahl der Mitglieder. Es ist nur zum Lesen gedacht.
    ticket_count = serializers.SerializerMethodField(read_only=True)# Ein weiteres berechnetes Feld: die Anzahl der „Tickets“ (z. B. Aufgaben) auf dem Board.
    tasks_to_do_count = serializers.SerializerMethodField(read_only=True)# Noch zwei berechnete Felder, derzeit aber noch nicht implementiert – Rückgabe ist einfach 0.
    tasks_high_prio_count = serializers.SerializerMethodField(read_only=True)# Noch zwei berechnete Felder, derzeit aber noch nicht implementiert – Rückgabe ist einfach 0.
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)# Zeigt die ID des Besitzers des Boards an. Sie wird automatisch aus owner.id gelesen.

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
        return obj.ticket_set.count() if hasattr(obj, 'ticket_set') else 0
    
    def get_tasks_to_do_count(self, obj): #Hier ist Platz für zukünftige Logik, z. B. um offene Aufgaben zu zählen.
        return 0  # Implementiere bei Bedarf
    
    def get_tasks_high_prio_count(self, obj): #Auch hier: Kann später angepasst werden, um z. B. Aufgaben mit hoher Priorität zu zählen.
        return 0  # Implementiere bei Bedarf

    def create(self, validated_data):#Diese Methode wird aufgerufen, wenn ein neues Board erstellt wird:, validated_data enthält alle geprüften Daten, die vom Client gesendet wurden (z. B. per API)
        members_ids = validated_data.pop('members')#pop('members') holt sich den Eintrag 'members' und entfernt ihn gleichzeitig aus validated_data, Weil wir members nicht direkt an Board.objects.create() übergeben wollen, sondern es manuell später
        owner = self.context['request'].user #gibt den aktuell eingeloggten Benutzer zurück – also den Ersteller des Boards.
        users = User.objects.filter(id__in=members_ids)
        if len(users) != len(set(members_ids)):
            raise serializers.ValidationError("Ein oder mehrere benutzer existieren nicht")
        board = Board.objects.create(title=validated_data['title'], owner=owner)#Ein neues Board-Objekt wird erstellt.,title wird aus dem verbleibenden validated_data geholt., owner ist der aktuelle Benutzer (aus Zeile 2).
        board.members.set(users)# board.members ist eine ManyToMany-Beziehung., .set(...) ersetzt die bestehenden Mitglieder mit einer neuen Liste von Benutzern. User.objects.filter(id__in=members_ids) sucht alle Benutzer, deren ID in der Liste members_ids enthalten ist.
        return board