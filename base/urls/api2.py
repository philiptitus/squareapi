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
from django.conf import settings
from base.core.post_api import generate_markdown_from_images, image_to_base64



logger = logging.getLogger(__name__)



class uploadImage(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        try:
            data = request.data

            post_id = data.get('post_id')
            post = Post.objects.get(id=post_id)

            post.image = request.FILES.get('image')
            post.save()

            return Response({'detail': 'Image was uploaded successfully'})
        except Exception as e:
            logger.error(f'Error uploading image: {str(e)}')
            return Response({'detail': 'Internal Server Error'}, status=500)






# class UploadAlbum(APIView):
#     parser_classes = (MultiPartParser, FormParser)

#     def post(self, request):
#         try:
#             data = request.data

#             post_id = data.get('post_id')
#             post = Post.objects.get(id=post_id)

#             # Assuming the files are sent as 'images' field in the request
#             albums = request.FILES.getlist('albums')

#             # Set the first image as the post's main image
#             if albums:
#                 post.image = albums[0]
#                 post.save()

#             for album in albums:
#                 post_album = PostImage.objects.create(post=post, album=album)

#             return Response({'detail': 'Images were uploaded successfully'})
#         except Exception as e:
#             logger.error(f'Error uploading images: {str(e)}')
#             return Response({'detail': 'Internal Server Error'}, status=500)


class UploadAlbum(APIView):
    parser_classes = (MultiPartParser, FormParser)
    GOOGLE_API_KEY = settings.GOOGLE_API_KEY

    def post(self, request):
        try:
            data = request.data
            post_id = data.get('post_id')
            post = Post.objects.get(id=post_id)
            community = post.community

            # Assuming the files are sent as 'albums' field in the request
            albums = request.FILES.getlist('albums')

            if len(albums) > 3:
                return Response({'detail': 'You can only upload up to 3 images.'}, status=status.HTTP_400_BAD_REQUEST)

            if community and community.ai_services:
                # Convert uploaded images to base64
                base64_images = [image_to_base64(album) for album in albums]

                # Generate markdown from images
                response_text = generate_markdown_from_images(base64_images, self.GOOGLE_API_KEY)

                if response_text == "NO":
                    post.delete()
                    return Response({'detail': 'The images were rejected by the AI.'}, status=status.HTTP_400_BAD_REQUEST)
                elif response_text == "YES":
                    # Set the first image as the post's main image
                    if albums:
                        post.image = albums[0]
                        post.save()

                    for album in albums:
                        PostImage.objects.create(post=post, album=album)

                    return Response({'detail': 'Images were uploaded successfully'})
                else:
                    post.delete()
                    return Response({'detail': 'The AI response was unclear, images were rejected.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Upload images without AI checks
                if albums:
                    post.image = albums[0]
                    post.save()

                for album in albums:
                    PostImage.objects.create(post=post, album=album)

                return Response({'detail': 'Images were uploaded successfully'})
        except Exception as e:
            print(f'Error uploading images: {str(e)}')
            return Response({'detail': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
class deleteComment(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        comment = get_object_or_404(Comment, id=pk)

        # Check if the user is either the author of the comment or the owner of the post
        if request.user == comment.user or request.user == comment.post.user:
            comment.delete()
            return Response("The Comment Was Deleted Successfully")
        else:
            return Response("You are not allowed to delete this comment", status=403)



#TOCHECK
class deletePost(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        post = get_object_or_404(Post, id=pk)

        # Check if the user is either the author of the post or the owner of the post
        if request.user == post.user :
            post.delete()
            return Response("The Post Was Deleted Successfully")
        else:
            return Response("You are not allowed to delete this post", status=403)
        




class GetPostsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Check if the user is blacklisted in the community
        if CommunityBlackList.objects.filter(user=user, community=user.community).exists():
            return Response({'detail': 'You are blacklisted and cannot fetch posts in this community.'}, status=status.HTTP_403_FORBIDDEN)

        # Retrieve posts from the community
        posts = Post.objects.filter(community=user.community)

        # Filter posts by name if provided
        name = request.query_params.get('name')
        if name is not None:
            posts = posts.filter(caption__icontains=name)

        # Use Django REST framework's built-in pagination
        paginator = PageNumberPagination()
        paginator.page_size = 10  # Set the number of posts per page
        result_page = paginator.paginate_queryset(posts, request)
        
        serializer = PostSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)



class GetPost(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = request.user

        # Check if the user is blacklisted in the community
        if CommunityBlackList.objects.filter(user=user, community=user.community).exists():
            return Response({'detail': 'You are blacklisted and cannot view posts in this community.'}, status=status.HTTP_403_FORBIDDEN)

        # Retrieve the post
        post = get_object_or_404(Post, id=pk)
        serializer = PostSerializer(post, many=False)
        return Response(serializer.data)


#NOTICE
@permission_classes([IsAuthenticated])
class LikePost(APIView):
    def post(self, request, pk):
        liker = request.user
        post = Post.objects.get(id=pk)

        # 1. If Follower already exists
        already_exists = Like.objects.filter(liker=liker, post=post).exists()

        if already_exists:
            # If Follower already exists, delete it (unfollow)
            Like.objects.filter(liker=liker, post=post).delete()
            return Response('Like Removed')

        else:
            # If Follower doesn't exist, create it (follow)
            like = Like.objects.create(
                liker=liker,
                post=post,
            )

            notice = Notice.objects.create(
                user=post.user,
                message=f"{liker.username} liked your Post",
            )
            return Response('Post Liked')





#NOTICE       
class CreateComment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        post = get_object_or_404(Post, id=pk)

        # Check if the user is blacklisted in the community
        if CommunityBlackList.objects.filter(user=user, community=user.community).exists():
            return Response({'detail': 'You are blacklisted and cannot add a comment to posts in this community.'}, status=status.HTTP_403_FORBIDDEN)

        # Check if the post is expired
        if post.is_expired:
            return Response({'detail': 'The discussion is closed.'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        parent_id = data.get('parent_id')
        comment_message = data.get('message', '')

        # Check if the comment already exists
        already_exists = Comment.objects.filter(user=user, post=post, message=comment_message).exists()
        if already_exists:
            return Response({'detail': 'Comment already added.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the comment message is more than 100 characters
        if len(comment_message) > 100:
            return Response({'detail': 'Comment cannot be more than 100 characters.'}, status=status.HTTP_400_BAD_REQUEST)

        # Filter profanity in the comment message
        if profanity.contains_profanity(comment_message):
            censored_text = profanity.censor(comment_message)
            comment_message = censored_text
            print(f"Profanity detected! Censored text: {censored_text}")

        parent_comment = None
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)

        comment = Comment.objects.create(
            user=user,
            post=post,
            message=comment_message,
            parent=parent_comment
        )

        return Response({'detail': 'Comment saved.'}, status=status.HTTP_201_CREATED)


class UpdatePost(APIView):
    def put(self, request, pk):
        post = Post.objects.get(id=pk)
        data = request.data
        expiration_hours = data.get('expiration_hours')

        post.caption = data.get('caption', post.caption)
        post.description = data.get('description', post.description)
        
        if expiration_hours:
            expiration_hours = int(expiration_hours)
            post.expiration_date = timezone.now() + timedelta(hours=expiration_hours)

        post.save()

        serializer = PostSerializer(post, many=False)
        return Response(serializer.data)


@permission_classes([IsAuthenticated])
class CreatePost(APIView):
    def post(self, request):
        user = request.user

        # Check if the user has a community
        if not user.community:
            return Response({'detail': 'You must be in a community to proceed.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user is blacklisted in the community
        if CommunityBlackList.objects.filter(user=user, community=user.community).exists():
            return Response({'detail': 'You are blacklisted and cannot make a post in this community.'}, status=status.HTTP_403_FORBIDDEN)

        # Create the post
        post = Post.objects.create(
            user=user,
            caption='',
            description='',
            community=user.community
        )

        # Serialize the post
        serializer = PostSerializer(post, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UploadVideo(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @transaction.atomic
    def post(self, request):
        try:
            data = request.data

            post_id = data.get('post_id')
            post = Post.objects.get(id=post_id)

            vid = request.FILES.get('video')
            if vid is None:
                raise ValidationError("No video file provided")

            self.validate_video_size(vid)

            # Update the post with the uploaded video
            post.video = vid
            # Set isSlice to True
            post.isSlice = True
            post.save()

            return Response({'detail': 'Video was uploaded successfully'})
        except ValidationError as e:
            error_message = "Validation Error: " + str(e)
            logger.error(f'Error uploading video: {error_message}')
            print(error_message)  # Print error to console
            return Response({'detail': error_message}, status=400)
        except Exception as e:
            error_message = "Internal Server Error: " + str(e)
            logger.error(f'Error uploading video: {error_message}')
            print(error_message)  # Print error to console
            return Response({'detail': error_message}, status=500)

    def validate_video_size(self, file):
        max_size = 262144000  # Maximum size in bytes (250 MB)
        if file.size > max_size:
            raise ValidationError("Maximum size for video is 250 MB")




from django.utils import timezone

class CheckExpiredPosts(APIView):
    def get(self, request):
        now = timezone.now()
        post_to_expire = Post.objects.filter(expiration_date__lte=now, is_expired=False).first()

        if post_to_expire:
            post_to_expire.is_expired = True
            post_to_expire.save()
            return Response({'detail': f'Post {post_to_expire.id} marked as expired'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'No posts to mark as expired'}, status=status.HTTP_200_OK)