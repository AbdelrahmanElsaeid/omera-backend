from django.shortcuts import render
from django.conf import settings
from .models import User, Profile
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializer import MyTokenObtainPairSerializer ,RegisterSerializer, UserSerializer,ProfileSerializer,LoginSerializer
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
import random
import shortuuid
from django.core.mail import send_mail
from django.urls import reverse
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.contrib.auth import login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
import jwt, datetime
from django.views.decorators.csrf import get_token
from django.http import JsonResponse
#from django.utils.translation import gettext as _



def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})

class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            #aise AuthenticationFailed('User not found!')
            return Response({"status": "Error","message": _("Invalid Email or password")}, status=status.HTTP_200_OK)

        if not user.check_password(password):
            #raise AuthenticationFailed('Incorrect password!')
            return Response({"status": "Error","message": _("Invalid Email or password")}, status=status.HTTP_200_OK)

        refresh = RefreshToken.for_user(user)


        # Add additional data to the access token payload
        refresh.payload['full_name'] = user.full_name
        refresh.payload['email'] = user.email
        refresh.payload['username'] = user.username
        refresh.payload['vendor_id'] = user.vendor.id if hasattr(user, 'vendor') else 0

    

        return Response({
            'status': 'success', 
            'message': _("login successfully"), 
            "tokens":{ 
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            }
            
        }, status=status.HTTP_200_OK)











class MyTokenOptainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        tokens = serializer.validated_data
        response_data = {
            'tokens': tokens,
            'user': {
                'id': user.id,
                'full_name': user.full_name,
                'email': user.email,
                'username': user.username,
                # Add more user information as needed
            }
        }

    
        return Response(response_data)
        #return Response(response_data)

    
from django.utils.translation import gettext as _
   
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny,]
    serializer_class = RegisterSerializer 


    def create(self, request, *args, **kwargs):
        email = request.data.get('email')

        email_user, _ = email.split("@")

        from django.utils.translation import gettext as _



        if User.objects.filter(email=email).exists():
            return Response({'status': 'error','message': _('This email is already used')}, status=status.HTTP_200_OK)
            #return Response({'status': 'error','message':mes}, status=status.HTTP_200_OK)


        
        if User.objects.filter(username=email_user).exists(): 
        
            #return Response({'status': 'error','message': 'This email is already used.'}, status=status.HTTP_200_OK)
            return Response({'status': 'error','message': _('This email is already used')}, status=status.HTTP_200_OK)

        


        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        from django.utils.translation import gettext as _

        return Response({'message': _('User created successfully.'), 'status': 'success', 'data': serializer.data}, status=status.HTTP_201_CREATED)

    

    def perform_create(self, serializer):
        email = serializer.validated_data['email']
        user = User.objects.create(
            full_name=serializer.validated_data['full_name'],
            email=email,
            phone=serializer.validated_data['phone'], 
        )
        email_user, _ = email.split("@")
                
        user.username = email_user
        user.set_password(serializer.validated_data['password'])
        user.save()








def generate_otp():
    uuid_key = shortuuid.uuid()
    unique_key = uuid_key[:6]
    return unique_key

  


class PasswordRestEmailVerify(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny, )

    def create(self, request, *args, **kwargs):
        #email = self.kwargs['email']
        email=self.request.data['email']
        link_url = self.request.data['link']
        try:
            user = User.objects.get(email=email)
        except:
            
            return Response({"status": "error", "message":_("This Email isn't exist")}, status=status.HTTP_200_OK)     

        if user:
            user.otp= generate_otp()
            user.save()

            uidb64 = user.pk
            otp = user.otp

            link = f"{link_url}/create-new-password?otp={otp}&uidb64={uidb64}"
            # print(link)
            #link = reverse('create-new-password') + f'?otp={otp}&uidb64={uidb64}'

            email_subject = 'Reset Your Password'
            email_body = f'Please follow this link to reset your password: {link}'

            send_mail(
                email_subject,
                email_body,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
           

            

        return Response({'status':'success','message': _("Check Your Email")}, status=status.HTTP_201_CREATED)    


class PasswordChangeView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny, )        

    def create(self,request, *args, **kwargs):
        payload = request.data

        otp = payload['otp']
        uidb64 = payload['uidb64']
        password = payload['password']
        password2 = payload['password2']
        if password != password2:
            return Response({"status": "error", "message":_("Password does not match")}, status=status.HTTP_200_OK)


        user = User.objects.get(otp=otp, id=uidb64)

        if user:
            user.set_password(password)
            user.otp= ""
            user.save()
            return Response({"message": _("Password Changed Successfully")}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": _("User Does Not Exists")}, status=status.HTTP_404_NOT_FOUND)





class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class=ProfileSerializer
    permission_classes = [AllowAny,]

    def get_object(self):
        user_id = self.kwargs['user_id']

        user = User.objects.get(id=user_id)
        profile = Profile.objects.get(user=user)

        return profile