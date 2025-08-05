from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from django.db import IntegrityError
from django.conf import settings
from .models import User, Profile
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from django.utils.translation import gettext as _


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, style={"input_type": "password"})

    # def validate(self, attrs):
    #     email = attrs.get("email")
    #     password = attrs.get("password")

    #     if email and password:
    #         user = authenticate(request=self.context.get("request"), email=email, password=password)

    #         if not user:
    #             msg = "Unable to log in with provided credentials."
    #             raise serializers.ValidationError(msg, code="authorization")

    #     else:
    #         msg = "Must include 'email' and 'password'."
    #         raise serializers.ValidationError(msg, code="authorization")

    #     attrs["user"] = user
    #     return attrs


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls,user):
        token = super().get_token(user)

        token['full_name'] = user.full_name
        token['email'] = user.email
        token['username'] = user.username

        try:
            token['vendor_id'] = user.vendor.id
        except:
            token['vendor_id'] = 0

        return token 
    
    
    
    
    


def validate_phone_number(value):
    if not value.startswith('01'):
        raise serializers.ValidationError({'phone':_('Phone number must start with "01".')})
    
def validate_full_name(value):
    if len(value) < 3:
        raise serializers.ValidationError({'full_name': 'Full name must be at least 3 characters long.'})
    elif len(value) > 30:
        #raise serializers.ValidationError({'full_name': 'Full name cannot be longer than 30 characters.'})
        return Response({'message': 'Full name cannot be longer than 30 characters.'}, status=status.HTTP_400_BAD_REQUEST)
def validate_email(value):
    if User.objects.filter(email=value).exists():
        return Response({'message': 'This email is already in use.'}, status=status.HTTP_400_BAD_REQUEST)

    
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True,validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)


    def validate_full_name_and_phone(self, attrs):
        full_name = attrs.get('full_name')
        phone = attrs.get('phone')
        email = attrs.get('email')
        validate_email(email)
        validate_full_name(full_name)
        validate_phone_number(phone)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'password', 'password2']

    def validate(self, attrs):
        self.validate_full_name_and_phone(attrs)
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"status": "error", "message":_("Password does not match")})
        return attrs
        
      
    def create(self, validated_data):
        value=validated_data['email'],

        if User.objects.filter(email=value).exists():
            return Response({'Message': _('This email is already used')}, status=status.HTTP_200_OK)
       
        else:
            user = User.objects.create(
                full_name=validated_data['full_name'],
                email=validated_data['email'],
                phone=validated_data['phone'], 
            )  
            email_user,_ = user.email.split("@")
            try:
                user.username = email_user
                print(f"email useername--------- {email_user}")
            except:
                Response({'Message': _('This email is already used')}, status=status.HTTP_200_OK)

            user.set_password(validated_data['password'])

            user.save()
            return user     


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'



class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = '__all__'


    def to_representation(self, instance):
        response =  super().to_representation(instance) 
        response['user'] = UserSerializer(instance.user).data
        return response   
    


class ProfileReviewSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Profile
        fields = ['id','full_name', 'image']