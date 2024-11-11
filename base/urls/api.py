from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from better_profanity import profanity
from django.db import transaction

from rest_framework.decorators import permission_classes

from rest_framework import generics
from ..serializers import *
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination


import logging
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes



from math import sqrt, pi
from geopy.distance import geodesic
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union


from base.core.image_api import get_waste_type_from_image
from base.core.insight_api import generate_markdown


# class CreateTrashView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         serializer = TrashSerializer(data=request.data)
#         if serializer.is_valid():
#             # Save the uploaded file temporarily in memory
#             temp_file = serializer.validated_data['photo']

#             # Generate waste type using the AI model
#             waste_type = get_waste_type_from_image(temp_file, settings.GOOGLE_API_KEY)

#             # Save the trash object with the AI-generated type and the user
#             trash = Trash.objects.create(
#                 user=request.user,
#                 photo=serializer.validated_data['photo'],
#                 point=serializer.validated_data['point'],
#                 types=waste_type
#             )
#             return Response(TrashSerializer(trash).data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateTrashView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TrashSerializer(data=request.data)
        if serializer.is_valid():
            temp_file = serializer.validated_data['photo']

            # Generate waste type using the AI model
            waste_type = get_waste_type_from_image(temp_file, settings.GOOGLE_API_KEY)

            # Retrieve the point from the validated data
            point = serializer.validated_data['point']

            # Check if the generated waste type is accepted at the specified point
            if waste_type not in point.types:
                return Response(
                    {"detail": f"You cannot throw this type of trash here. Look for {waste_type} collection points."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Save the trash object with the AI-generated type and the user
            trash = Trash.objects.create(
                user=request.user,
                photo=serializer.validated_data['photo'],
                point=point,
                types=waste_type
            )
            return Response(TrashSerializer(trash).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




from django.utils import timezone
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import ParseError



class CreateTrashDirectView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Parse the JSON data from the request
        try:
            data = JSONParser().parse(request)
        except ParseError:
            return Response({"detail": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the required fields are present
        required_fields = ['trash_type', 'point']
        for field in required_fields:
            if field not in data:
                return Response({"detail": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Extract the trash type and point
        trash_type = data['trash_type']
        point = data['point']

        # Check if the provided point exists
        try:
            point_instance = Point.objects.get(id=point)
        except Point.DoesNotExist:
            return Response({"detail": "You chose a non-existent point."}, status=status.HTTP_400_BAD_REQUEST)

        # # Check if the provided trash type is accepted at the specified point
        # if trash_type not in point_instance.types:
        #     return Response(
        #         {"detail": f"You cannot throw this type of trash here. Look for {trash_type} collection points."},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )

        # Save the trash object with the provided type and the user
        trash = Trash.objects.create(
            user=request.user,
            point=point_instance,
            types=trash_type,
        )
        return Response(TrashSerializer(trash).data, status=status.HTTP_201_CREATED)


# class VerifyTrashView(APIView):
#     permission_classes = [IsAuthenticated]
#     parser_classes = [JSONParser]

#     POINTS_AWARD_SYSTEM = {
#         'Hazardous': 10,
#         'Electronic': 9,
#         'Metal': 8,
#         'Plastic': 7,
#         'General': 6,
#         'Glass': 5,
#         'Paper': 4,
#         'Organic': 3,
#         'Food': 2,
#     }

#     INDIVIDUAL_MILESTONES = [100, 500, 1000, 5000, 10000]
#     COMMUNITY_MILESTONES = [1000, 10000, 25000, 50000, 100000]

#     def post(self, request):
#         # Ensure the request data is JSON
#         if not request.content_type == 'application/json':
#             return Response({'detail': 'Content-Type must be application/json.'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             request_data = request.data
#         except ParseError:
#             return Response({'detail': 'Invalid JSON.'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             trash = Trash.objects.filter(user=request.user).latest('timestamp')
#         except Trash.DoesNotExist:
#             return Response({'detail': 'No trash found for the user.'}, status=status.HTTP_404_NOT_FOUND)

#         status_data = request_data.get('status', None)

#         if status_data is None:
#             return Response({'detail': 'Status field is required.'}, status=status.HTTP_400_BAD_REQUEST)

#         if status_data in ['yes', 'no']:
#             # Generate AI insight and create/update Insight object
#             api_key = settings.GOOGLE_API_KEY
#             markdown_text = generate_markdown(api_key, trash.types)
#             Insights.objects.filter(trash=trash, user=request.user).delete()
#             Insights.objects.create(trash=trash, user=request.user, description=markdown_text)

#         if status_data == 'yes':
#             trash.verification_status = True
#             trash.save()
#             self.award_points(trash)
#             return Response({'detail': 'Trash verification status updated to true, points awarded, and insight generated.'}, status=status.HTTP_200_OK)

#         if status_data == 'na':
#             trash.delete()
#             return Response({'detail': 'Trash object deleted.'}, status=status.HTTP_200_OK)

#         return Response({'detail': 'Invalid status value.'}, status=status.HTTP_400_BAD_REQUEST)

#     def award_points(self, trash):
#         points = self.POINTS_AWARD_SYSTEM.get(trash.types, 0)
#         user = trash.user
#         community = user.community

#         # Update IndividualLeaderboard
#         individual_leaderboard, created = IndividualLeaderboard.objects.get_or_create(user=user)
#         previous_points = individual_leaderboard.points
#         individual_leaderboard.points += points
#         individual_leaderboard.save()

#         # Check for individual milestones
#         for milestone in self.INDIVIDUAL_MILESTONES:
#             if previous_points < milestone <= individual_leaderboard.points:
#                 Notice.objects.create(
#                     user=user,
#                     message=f'Congratulations! You have reached {milestone} points.'
#                 )

#         # Update CommunityLeaderboard
#         if community:
#             community_leaderboard, created = CommunityLeaderboard.objects.get_or_create(community=community)
#             previous_community_points = community_leaderboard.points
#             community_leaderboard.points += points
#             community_leaderboard.save()

#             # Check for community milestones
#             for milestone in self.COMMUNITY_MILESTONES:
#                 if previous_community_points < milestone <= community_leaderboard.points:
#                     Notice.objects.create(
#                         user=community.admin,
#                         message=f'Community {community.name} has reached {milestone} points.'
#                     )



class VerifyTrashView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    POINTS_AWARD_SYSTEM = {
        'Hazardous': 10,
        'Electronic': 9,
        'Metal': 8,
        'Plastic': 7,
        'General': 6,
        'Glass': 5,
        'Paper': 4,
        'Organic': 3,
        'Food': 2,
    }

    INDIVIDUAL_MILESTONES = [100, 500, 1000, 5000, 10000]
    COMMUNITY_MILESTONES = [1000, 10000, 25000, 50000, 100000]

    def post(self, request):
        if not request.content_type == 'application/json':
            return Response({'detail': 'Content-Type must be application/json.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            request_data = request.data
            print(f"Received request data: {request_data}")
        except ParseError:
            return Response({'detail': 'Invalid JSON.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            trash = Trash.objects.filter(user=request.user).latest('timestamp')
        except Trash.DoesNotExist:
            return Response({'detail': 'No trash found for the user.'}, status=status.HTTP_404_NOT_FOUND)

        status_data = request_data.get('status', None)
        print(f"Status data received: {status_data}")

        if status_data is None:
            return Response({'detail': 'Status field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if status_data in ['yes', 'no']:
            api_key = settings.GOOGLE_API_KEY
            markdown_text = generate_markdown(api_key, trash.types)
            Insights.objects.filter(trash=trash, user=request.user).delete()
            Insights.objects.create(trash=trash, user=request.user, description=markdown_text)

        if status_data == 'yes':
            trash.verification_status = True
            trash.save()
            self.award_points(trash)
            return Response({'detail': 'Trash verification status updated to true, points awarded, and insight generated.'}, status=status.HTTP_200_OK)

        if status_data == 'no':
            trash.verification_status = False
            trash.save()
            return Response({'detail': 'Trash verification status updated to false, and insight generated.'}, status=status.HTTP_200_OK)

        if status_data == 'na':
            trash.delete()
            return Response({'detail': 'Trash object deleted.'}, status=status.HTTP_200_OK)

        return Response({'detail': 'Invalid status value.'}, status=status.HTTP_400_BAD_REQUEST)

    def award_points(self, trash):
        points = self.POINTS_AWARD_SYSTEM.get(trash.types, 0)
        user = trash.user
        community = user.community

        individual_leaderboard, created = IndividualLeaderboard.objects.get_or_create(user=user)
        previous_points = individual_leaderboard.points
        individual_leaderboard.points += points
        individual_leaderboard.save()

        # Update user's points
        user.points = individual_leaderboard.points
        user.save()

        for milestone in self.INDIVIDUAL_MILESTONES:
            if previous_points < milestone <= individual_leaderboard.points:
                Notice.objects.create(
                    user=user,
                    message=f'Congratulations! You have reached {milestone} points.'
                )

        if community:
            community_leaderboard, created = CommunityLeaderboard.objects.get_or_create(community=community)
            previous_community_points = community_leaderboard.points
            community_leaderboard.points += points
            community_leaderboard.save()

            for milestone in self.COMMUNITY_MILESTONES:
                if previous_community_points < milestone <= community_leaderboard.points:
                    Notice.objects.create(
                        user=community.admin,
                        message=f'Community {community.name} has reached {milestone} points.'
                    )



# class VerifyTrashView(APIView):
#     permission_classes = [IsAuthenticated]
#     parser_classes = [JSONParser]

#     POINTS_AWARD_SYSTEM = {
#         'Hazardous': 10,
#         'Electronic': 9,
#         'Metal': 8,
#         'Plastic': 7,
#         'General': 6,
#         'Glass': 5,
#         'Paper': 4,
#         'Organic': 3,
#         'Food': 2,
#     }

#     INDIVIDUAL_MILESTONES = [100, 500, 1000, 5000, 10000]
#     COMMUNITY_MILESTONES = [1000, 10000, 25000, 50000, 100000]

#     def post(self, request):
#         if not request.content_type == 'application/json':
#             return Response({'detail': 'Content-Type must be application/json.'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             request_data = request.data
#             print(f"Received request data: {request_data}")
#         except ParseError:
#             return Response({'detail': 'Invalid JSON.'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             trash = Trash.objects.filter(user=request.user).latest('timestamp')
#         except Trash.DoesNotExist:
#             return Response({'detail': 'No trash found for the user.'}, status=status.HTTP_404_NOT_FOUND)

#         status_data = request_data.get('status', None)
#         print(f"Status data received: {status_data}")

#         if status_data is None:
#             return Response({'detail': 'Status field is required.'}, status=status.HTTP_400_BAD_REQUEST)

#         if status_data in ['yes', 'no']:
#             api_key = settings.GOOGLE_API_KEY
#             markdown_text = generate_markdown(api_key, trash.types)
#             Insights.objects.filter(trash=trash, user=request.user).delete()
#             Insights.objects.create(trash=trash, user=request.user, description=markdown_text)

#         if status_data == 'yes':
#             trash.verification_status = True
#             trash.save()
#             self.award_points(trash)
#             return Response({'detail': 'Trash verification status updated to true, points awarded, and insight generated.'}, status=status.HTTP_200_OK)

#         if status_data == 'no':
#             trash.verification_status = False
#             trash.save()
#             return Response({'detail': 'Trash verification status updated to false, and insight generated.'}, status=status.HTTP_200_OK)

#         if status_data == 'na':
#             trash.delete()
#             return Response({'detail': 'Trash object deleted.'}, status=status.HTTP_200_OK)

#         return Response({'detail': 'Invalid status value.'}, status=status.HTTP_400_BAD_REQUEST)

#     def award_points(self, trash):
#         points = self.POINTS_AWARD_SYSTEM.get(trash.types, 0)
#         user = trash.user
#         community = user.community

#         individual_leaderboard, created = IndividualLeaderboard.objects.get_or_create(user=user)
#         previous_points = individual_leaderboard.points
#         individual_leaderboard.points += points
#         individual_leaderboard.save()

#         for milestone in self.INDIVIDUAL_MILESTONES:
#             if previous_points < milestone <= individual_leaderboard.points:
#                 Notice.objects.create(
#                     user=user,
#                     message=f'Congratulations! You have reached {milestone} points.'
#                 )

#         if community:
#             community_leaderboard, created = CommunityLeaderboard.objects.get_or_create(community=community)
#             previous_community_points = community_leaderboard.points
#             community_leaderboard.points += points
#             community_leaderboard.save()

#             for milestone in self.COMMUNITY_MILESTONES:
#                 if previous_community_points < milestone <= community_leaderboard.points:
#                     Notice.objects.create(
#                         user=community.admin,
#                         message=f'Community {community.name} has reached {milestone} points.'
#                     )


class UpdateTrashView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        trash = get_object_or_404(Trash, pk=pk)
        if trash.user != request.user:
            return Response({'detail': 'You do not have permission to update this item.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TrashSerializer(trash, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class RetrieveTrashView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        trash = get_object_or_404(Trash, pk=pk)
        serializer = TrashSerializer(trash)
        return Response(serializer.data, status=status.HTTP_200_OK)


#LIST
class ListTrashView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        trash_items = Trash.objects.filter(user=request.user)
        name = request.query_params.get('name')
        if name is not None:
            trash_items = trash_items.filter(types__icontains=name)


        paginator = PageNumberPagination()
        paginator.page_size = 10  # Set the number of posts per page
        result_page = paginator.paginate_queryset(trash_items, request)


        serializer = TrashSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
















#checked
class CreatePointView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PointSerializer(data=request.data)
        if serializer.is_valid():
            # Extract validated data
            admin_area_id = serializer.validated_data.get('admin_area')
            location = serializer.validated_data.get('location')


            # Fetch the associated AdminArea
            try:
                admin_area = AdminArea.objects.get(id=request.data.get("admin_area"))
            except AdminArea.DoesNotExist:
                return Response({'detail': 'Admin area does not exist.'}, status=status.HTTP_404_NOT_FOUND)

            # Check if the user is the admin of the AdminArea
            if request.user != admin_area.admin:
                return Response({'detail': 'You do not have permission to add points to this admin area.'}, status=status.HTTP_403_FORBIDDEN)

            # Validate the location
            try:
                loc_lat, loc_lon = map(float, location.strip().split(','))
                admin_lat, admin_lon = map(float, admin_area.main_coordinate.split(','))
                point_distance = geodesic((loc_lat, loc_lon), (admin_lat, admin_lon)).kilometers

                # Check if the location is within the 2.586 km radius
                if point_distance > 2.586:
                    return Response({'detail': 'The point must be within 2.586 km radius of the admin area.'}, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                return Response({'detail': 'Invalid location coordinates provided.'}, status=status.HTTP_400_BAD_REQUEST)

            # Save the valid point
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






# class UpdatePointView(APIView):
#     permission_classes = [IsAuthenticated]

#     def put(self, request, pk):
#         point = get_object_or_404(Point, pk=pk)
#         serializer = PointSerializer(point, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#checked
class RetrievePointView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        point = get_object_or_404(Point, pk=pk)
        serializer = PointSerializer(point)
        return Response(serializer.data, status=status.HTTP_200_OK)


from base.models import Point

#checked
class ListPointsByAdminAreaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, admin_area_id):
        admin_area = get_object_or_404(AdminArea, id=admin_area_id)
        points = Point.objects.filter(admin_area=admin_area)
        serializer = PointSerializer(points, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


#LIST
class RetrievePointsWithinRadiusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        coordinates = request.data.get('coordinates')
        if not coordinates:
            return Response({'detail': 'Coordinates are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            loc_lat, loc_lon = map(float, coordinates.strip().split(','))
        except Exception as e:
            return Response({'detail': 'Invalid coordinates provided.'}, status=status.HTTP_400_BAD_REQUEST)

        points_within_radius = []
        all_points = Point.objects.all()

        name = request.query_params.get('name')


        for point in all_points:
            point_lat, point_lon = map(float, point.location.split(','))
            point_distance = geodesic((loc_lat, loc_lon), (point_lat, point_lon)).kilometers

            if point_distance <= 2.586:
                points_within_radius.append(point)

        if name is not None:
            points_within_radius = points_within_radius.filter(types__icontains=name)

        paginator = PageNumberPagination()
        paginator.page_size = 20  # Set the number of posts per page
        result_page = paginator.paginate_queryset(points_within_radius, request)




        serializer = PointSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)



import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class JoinAreaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Ensure the user already belongs to an area and community
        if user.area and user.community:
            return Response({'detail': 'You are already part of an area and community.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if request.data is None
        if request.data is None:
            logger.error("Request data is None. Possible issue with the content type or request payload.")
            return Response({'detail': 'Invalid request data.'}, status=status.HTTP_400_BAD_REQUEST)

        coordinates = request.data.get('coordinates')
        if not coordinates:
            return Response({'detail': 'Coordinates are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_lat, user_lon = map(float, coordinates.strip().split(','))
        except Exception as e:
            logger.error(f"Invalid coordinates provided: {coordinates}. Error: {e}")
            return Response({'detail': 'Invalid coordinates provided.'}, status=status.HTTP_400_BAD_REQUEST)

        closest_admin_area = None
        min_distance = float('inf')

        all_admin_areas = AdminArea.objects.all()
        for admin_area in all_admin_areas:
            if not admin_area.main_coordinate:
                continue

            admin_lat, admin_lon = map(float, admin_area.main_coordinate.split(','))
            distance = geodesic((user_lat, user_lon), (admin_lat, admin_lon)).kilometers

            if distance < min_distance and distance <= 3:
                min_distance = distance
                closest_admin_area = admin_area

        if closest_admin_area is None:
            return Response({'detail': 'We could not find any nearby areas registered with us.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the closest admin area has a community
        community = Community.objects.filter(area=closest_admin_area).first()

        if community:
            user.community = community
            user.user_type = "normal"
            user.save()

        user.area = closest_admin_area
        user.save()

        # Send a notice to the user
        Notice.objects.create(
            user=user,
            message=f'You have successfully joined the area: {closest_admin_area.name}' + (f' and community: {community.name}' if community else '')
        )

        return Response({'detail': f'User joined area: {closest_admin_area.name}', 'community': community.name if community else 'None'}, status=status.HTTP_200_OK)

#checked
class DeletePointView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        point = get_object_or_404(Point, pk=pk)
        point.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)











import os

#checked
class CreateCommunityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Check if the user is an admin
        if user.user_type != 'admin':
            return Response({'detail': 'You do not have permission to create a community.'}, status=status.HTTP_403_FORBIDDEN)

        # Check if the user owns an AdminArea
        if not AdminArea.objects.filter(admin=user).exists():
            return Response({'detail': 'You must own an AdminArea to create a community.'}, status=status.HTTP_403_FORBIDDEN)

        # Check if the user has already created a community in the same location
        if Community.objects.filter(admin=user).exists():
            return Response({'detail': 'You have already created a community in this location.'}, status=status.HTTP_400_BAD_REQUEST)

        # Extract data from the request
        name = request.data.get('name', '')
        email = request.data.get('email', '')
        bio = request.data.get('bio', '')


        template_path = os.path.join(settings.BASE_DIR, 'base', 'email_templates', 'NewCommunity.html')
        with open(template_path, 'r', encoding='utf-8') as template_file:
            html_content = template_file.read()
        # Create the Community instance
        community = Community.objects.create(
            name=name,
            admin=user,
            area = user.area,
            email = email,
            bio = bio

        )
        user.community = community
        user.save()

        # Send email
        email_data = {
            'email_subject': 'You Made A Community',
            'email_body': html_content,
            'to_email': user.email,
            'context': {
                'name': community.name,
            },
        }
        send_normal_email(email_data)

        # Serialize the created instance
        serializer = CommunitySerializer(community, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


#checked
class UpdateCommunityView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        community = get_object_or_404(Community, pk=pk)

        # Check if the requesting user is the admin of the community
        if community.admin != request.user:
            return Response({'detail': 'You do not have permission to update this community.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommunitySerializer(community, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#checked
class RetrieveCommunityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        community = get_object_or_404(Community, pk=pk)
        serializer = CommunitySerializer(community)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DeleteCommunityView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        community = get_object_or_404(Community, pk=pk)

        # Check if the requesting user is the admin of the community
        if community.admin != request.user:
            return Response({'detail': 'You do not have permission to delete this community.'}, status=status.HTTP_403_FORBIDDEN)

        # Get all users in the community except the requesting user
        community_members = CustomUser.objects.filter(community=community).exclude(id=request.user.id)

        # Send a notice to each member of the community
        for member in community_members:
            Notice.objects.create(
                user=member,
                message=f'Unfortunately, your community "{community.name}" has been discontinued.'
            )

        # Delete the community
        community.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


#LIST
class ListIndividualLeaderboardsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        leaderboards = IndividualLeaderboard.objects.all().order_by('-points')


        name = request.query_params.get('name')
        if name is not None:
            leaderboards = leaderboards.filter(points__icontains=name)

        # Use Django REST framework's built-in pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Set the number of posts per page
        result_page = paginator.paginate_queryset(leaderboards, request)





        serializer = IndividualLeaderboardSerializer(result_page, many=True)




        return paginator.get_paginated_response(serializer.data)

#LIST
class RetrieveCommunityLeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        leaderboards = CommunityLeaderboard.objects.all().order_by('-points')


        name = request.query_params.get('name')
        if name is not None:
            leaderboards = leaderboards.filter(points__icontains=name)

        # Use Django REST framework's built-in pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Set the number of posts per page
        result_page = paginator.paginate_queryset(leaderboards, request)



        serializer = CommunityLeaderboardSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)






import geopy



# class CreateAdminAreaView(APIView):
#     permission_classes = [IsAuthenticated]

#     def point_within_existing_areas(self, polygon):
#         existing_areas = AdminArea.objects.all()
#         for area in existing_areas:
#             area_coords = [tuple(map(float, coord.strip().split(','))) for coord in area.coordinates.split(';')]
#             existing_polygon = Polygon(area_coords)
#             if existing_polygon.intersects(polygon) or existing_polygon.contains(polygon):
#                 return True
#         return False

#     def is_far_enough_from_existing_areas(self, lat, lon, min_distance_km=42):
#         existing_areas = AdminArea.objects.all()
#         new_center = (lat, lon)
#         for area in existing_areas:
#             existing_lat, existing_lon = map(float, area.main_coordinate.split(','))
#             existing_center = (existing_lat, existing_lon)
#             distance = geodesic(new_center, existing_center).kilometers
#             if distance < min_distance_km:
#                 return False
#         return True

#     def post(self, request):
#         user = request.user

#         # Check if the user is an admin
#         if user.user_type != 'admin':
#             return Response({'detail': 'You do not have permission to create an admin area.'}, status=status.HTTP_403_FORBIDDEN)

#         # Check if the user already has an admin area
#         if AdminArea.objects.filter(admin=user).exists():
#             return Response({'detail': 'You have already created an admin area.'}, status=status.HTTP_400_BAD_REQUEST)

#         # Extract data from the request
#         name = request.data.get('name', '')
#         coordinates = request.data.get('coordinates', '')

#         try:
#             lat, lon = map(float, coordinates.strip().split(','))
#             center_point = Point(lon, lat)

#             # Radius for the 21 km² area circle
#             radius_km = 2.586

#             # Generate points around the circle
#             points = []
#             for angle in range(0, 360, 1):
#                 new_point = geodesic(kilometers=radius_km).destination((lat, lon), angle)
#                 points.append((new_point.longitude, new_point.latitude))

#             # Create the circular polygon
#             polygon = Polygon(points)

#         except Exception as e:
#             return Response({'detail': 'Invalid coordinates provided.'}, status=status.HTTP_400_BAD_REQUEST)

#         # Check if the point is within any existing admin areas
#         if self.point_within_existing_areas(polygon):
#             return Response({'detail': 'The coordinates fall within an existing admin area.'}, status=status.HTTP_400_BAD_REQUEST)

#         # Check if the new area is at least 42 km away from existing admin areas
#         if not self.is_far_enough_from_existing_areas(lat, lon):
#             return Response({'detail': 'The new admin area must be at least 42 km away from any existing admin area.'}, status=status.HTTP_400_BAD_REQUEST)

#         # Prepare the coordinates string
#         coordinates_str = "; ".join([f"{coord[1]}, {coord[0]}" for coord in points])

#         # Create the AdminArea instance
#         admin_area = AdminArea.objects.create(
#             name=name,
#             admin=user,
#             coordinates=coordinates_str,
#             main_coordinate=f"{lat}, {lon}"
#         )

#         user.area = admin_area
#         user.save()


#         template_path = os.path.join(settings.BASE_DIR, 'base', 'email_templates', 'NewArea.html')
#         with open(template_path, 'r', encoding='utf-8') as template_file:
#             html_content = template_file.read()

#         # Send email
#         email_data = {
#             'email_subject': 'You Added An Area',
#             'email_body': html_content,
#             'to_email': user.email,
#             'context': {
#                 'name': name,
#                 'central': f"{lat}, {lon}",
#             },
#         }
#         send_normal_email(email_data)

#         # Serialize the created instance
#         serializer = AdminAreaSerializer(admin_area, many=False)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


class CreateAdminAreaView(APIView):
    permission_classes = [IsAuthenticated]

    def point_within_existing_areas(self, polygon):
        existing_areas = AdminArea.objects.all()
        for area in existing_areas:
            if area.coordinates:  # Ensure coordinates is not None
                area_coords = [
                    tuple(map(float, coord.strip().split(',')))
                    for coord in area.coordinates.split(';')
                    if coord.strip()  # Ensure coord is not empty
                ]
                existing_polygon = Polygon(area_coords)
                if existing_polygon.intersects(polygon) or existing_polygon.contains(polygon):
                    return True
        return False

    def is_far_enough_from_existing_areas(self, lat, lon, min_distance_km=42):
        existing_areas = AdminArea.objects.all()
        new_center = (lat, lon)
        for area in existing_areas:
            if area.main_coordinate:  # Ensure main_coordinate is not None
                try:
                    existing_lat, existing_lon = map(float, area.main_coordinate.split(','))
                    existing_center = (existing_lat, existing_lon)
                    distance = geodesic(new_center, existing_center).kilometers
                    if distance < min_distance_km:
                        return False
                except ValueError:
                    continue  # Skip invalid coordinates
        return True

    def post(self, request):
        user = request.user

        # Check if the user is an admin
        if user.user_type != 'admin':
            return Response({'detail': 'You do not have permission to create an admin area.'}, status=status.HTTP_403_FORBIDDEN)

        # Check if the user already has an admin area
        if AdminArea.objects.filter(admin=user).exists():
            return Response({'detail': 'You have already created an admin area.'}, status=status.HTTP_400_BAD_REQUEST)

        # Extract data from the request
        name = request.data.get('name', '')
        coordinates = request.data.get('coordinates', '')

        try:
            # Validate and parse the coordinates
            lat, lon = map(float, coordinates.strip().split(','))
            center_point = Point(lon, lat)

            # Radius for the 21 km² area circle
            radius_km = 2.586

            # Generate points around the circle
            points = []
            for angle in range(0, 360, 1):
                new_point = geodesic(kilometers=radius_km).destination((lat, lon), angle)
                points.append((new_point.longitude, new_point.latitude))

            # Create the circular polygon
            polygon = Polygon(points)

        except ValueError:
            return Response({'detail': 'Invalid coordinates provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the point is within any existing admin areas
        if self.point_within_existing_areas(polygon):
            return Response({'detail': 'The coordinates fall within an existing admin area.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the new area is at least 42 km away from existing admin areas
        if not self.is_far_enough_from_existing_areas(lat, lon):
            return Response({'detail': 'The new admin area must be at least 42 km away from any existing admin area.'}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare the coordinates string
        coordinates_str = "; ".join([f"{coord[1]}, {coord[0]}" for coord in points])

        # Create the AdminArea instance
        admin_area = AdminArea.objects.create(
            name=name,
            admin=user,
            coordinates=coordinates_str,
            main_coordinate=f"{lat}, {lon}"
        )

        user.area = admin_area
        user.save()

        template_path = os.path.join(settings.BASE_DIR, 'base', 'email_templates', 'NewArea.html')
        with open(template_path, 'r', encoding='utf-8') as template_file:
            html_content = template_file.read()

        # Send email
        email_data = {
            'email_subject': 'You Added An Area',
            'email_body': html_content,
            'to_email': user.email,
            'context': {
                'name': name,
                'central': f"{lat}, {lon}",
            },
        }
        send_normal_email(email_data)

        # Serialize the created instance
        serializer = AdminAreaSerializer(admin_area, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



#checked
class ListAdminAreasView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        admin_areas = AdminArea.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Set the number of communities per page
        result_page = paginator.paginate_queryset(admin_areas, request)

        serializer = AdminAreaSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)



#checked
class RetrieveAdminAreaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        admin_area = get_object_or_404(AdminArea, pk=pk)
        serializer = AdminAreaSerializer(admin_area)
        return Response(serializer.data, status=status.HTTP_200_OK)

#checked
class DeleteAdminAreaView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        admin_area = get_object_or_404(AdminArea, pk=pk)

        # Check if the requesting user is the admin of the AdminArea
        if admin_area.admin != request.user:
            return Response({'detail': 'You do not have permission to delete this admin area.'}, status=status.HTTP_403_FORBIDDEN)


        template_path = os.path.join(settings.BASE_DIR, 'base', 'email_templates', 'Delete.html')
        with open(template_path, 'r', encoding='utf-8') as template_file:
            html_content = template_file.read()

        # Send email
        email_data = {
            'email_subject': 'You Added An Area',
            'email_body': html_content,
            'to_email': admin_area.admin.email,
            'context': {
                'name': admin_area.name,
                'central': admin_area.main_coordinate,
            },
        }
        send_normal_email(email_data)
        admin_area.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
