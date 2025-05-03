from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status 
from.serializers import RegistrationSerializer, EmailAuthTokenSerializer
from django.contrib.auth.models import User


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request): 
        serializer = RegistrationSerializer(data=request.data)

        data = {}
        if serializer.is_valid():
            try:
                saved_account = serializer.save()
                token, created = Token.objects.get_or_create(user=saved_account)

                data = {
                    'token': token.key,
                    'fullname': saved_account.first_name.capitalize() + ' ' + saved_account.last_name.capitalize(),
                    'email': saved_account.email,
                    'user_id': saved_account.id
                    }
                
                return Response(data, status=status.HTTP_201_CREATED)
            
            except:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailAuthTokenSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            try:
                user = serializer.validated_data['user']
                token, _ = Token.objects.get_or_create(user=user)
                full_name = f"{user.first_name} {user.last_name}"

                data = {
                    'token': token.key,
                    'email': user.email,
                    'fullname': full_name,
                    'user_id': user.id
                }

                return Response(data, status=status.HTTP_200_OK)
            
            except:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmailCheckView(APIView):
    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response("error", status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            return Response({
                'id': user.id,
                'email': user.email,
                'fullname': f'{user.first_name} {user.last_name}'
            },status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)