from rest_framework import serializers
from .models import CustomUser as Userr
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
import json
from dataclasses import field
from rest_framework import serializers
from string import ascii_lowercase, ascii_uppercase
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import *
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework import serializers
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from .utils import *
from rest_framework import serializers
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed





class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    _id = serializers.SerializerMethodField(read_only=True)
    isAdmin = serializers.SerializerMethodField(read_only=True)



    




    class Meta:
        model = Userr
        fields = '__all__'



    def get__id(self, obj):
        return obj.id
    
    def get_isAdmin(self, obj):
        return obj.is_staff 
    
    
        
    def get_name(self, obj):
        name = obj.first_name
        if name == '':
            name = obj.email

        return name
    

    
    def get_avi(self, obj):
        avi = obj.avi


        return avi
  
# class UserSerializerWithToken(UserSerializer):
#     token = serializers.SerializerMethodField(read_only=True)

#     class Meta:
#         model = Userr
#         fields = ['id', '_id', 'username', 'email', 'name', 'isAdmin', 'bio', 'token']

#     def get_token(self, obj):
#         token = RefreshToken.for_user(obj)
#         return str(token.access_token)
    












from datetime import datetime
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
import jwt
from pytz import timezone  # Import timezone from pytz
from datetime import timedelta




class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)
    expiration_time = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Userr
        fields = ['id', '_id', 'username', 'email', 'name', 'isAdmin', 'bio', 'token', 'expiration_time']

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        print("Your Token is:", token)

        return str(token.access_token)

    def get_expiration_time(self, obj):
        token = RefreshToken.for_user(obj)
        access_token = str(token.access_token)
        decoded_token = jwt.decode(access_token, options={"verify_signature": False})  # Decode token without verification
        expiration_timestamp = decoded_token['exp']  # Get the expiration time from the decoded token
        expiration_datetime_utc = datetime.utcfromtimestamp(expiration_timestamp)  # Convert expiration timestamp to UTC datetime
        expiration_datetime_local = expiration_datetime_utc.astimezone(timezone('Africa/Nairobi'))  # Convert to Nairobi timezone
        expiration_datetime_local += timedelta(hours=3)  # Add three hours to the expiration time
        return expiration_datetime_local.strftime('%Y-%m-%d %H:%M:%S %Z')  # 




import os

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    def validate(self, attrs):
        email = attrs.get('email')
        user = Userr.objects.get(email=email)

            

        if Userr.objects.filter(email=email).exists():

            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            request = self.context.get('request')
            abslink = f"http://localhost:3000/#/password-reset-confirm/{uidb64}/{token}/"
            print(abslink)
            template_path = os.path.join(settings.BASE_DIR, 'base', 'email_templates', 'INTERVIEW.html')
            with open(template_path, 'r', encoding='utf-8') as template_file:
                html_content = template_file.read()

            # Send email
            email_data = {
                'email_subject': 'Reset Your Password',
                'email_body': html_content,
                'to_email': user.email,
                'context': {
                    'link': abslink,
                },
            }
            send_normal_email(email_data)

        return attrs




from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError



class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    confirm_password = serializers.CharField(max_length=100, min_length=6, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)
    token = serializers.CharField(min_length=3, write_only=True)

    class Meta:
        fields = ['password', 'confirm_password', 'uidb64', 'token']

    def validate(self, attrs):
        try:
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')
            password = attrs.get('password')
            confirm_password = attrs.get('confirm_password')

            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = Userr.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed("Reset link is invalid or has expired", 401)

            if password != confirm_password:
                raise AuthenticationFailed("Passwords do not match")

            # Validate password using Django's password validators
            try:
                validate_password(password, user)
            except ValidationError as e:
                raise ValidationError(detail=str(e))

            user.set_password(password)
            user.save()

            template_path = os.path.join(settings.BASE_DIR, 'base', 'email_templates', 'PassChange.html')
            with open(template_path, 'r', encoding='utf-8') as template_file:
                html_content = template_file.read()

            # Send email
            email_data = {
                'email_subject': 'Your Password Was Changed',
                'email_body': html_content,
                'to_email': user.email,

            }
            send_normal_email(email_data)

            return user
        except Exception as e:
            raise AuthenticationFailed("Link is invalid or has expired")



class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'




class TrashSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trash
        fields = ['photo',  'point',  'types'] 
        read_only_fields = ['verification_status', 'timestamp', 'types']




class CommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = '__all__'



class CommunityBlackListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityBlackList
        fields = '__all__'






class AdminAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminArea
        fields = '__all__'





class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = '__all__'



 



class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['report',  'points', ] 








class IndividualLeaderboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndividualLeaderboard
        fields = '__all__'






class CommunityLeaderboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityLeaderboard
        fields = '__all__'





class QuestionnaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questionnaire
        fields = '__all__'



class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'created_at', 'message', 'post', 'parent', 'replies']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []







class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = '__all__' 


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__' 





class PostSerializer(serializers.ModelSerializer):
    albums = PostImageSerializer(many=True, read_only=True)
    videos = VideoSerializer(many=True, read_only=True)



    uploaded_albums = serializers.ListField(
        child = serializers.ImageField(max_length = 1000000, allow_empty_file = False, use_url = False),
        write_only=True)
    likers = serializers.SerializerMethodField(read_only=True)
    comments = serializers.SerializerMethodField(read_only=True)
    total_likes = serializers.SerializerMethodField(read_only=True)
    total_comments = serializers.SerializerMethodField(read_only=True)
    user_avi = serializers.ImageField(read_only=True)
    user_name = serializers.CharField(read_only=True)




    class Meta:
        model = Post
        fields = '__all__' 





    def create(self, validated_data):
        uploaded_albums = validated_data.pop("uploaded_albums")
        post = Post.objects.create(**validated_data)
        for album in uploaded_albums:
            newpost_album = PostImage.objects.create(post=post, album=album)
        return post
        

        
        



    
    def get_likers(self, obj):
        likers = obj.like_set.all()
        serializer = LikeSerializer(likers, many=True)
        return serializer.data
    
    def get_comments(self, obj):
        comments = obj.comment_set.all()
        serializer = CommentSerializer(comments, many=True)
        return serializer.data

    
 

    def get_total_likes(self, obj):
        return obj.like_set.count()
    
    def get_total_comments(self, obj):
        return obj.comment_set.count()
         # Update with actual fields from the Product model



class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


