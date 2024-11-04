from django.urls import path
from .api import *
from .api2 import *
from .api3 import *

urlpatterns = [


    path('trash/', CreateTrashView.as_view(), name='create-trash'),
    path('trash/direct/', CreateTrashDirectView.as_view(), name='create-trash'),

    path('trash/all/', ListTrashView.as_view(), name='list-trash'),


    path('point/', CreatePointView.as_view(), name='create-point'),
    path('points/', RetrievePointsWithinRadiusView.as_view(), name='get-points'),


    path('upload/', uploadImage.as_view(), name='image-upload'),
    path('uploads/', UploadAlbum.as_view(), name='images-upload'),
    path('videos/', UploadVideo.as_view(), name='video-upload'),
    path('new/', CreatePost.as_view(), name='new-post'),
    path('gallery/', GetPostsView.as_view(), name='get_posts'),
    path('blacklisted-communities/', ListBlacklistedCommunitiesView.as_view(), name='list-blacklisted-communities'),

    path('insights/', RandomInsightView.as_view(), name='get_posts'),



    path('community/', CreateCommunityView.as_view(), name='create-community'),


    path('leaderboards/individual/', ListIndividualLeaderboardsView.as_view(), name='list-individual-leaderboards'),
    path('leaderboards/community/', RetrieveCommunityLeaderboardView.as_view(), name='retrieve-community-leaderboard'),



    path('newarea/', CreateAdminAreaView.as_view(), name='create-admin-area'),
    path('admin-areas/', ListAdminAreasView.as_view(), name='list-admin-areas'),
    path('join/', JoinAreaView.as_view(), name='join-admin-area'),

    path('newreport/', CreateReportView.as_view(), name='create-report'),




    path('blacklist/add/', AddToBlacklistView.as_view(), name='add_to_blacklist'),
    path('blacklist/remove/', RemoveFromBlacklistView.as_view(), name='remove_from_blacklist'),
    path('blacklist/appeal/', AppealBlacklistView.as_view(), name='appeal_blacklist'),
    path('blacklist/list/', ListBlacklistedUsersView.as_view(), name='list_blacklisted_users'),

    path('reports/community/', ListReportsByCommunityView.as_view(), name='list-reports-by-community'),

    path('trash/verify/', VerifyTrashView.as_view(), name='verify-trash'),



    path('<str:pk>/', GetPost.as_view(), name='get_post'),

    path('trash/<int:pk>/update/', UpdateTrashView.as_view(), name='update-trash'),
    path('trash/<int:pk>/', RetrieveTrashView.as_view(), name='retrieve-trash'),


    path('point/<int:pk>/', RetrievePointView.as_view(), name='retrieve-point'),
    path('point/<int:pk>/delete/', DeletePointView.as_view(), name='delete-point'),
    path('points/<int:admin_area_id>/', ListPointsByAdminAreaView.as_view(), name='list-points-by-admin-area'),




    path('update/<str:pk>/', UpdatePost.as_view(), name='post-update'),
    path('<str:pk>/like/', LikePost.as_view(), name='like'),
    path('<str:pk>/comment/', CreateComment.as_view(), name='create-comment'),
    path('comment/<str:pk>/delete/', deleteComment.as_view(), name='delete-comment'),
    path('<str:pk>/delete/', deletePost.as_view(), name='delete-post'),
    path('posts/check-expired/', CheckExpiredPosts.as_view(), name='check-expired-posts'),


    path('community/<int:pk>/update/', UpdateCommunityView.as_view(), name='update-community'),
    path('community/<int:pk>/get/', RetrieveCommunityView.as_view(), name='retrieve-community'),
    path('community/<int:pk>/delete/', DeleteCommunityView.as_view(), name='delete-community'),






    path('admin-areas/<int:pk>/', RetrieveAdminAreaView.as_view(), name='retrieve-admin-area'),
    path('area/<int:pk>/delete/', DeleteAdminAreaView.as_view(), name='delete-admin-area'),



    path('reports/<int:pk>/', DeleteReportView.as_view(), name='delete-report'),




]
