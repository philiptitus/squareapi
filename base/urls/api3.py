from rest_framework.views import APIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from better_profanity import profanity
from django.db import transaction
import random

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



class CreateReportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Ensure the user's type is either 'admin' or 'staff'
        if user.user_type not in ['admin', 'staff']:
            return Response({'detail': 'You do not have permission to create a report.'}, status=status.HTTP_403_FORBIDDEN)

        # Ensure the user's community field is not null
        if not user.community:
            return Response({'detail': 'You must belong to a community to create a report.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate and save the report
        serializer = ReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(community=user.community, user=user)

            # If the user is staff, send a notice to the community admin
            if user.user_type == 'staff':
                Notice.objects.create(
                    user=user.community.admin,
                    message=f'You have received an environmental report from staff member {user.email}.'
                )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




#LIST
class ListReportsByCommunityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        community = request.user.community

        # # Ensure the requesting user is the admin of the community
        # if request.user != community.admin:
        #     return Response({'detail': 'You do not have permission to view these reports.'}, status=status.HTTP_403_FORBIDDEN)

        reports = Report.objects.filter(community=community)

        name = request.query_params.get('name')
        if name is not None:
            reports = reports.filter(points__icontains=name)


        paginator = PageNumberPagination()
        paginator.page_size = 10  # Set the number of posts per page
        result_page = paginator.paginate_queryset(reports, request)




        serializer = ReportSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class DeleteReportView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        report = get_object_or_404(Report, pk=pk)

        # Check if the user is the owner of the report or the admin of the associated community
        if request.user != report.user and request.user != report.community.admin:
            return Response({'detail': 'You do not have permission to delete this report.'}, status=status.HTTP_403_FORBIDDEN)

        report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class ListBlacklistedCommunitiesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the communities where the user is blacklisted
        blacklisted_communities = CommunityBlackList.objects.filter(user=request.user)

        # Extract community IDs from the blacklist entries
        community_ids = blacklisted_communities.values_list('community_id', flat=True)

        # Get the communities based on IDs
        communities = Community.objects.filter(id__in=community_ids)

        paginator = PageNumberPagination()
        paginator.page_size = 10  # Set the number of communities per page
        result_page = paginator.paginate_queryset(communities, request)

        serializer = CommunitySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

















    #BLACKLIST



class AddToBlacklistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_to_blacklist_id = request.data.get('user_id')
        user_to_blacklist = CustomUser.objects.get(id=user_to_blacklist_id)
        community = request.user.community

        if request.user != community.admin and (request.user.user_type != 'staff' or request.user.community != community):
            return Response({'detail': 'You do not have permission to add someone to the blacklist.'}, status=status.HTTP_403_FORBIDDEN)

        blacklist_entry, created = CommunityBlackList.objects.get_or_create(user=user_to_blacklist, community=community)
        if not created:
            return Response({'detail': 'User is already blacklisted in this community.'}, status=status.HTTP_400_BAD_REQUEST)

        # Send a notice to the blacklisted person
        Notice.objects.create(
            user=user_to_blacklist,
            message=f'You have been blacklisted from the community "{community.name}". Please appeal if you need further assistance.'
        )

        return Response({'detail': 'User has been added to the blacklist.'}, status=status.HTTP_201_CREATED)






class RemoveFromBlacklistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_to_remove_id = request.data.get('user_id')
        user_to_remove = CustomUser.objects.get(id=user_to_remove_id)
        community = request.user.community

        if request.user != community.admin and (request.user.user_type != 'staff' or request.user.community != community):
            return Response({'detail': 'You do not have permission to remove someone from the blacklist.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            blacklist_entry = CommunityBlackList.objects.get(user=user_to_remove, community=community)
            blacklist_entry.delete()

            # Send a notice to the user who has been removed from the blacklist
            Notice.objects.create(
                user=user_to_remove,
                message=f'You have been removed from the blacklist of the community "{community.name}".'
            )

            return Response({'detail': 'User has been removed from the blacklist.'}, status=status.HTTP_200_OK)
        except CommunityBlackList.DoesNotExist:
            return Response({'detail': 'User is not blacklisted in this community.'}, status=status.HTTP_400_BAD_REQUEST)

import os
class AppealBlacklistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        community = request.user.community
        description = request.data.get('description')

        if CommunityBlackList.objects.filter(user=request.user, community=community).exists():
            blacklist = CommunityBlackList.objects.get(user=request.user, community=community)

            if not blacklist.appeal_sent:
                blacklist.appeal_sent = True
                blacklist.save()

                subject = 'Appeal for Blacklist Removal'
                message = f'{request.user.email} has appealed to be removed from the blacklist.\n\nDescription: {description}'
                recipient_list = community.admin.email

                template_path = os.path.join(settings.BASE_DIR, 'base', 'email_templates', 'Appeal.html')
                with open(template_path, 'r', encoding='utf-8') as template_file:
                    html_content = template_file.read()

                # Send email
                email_data = {
                    'email_subject': subject,
                    'email_body': html_content,
                    'to_email': recipient_list,
                    'context': {
                        'name': request.user.email,
                        'description': description,
                    },
                }
                send_normal_email(email_data)

                # Send a notice to the community admin
                Notice.objects.create(
                    user=community.admin,
                    message=f'User {request.user.email} has appealed to be removed from the blacklist. Check your email for details.'
                )

                return Response({'detail': 'Your appeal has been sent.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'You have already sent an appeal.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'You are not blacklisted in this community.'}, status=status.HTTP_400_BAD_REQUEST)




class ListBlacklistedUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        community = request.user.community

        if request.user != community.admin and (request.user.user_type != 'staff' or request.user.community != community):
            return Response({'detail': 'You do not have permission to view the blacklist.'}, status=status.HTTP_403_FORBIDDEN)

        blacklisted_users = CommunityBlackList.objects.filter(community=community)

        name = request.query_params.get('name')
        if name is not None:
            blacklisted_users = blacklisted_users.filter(community__icontains=name)

        paginator = PageNumberPagination()
        paginator.page_size = 10  # Set the number of posts per page
        result_page = paginator.paginate_queryset(blacklisted_users, request)





        serializer = CommunityBlackListSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)





class RandomInsightView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        insights = Insights.objects.filter(user=request.user)
        if insights.exists():
            random_insight = random.choice(insights)
            data = {
                "id": random_insight.id,
                "description": random_insight.description,
                "trash_id": random_insight.trash.id,
                "username": random_insight.user.username,
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'No insights found for this user.'}, status=status.HTTP_404_NOT_FOUND)
