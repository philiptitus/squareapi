from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import generics
from base.serializers import *
from django.db import IntegrityError
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from ..models import CustomUser  as Userr
from ast import Expression
from multiprocessing import context
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
       def validate(self, attrs: dict[str, any]) -> dict[str, str]:
        data = super().validate(attrs)
        serializer = UserSerializerWithToken(self.user).data

        for k, v in serializer.items():
            data[k] = v



        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer








from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from django.db.models import Q







from django.db.models import Case, When, Value, IntegerField

from django.db.models import Q, F
from rest_framework.pagination import PageNumberPagination

from rest_framework.pagination import PageNumberPagination

from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.db.models import Q

from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

# Create your views here.



class MyLoginView(TokenObtainPairView):
        serializer_class = MyTokenObtainPairSerializer

        # No need for JWT authentication logic here
        # No need to generate JWT token or expiration time

        # Return the default response provided by the parent class



@permission_classes([IsAuthenticated])
class GetUsersView(APIView):
    def get(self, request):
        # Check if the requesting user is either admin or staff
        if request.user.user_type not in ['admin']:
            return Response({'detail': 'Only Admins are allowed to view users.'}, status=status.HTTP_403_FORBIDDEN)

        # Fetch all users
        users = Userr.objects.all()

        # Filter out the current user
        users = users.exclude(id=request.user.id)

        # Filter users by hostel if hostel_id is provided

        users = users.filter(area = request.user.area)

        # Apply name search if provided
        name = request.query_params.get('name')
        if name:
            users = users.filter(Q(username__icontains=name) | Q(email__icontains=name) | Q(user_type__icontains=name)).exclude(user_type="admin")

        # Paginate the results
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(users, request)

        # Serialize the paginated users
        serializer = UserSerializer(result_page, many=True)

        # Return paginated response
        return paginator.get_paginated_response(serializer.data)

from rest_framework.exceptions import PermissionDenied

@permission_classes([IsAuthenticated])
class GetUserById(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = Userr.objects.get(id=pk)
        serializer = UserSerializer(user)

        # Check if the requesting user is the same as the requested user
        if request.user.id == user.id:
            return Response(serializer.data)



        # Check if the requesting user is a student and is trying to access themselves
        if request.user.user_type == 'normal' and request.user.id == user.id:
            return Response(serializer.data)

        # If none of the conditions are met, raise PermissionDenied
        raise PermissionDenied("You do not have permission to access this user's profile.")

from django.db.models import Subquery


class UserNotices(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Retrieve the IDs of the latest five unread notices for the authenticated user
        latest_five_notice_ids = list(Notice.objects.filter(user=user, is_read=False).order_by('-created_at').values_list('id', flat=True)[:5])

        if latest_five_notice_ids:
            # Update the is_read field for these notices
            Notice.objects.filter(id__in=latest_five_notice_ids).update(is_read=True)

        # Retrieve the updated notices
        notices = Notice.objects.filter(id__in=latest_five_notice_ids).order_by('-created_at')

        # Paginate the notices
        paginator = PageNumberPagination()
        paginator.page_size = 5  # Set the number of notices per page to 5
        result_page = paginator.paginate_queryset(notices, request)

        # Serialize the notices
        serializer = NoticeSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
from rest_framework.response import Response
from rest_framework.views import APIView

class uploadImage(APIView):
    def post(self, request):
        try:
            data = request.data

            user_id = data['user_id']
            user = Userr.objects.get(id=user_id)

            if request.user != user:
                return Response({'detail': 'You are not authorized to upload Image for this user.'}, status=403)

            user.avi = request.FILES.get('avi')
            user.save()

            return Response({'detail': 'Image was uploaded successfully'})
        except Exception as e:
            print(f'Error uploading image: {str(e)}')  # Print error to console
            return Response({'detail': f'Error uploading image: {str(e)}'}, status=500)







from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class ResetImage(APIView):
    def post(self, request):
        try:
            data = request.data

            user = request.user

            if request.user != user:
                return Response({'detail': 'You are not authorized to reset the image for this user.'}, status=403)

            # Set the avi field back to its default value
            user.avi = '/avatar.png'
            user.save()

            return Response({'detail': 'Image was reset successfully'})
        except Exception as e:
            print(f'Error resetting image: {str(e)}')  # Print error to console
            return Response({'detail': f'Error resetting image: {str(e)}'}, status=500)





from rest_framework.parsers import MultiPartParser, FormParser



from django.contrib.auth.validators import UnicodeUsernameValidator

from django.core.validators import validate_email



# class RegisterUser(APIView):

#     def post(self, request):
#         data = request.data

#         print("Data received from the form:", data)


#         # Determine user type based on form data
#         user_type = data.get('user_type')
#         if user_type == 'admin':
#             fields_to_check = ['name', 'email', 'password', 'date_of_birth', 'gender', 'address']
#             email_message = "Welcome to FORTE! We hope you enjoy our services Be Sure To Confirm Your Email Or You Will Not Get Your Account Back When You Lose Your Password"
#         elif user_type == 'staff':
#             abslink = "http://localhost:3000/#/forgot-password/"

#             fields_to_check = ['name', 'email', 'password', 'date_of_birth', 'gender', 'address', 'Id_number']
#             email_message = f"You have been invited as a staff member at a FORTE hostel. Go Here: {abslink} and enter your Email to Reset Your Password and then log in with Your New Password."

#         elif user_type == 'student':
#             fields_to_check = ['name', 'email', 'password', 'date_of_birth', 'gender', 'address', 'guardian_name', 'guardian_contact', 'guardian2_name', 'guardian2_contact', 'Id_number']
#             email_message = "Welcome to FORTE! We hope you enjoy our services."
#         else:
#             return Response({'detail': 'Invalid user type.'}, status=status.HTTP_400_BAD_REQUEST)


#         # Check if all required fields are present
#         for field in fields_to_check:
#             if field not in data:
#                 return Response({'detail': f'Missing {field} field.'}, status=status.HTTP_400_BAD_REQUEST)

#         # Check password length
#         if len(data['password']) < 8:
#             content = {'detail': 'Password must be at least 8 characters long.'}
#             return Response(content, status=status.HTTP_400_BAD_REQUEST)

#         # Check password for username and email
#         if data['password'].lower() in [data['name'].lower(), data['email'].lower()]:
#             content = {'detail': 'Password cannot contain username or email.'}
#             return Response(content, status=status.HTTP_400_BAD_REQUEST)

#         # Validate email format
#         try:
#             validate_email(data['email'])
#         except ValidationError:
#             return Response({'detail': 'Invalid email address.'}, status=status.HTTP_400_BAD_REQUEST)

#         # Validate password strength
#         try:
#             validate_password(data['password'])
#         except ValidationError as e:
#             return Response({'detail': ', '.join(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

#         # Create user
#         try:
#             user = CustomUser.objects.create_user(
#                 first_name=data['name'],
#                 username=data['email'],
#                 email=data['email'],
#                 user_type=user_type,  # Set the user_type field
#                 password=data['password'],
#                 isForte=(user_type == 'staff')  # Set isForte to True for staff
#             )

#             if user_type == 'staff' and hasattr(request.user, 'hostel'):
#                 user.hostel = request.user.hostel
#                 user.save()

#             email_subject = "Welcome to FORTE"
#             to_email = user.email
#             data = {
#                 'email_body': email_message,
#                 'email_subject': email_subject,
#                 'to_email': to_email
#             }
#             send_normal_email(data)
#         except IntegrityError:
#             message = {'detail': 'User with this email already exists.'}
#             return Response(message, status=status.HTTP_400_BAD_REQUEST)

#         serializer = UserSerializer(user, many=False)
#         return Response(serializer.data)


from django.core.exceptions import ObjectDoesNotExist
import os

# #EMAIL
# class RegisterUser(APIView):

#     def post(self, request):
#         data = request.data

#         print("Data received from the form:", data)

#         # Check if user type is provided
#         user_type = data.get('user_type')
#         if not user_type:
#             return Response({'detail': 'User type not provided.'}, status=status.HTTP_400_BAD_REQUEST)




#         # Load email template
#         template_path = os.path.join(settings.BASE_DIR, 'base/email_templates', 'Register.html')
#         with open(template_path, 'r', encoding='utf-8') as template_file:
#             html_content = template_file.read()


#         # Load email template
#         template_path2 = os.path.join(settings.BASE_DIR, 'base/email_templates', 'RegisterStaff.html')
#         with open(template_path2, 'r', encoding='utf-8') as template_file:
#             staff_content = template_file.read()



#         # Check if all required fields are present based on user type
#         if user_type == 'admin':
#             fields_to_check = ['name', 'email', 'password']
#             email_message = html_content
#         elif user_type == 'staff':
#             abslink = "http://localhost:3000/#/forgot-password/"
#             fields_to_check = ['name', 'email', 'password']
#             email_message = staff_content
#         elif user_type == 'normal':
#             fields_to_check = ['name', 'email', 'password']
#             email_message = html_content
#         else:
#             return Response({'detail': 'Invalid user type.'}, status=status.HTTP_400_BAD_REQUEST)

#         # Check if gender is provided for students

#         # Check if all required fields are present
#         for field in fields_to_check:
#             if field not in data:
#                 return Response({'detail': f'Missing {field} field.'}, status=status.HTTP_400_BAD_REQUEST)

#         # Check password length
#         if len(data['password']) < 8:
#             content = {'detail': 'Password must be at least 8 characters long.'}
#             return Response(content, status=status.HTTP_400_BAD_REQUEST)

#         # Check password for username and email
#         if data['password'].lower() in [data['name'].lower(), data['email'].lower()]:
#             content = {'detail': 'Password cannot contain username or email.'}
#             return Response(content, status=status.HTTP_400_BAD_REQUEST)

#         # Validate email format
#         try:
#             validate_email(data['email'])
#         except :
#             return Response({'detail': 'Invalid email address.'}, status=status.HTTP_400_BAD_REQUEST)

#         # Validate password strength
#         try:
#             validate_password(data['password'])
#         except :
#             return Response({'detail': "Password Must Have Both Letter Cases, Be 8 digits and Above, Have At Least 1 special Character and at least 1 Nummber"}, status=status.HTTP_400_BAD_REQUEST)

#         # Create user
#         try:
#             user = CustomUser.objects.create_user(
#                 first_name=data['name'],
#                 username=data['email'],
#                 email=data['email'],
#                 user_type=user_type,  # Set the user_type field
#                 password=data['password'],

#                     # Gender provided only for students
#                 # Set isForte to True for staff
#             )



#             if user_type == 'staff':
#                 try:
#                     if hasattr(request.user, 'area'):
#                         user.area = request.user.area
#                     if hasattr(request.user, 'community'):
#                         user.community = request.user.community
#                     user.save()
#                 except AttributeError:
#                     pass  # Ignore the error if the user does not have area or community



#             email_subject = "Welcome to FORTE"
#             to_email = user.email
#             data = {
#                 'email_body': email_message,
#                 'email_subject': email_subject,
#                 'to_email': to_email,
#                 'context': {
#                     'link': abslink,
#                 },
#             }
#             send_normal_email(data)
#         except IntegrityError:
#             message = {'detail': 'User with this email already exists.'}
#             return Response(message, status=status.HTTP_400_BAD_REQUEST)

#         serializer = UserSerializer(user, many=False)
#         return Response(serializer.data)




class RegisterUser(APIView):

    def post(self, request):
        data = request.data

        print("Data received from the form:", data)

        # Check if user type is provided
        user_type = data.get('user_type')
        if not user_type:
            return Response({'detail': 'User type not provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # Load email template based on user type
        if user_type == 'staff':
            template_path = os.path.join(settings.BASE_DIR, 'base','email_templates', 'RegisterStaff.html')
        else:
            template_path = os.path.join(settings.BASE_DIR, 'base/email_templates', 'Register.html')

        try:
            with open(template_path, 'r', encoding='utf-8') as template_file:
                email_content = template_file.read()
        except FileNotFoundError:
            return Response({'detail': 'Email template not found.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Define required fields based on user type
        fields_to_check = ['name', 'email', 'password']

        # Check if all required fields are present
        for field in fields_to_check:
            if field not in data:
                return Response({'detail': f'Missing {field} field.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check password length
        if len(data['password']) < 8:
            return Response({'detail': 'Password must be at least 8 characters long.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check password for username and email
        if data['password'].lower() in [data['name'].lower(), data['email'].lower()]:
            return Response({'detail': 'Password cannot contain username or email.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate email format
        try:
            validate_email(data['email'])
        except:
            return Response({'detail': 'Invalid email address.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate password strength
        try:
            validate_password(data['password'])
        except:
            return Response({'detail': 'Password must meet complexity requirements.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create user
        try:
            user = CustomUser.objects.create_user(
                first_name=data['name'],
                username=data['email'],
                email=data['email'],
                user_type=user_type,
                password=data['password'],
            )

            # Update area and community for staff
            if user_type == 'staff':
                if hasattr(request.user, 'area'):
                    user.area = request.user.area
                if hasattr(request.user, 'community'):
                    user.community = request.user.community

            # Update is_demo if provided
            if 'is_demo' in data:
                user.is_demo = data['is_demo']

            user.save()

            abslink = "http://localhost:3000/#/forgot-password/"
            email_subject = "Welcome to RE-UP"
            to_email = user.email
            email_data = {
                'email_body': email_content,
                'email_subject': email_subject,
                'to_email': to_email,
                'context': {
                    'link': abslink,
                },
            }
            send_normal_email(email_data)

        except IntegrityError:
            return Response({'detail': 'User with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)

from base.core.b2c import process_b2c_payment

# @permission_classes([IsAuthenticated])


# class GetUserProfile(APIView):

#     def get(self, request):
#         user = request.user
#         serializer = UserSerializer(user, many=False)


#         return Response(serializer.data)

@permission_classes([IsAuthenticated])
class GetUserProfile(APIView):

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user, many=False)

        # # Process B2C payment
        # template_path = os.path.join(settings.BASE_DIR, 'base', 'email_templates', 'Pay.html')
        # with open(template_path, 'r', encoding='utf-8') as template_file:
        #     html_content = template_file.read()
        # email_data = {
        #     'email_subject': 'You Received Payment',
        #     'email_body': html_content,
        #     'to_email': user.email,

        # }
        # send_normal_email(email_data)
        process_b2c_payment(user)


        return Response(serializer.data)

class UpdateUserProfile(APIView):

    def put(self, request):
        user = request.user
        serializer = UserSerializerWithToken(user, many=False)
        data = request.data

        new_email = data.get('email')

        # Check if email is being updated to an existing email
        if new_email and CustomUser.objects.exclude(pk=user.pk).filter(email=new_email).exists():
            return Response({'detail': 'User with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        # Update password if provided
        if 'password' in data and data['password'] != '':
            # Add password strength checks here
            if len(data['password']) < 8:
                content = {'detail': 'Password must be at least 8 characters long.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            uppercase_count = sum(1 for c in data['password'] if c.isupper())
            lowercase_count = sum(1 for c in data['password'] if c.islower())
            if uppercase_count < 1 or lowercase_count < 1:
                content = {'detail': 'Password must contain at least one uppercase and lowercase character.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            digit_count = sum(1 for c in data['password'] if c.isdigit())
            special_count = sum(1 for c in data['password'] if not c.isalnum())
            if digit_count < 1 or special_count < 1:
                content = {'detail': 'Password must contain at least one digit and one special character.'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

            user.password = make_password(data['password'])

        # Update user profile details
        user.first_name = data.get('name', user.first_name)
        user.username = data.get('email', user.username)
        user.email = data.get('email', user.email)
        user.bio = data.get('bio', user.bio)
        user.contact_number = data.get('contact_number', user.contact_number)

        # Save updated user profile
        user.save()

        # Return updated user data
        return Response(serializer.data)
from rest_framework.exceptions import PermissionDenied



@permission_classes([IsAuthenticated])
class deleteAccount(APIView):

    def delete(self, request):
        user_for_deletion = request.user
        user_for_deletion.delete()
        return Response({"detail": "Account deleted successfully."}, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    serializer_class=PasswordResetRequestSerializer

    def post(self, request):
        serializer=self.serializer_class(data=request.data, context={'request':request})
        serializer.is_valid(raise_exception=True)
        return Response({'message':'we have sent you a link to reset your password'}, status=status.HTTP_200_OK)
        # return Response({'message':'user with that email does not exist'}, status=status.HTTP_400_BAD_REQUEST)




class PasswordResetConfirm(APIView):

    def get(self, request, uidb64, token):
        try:
            user_id=smart_str(urlsafe_base64_decode(uidb64))
            user=Userr.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'message':'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success':True, 'message':'credentials is valid', 'uidb64':uidb64, 'token':token}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError as identifier:
            return Response({'message':'token is invalid or has expired'}, status=status.HTTP_401_UNAUTHORIZED)

class SetNewPasswordView(GenericAPIView):
    serializer_class=SetNewPasswordSerializer

    def patch(self, request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response({'success':True, 'message':"password reset is succesful"}, status=status.HTTP_200_OK)



@permission_classes([IsAuthenticated])
class RemoveStaff(APIView):
    def post(self, request, pk):
        # Check if the request user type is admin
        if request.user.user_type != 'admin':
            return Response({"message": "You are not authorized to remove staff."}, status=status.HTTP_403_FORBIDDEN)

        # Check if the user with the provided ID exists and is a staff member
        try:
            user = CustomUser.objects.get(id=pk)
            if user.user_type != 'staff':
                return Response({"message": "The provided user is not a staff member."}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the administrator's community matches the user's community
        if request.user.community != user.community:
            return Response({"message": "You are not authorized to remove staff from this community."}, status=status.HTTP_403_FORBIDDEN)

        # Update the user's user_type to 'normal' and reset the community field to null
        user.community = None
        user.user_type = "normal"
        user.save()

        # Send a notice to the staff member
        Notice.objects.create(
            user=user,
            message=f'Hi, unfortunately, you have been relieved of your duties in the community "{request.user.community.name}".'
        )

        return Response({"message": "Staff removed successfully."}, status=status.HTTP_200_OK)
