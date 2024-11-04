from django.contrib.auth.models import AbstractUser, BaseUserManager, Permission
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from .validators import *
from django.conf import settings






class AdminArea(models.Model):
    name = models.CharField(max_length=255)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_areas')
    coordinates = models.TextField(blank=True, null=True)  # Field to store coordinates
    main_coordinate = models.CharField(max_length=255, blank=True, null=True)  # Field to store coordinates

    def __str__(self):
        return self.name


class Community(models.Model):
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='followers', default=1, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, default= "mrptjobs@gmail.com")
    bio = models.TextField(null=True, blank=True)
    area = models.ForeignKey(AdminArea, related_name='area', on_delete=models.CASCADE, blank=True, null=True)
    ai_services = models.BooleanField(default=False)


    def __str__(self):
        return self.name






class CommunityBlackList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_black', default=1, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, related_name='community_black', on_delete=models.CASCADE, blank=True, null=True)
    appeal_sent = models.BooleanField(default=False)


    # def __str__(self):
    #     return self.name



# # Cre
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)



AUTH_PROVIDERS ={'email':'email', 'google':'google'}

class CustomUser(AbstractUser):

    community = models.ForeignKey(Community, on_delete=models.SET_NULL, null=True, blank=True)
    area = models.ForeignKey(AdminArea, related_name='area_user', on_delete=models.SET_NULL, blank=True, null=True)
    points = models.IntegerField(default=0)
    is_demo = models.BooleanField(default=False)
    id = models.AutoField(primary_key=True, editable=False, default=None)
    auth_provider=models.CharField(max_length=50, blank=False, null=False, default=AUTH_PROVIDERS.get('email'))
    email = models.EmailField(unique=True)
    bio = models.TextField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    avi = models.ImageField(null=True, blank=True, default='/avatar.png')
    contact_number = models.CharField('Contact Number', max_length=15, null=True, blank=True)
    location = models.TextField('Location', null=True, blank=True)
    user_type = models.CharField(max_length=20, choices=[
        ('admin', 'admin'),
        ('normal', 'normal'),
        ('staff', 'staff'),

    ] ,blank=True, null=True )


    objects = CustomUserManager()
    user_permissions = models.ManyToManyField(Permission, verbose_name='user permissions', blank=True)



    class Meta(AbstractUser.Meta):
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.email

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            "refresh":str(refresh),
            "access":str(refresh.access_token)
        }





class Organization(models.Model):
    community = models.ForeignKey(Community, related_name='community_roganaization', on_delete=models.CASCADE, blank=True, null=True)

    name = models.CharField(max_length=255)
    consumer_key = models.CharField(max_length=255)
    consumer_secret = models.CharField(max_length=255)
    initiator_name = models.CharField(max_length=255)
    security_credential = models.CharField(max_length=255)
    shortcode = models.CharField(max_length=10)
    # Add other fields as necessary

    def __str__(self):
        return self.name






class Notice(models.Model):


    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField(default='Default message')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


    # Add other fields as needed

    def __str__(self):
        return f'{self.user.username} - {self.message}'

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        # Trigger Pusher after saving the notice



# class AdminArea(models.Model):
#     name = models.CharField(max_length=255)
#     admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='admin_areas')
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user', blank=True, null=True)
#     coordinates = models.TextField(blank=True, null=True)  # Field to store coordinates
#     main_coordinate = models.CharField(max_length=255, blank=True, null=True)  # Field to store coordinates

#     def __str__(self):
#         return self.name



class Point(models.Model):
    WASTE_TYPES = [
        ('Food', 'Food'),
        ('Plastic', 'Plastic'),
        ('Glass', 'Glass'),
        ('Metal', 'Metal'),
        ('Paper', 'Paper'),
        ('Organic', 'Organic'),
        ('Electronic', 'Electronic'),
        ('Hazardous', 'Hazardous'),
        ('General', 'General'),

    ]








    admin_area = models.ForeignKey(AdminArea, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    estate = models.CharField(max_length=255, null = True, blank = True)

    types = models.CharField(max_length=50, choices=WASTE_TYPES, default="General")


    def __str__(self):
        return self.location






class Trash(models.Model):
    WASTE_TYPES = [
        ('Food', 'Food'),
        ('Plastic', 'Plastic'),
        ('Glass', 'Glass'),
        ('Metal', 'Metal'),
        ('Paper', 'Paper'),
        ('Organic', 'Organic'),
        ('Electronic', 'Electronic'),
        ('Hazardous', 'Hazardous'),
        ('General', 'General'),

    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='trash_photos/')
    point = models.ForeignKey(Point, on_delete=models.CASCADE, blank=True, null=True)
    verification_status = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    types = models.CharField(max_length=50, choices=WASTE_TYPES, default="General")

    def __str__(self):
        return f'{self.user.username} - {self.timestamp} - {self.types}'



from ckeditor.fields import RichTextField

class Report(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    report = RichTextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    points = models.IntegerField(default=0)



    def __str__(self):
        return f'{self.community.name} - {self.timestamp}'




class IndividualLeaderboard(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.username} - {self.points} points'




class CommunityLeaderboard(models.Model):
    community = models.OneToOneField(Community, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.community.name} - {self.points} points'




class Questionnaire(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.community.name} - {self.timestamp}'


class Response(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE)
    interview_datetime = models.DateTimeField(blank=True, null=True)
    passed = models.BooleanField(default=False)


    def __str__(self):
        return f"Interview for {self.job.title} on {self.interview_datetime}"




class ResponseBlock(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name='blocks')
    question = models.TextField(blank=True, null=True)
    answer = models.TextField(blank=True, null=True)
    score = models.FloatField(default=0)  # New field for the score of each block


    time_taken = models.DurationField(blank=True, null=True)

    def __str__(self):
        return f"Block for session {self.session.id}: {self.question[:30]}"





from django.db import models
from django.utils import timezone
from datetime import timedelta

class Post(models.Model):
    caption = models.CharField(max_length=50)
    description = models.TextField(max_length=264)
    image = models.ImageField(null=True, blank=True)
    video = models.FileField(validators=[file_size], null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now=True)
    isSlice = models.BooleanField(default=False)
    community = models.ForeignKey(Community, on_delete=models.CASCADE, null=True, blank=True)
    expiration_date = models.DateTimeField(null=True, blank=True)
    is_expired = models.BooleanField(default=False)

    @property
    def user_avi(self):
        return self.user.avi if self.user else None

    @property
    def user_name(self):
        return self.user.email if self.user else None

    def __str__(self):
        return self.caption

    class Meta:
        ordering = ['-created_date']






class Like(models.Model):
    liker = models.ForeignKey(CustomUser, related_name='liker',on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now=True)


    @property
    def liker_avi(self):
        return self.liker.avi if self.liker else None


    @property
    def liker_name(self):
        return self.liker.username if self.liker else None

    class Meta:
        ordering = ['-created_date']




class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name = "albums")
    album = models.ImageField( null=True, blank=True)


class Video(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name = "videos")
    video=models.FileField(validators=[file_size])





class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True)
    message = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    @property
    def comment_avi(self):
        return self.user.avi if self.user else None

    @property
    def comment_email(self):
        return self.user.email if self.user else None

    def __str__(self):
        return self.message

    class Meta:
        ordering = ['-created_at']



class Insights(models.Model):
    trash = models.ForeignKey(Trash, on_delete=models.CASCADE, related_name='insights')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='insights')
    description = models.TextField()

    def __str__(self):
        return f"Insight by {self.user.username} on {self.trash.id}"
