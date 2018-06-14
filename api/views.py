###########
# imports #
###########

from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from api import models
from api import serializers
from api import permissions

#########
# users #
#########

class UserViewSet(viewsets.ModelViewSet):
    # default query-set and serializer for all actions
    queryset = models.User.objects.all()
    serializer_class = serializers.UserReadSerializer

    # set filtering options
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_fields = ["username", "email"]
    search_fields = ["username", "email"]
    ordering_fields = ["hearts", "date_joined"]

    def get_serializer_class(self):
        if self.action in permissions.WRITE_ACTIONS:
            return serializers.UserWriteSerializer
        return serializers.UserReadSerializer

    # custom actions
    @action(detail=True)
    def heart_user(self, request, pk=None):
        """
        API endpoint that allows users to be hearted. If authenticated, 
        a simple visit to this endpoint will heart or unheart the user.
        """
        target_user = self.get_object()
        source_user = request.user
        if target_user in source_user.hearted_users.all():
            source_user.hearted_users.remove(target_user)
        else:
            source_user.hearted_users.add(target_user)
        serializer = serializers.UserReadSerializer(source_user, context={"request" : request})
        return Response(serializer.data)

    # set permissions
    def get_permissions(self):
        permission_classes = []
        if self.action in permissions.WRITE_ACTIONS:
            permission_classes = [permissions.UserWrite]
        elif self.action == "heart_user":
            permission_classes = [permissions.UserHeart]
        return [permission() for permission in permission_classes]

################
# user courses #
################

class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows courses to be viewed (by all) or edited (by staff).
    """
    # default query-set and serializer for all actions
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer

    # set filtering options
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_fields = ["name", "code"]
    search_fields = ["name", "code"]
    ordering_fields = ["user_count"]
    
    # set permissions
    def get_permissions(self):
        permission_classes = []
        if self.action in permissions.WRITE_ACTIONS:
            permission_classes = [permissions.CourseWrite]
        return [permission() for permission in permission_classes]

############
# projects #
############

class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows projects to be viewed or edited.
    """
    # default query-set and serializer for all actions
    queryset = models.Project.objects.all().order_by('-timestamp')
    serializer_class = serializers.ProjectSerializer

    # set filtering options
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_fields = ["category", "tags", "name"]
    search_fields = ["name", "description"]
    ordering_fields = ["timestamp", "hearts"]

    # set permissions
    def get_permissions(self):
        permission_classes = []
        if self.action in permissions.WRITE_ACTIONS:
            permission_classes = [permissions.ProjectWrite]
        return [permission() for permission in permission_classes]

###############################
# project tags and categories #
###############################

class ProjectCategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows project categories to be viewed or edited.
    """
    # default query-set and serializer for all actions
    queryset = models.ProjectCategory.objects.all()
    serializer_class = serializers.ProjectCategorySerializer

    # set filtering options
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filter_fields = ["name"]
    search_fields = ["name"]

    # set permissions
    def get_permissions(self):
        permission_classes = []
        if self.action in permissions.WRITE_ACTIONS:
            permission_classes = [permissions.ProjectCategoryWrite]
        return [permission() for permission in permission_classes]

class ProjectTagViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows project tags to be viewed or edited.
    """
    # default query-set and serializer for all actions
    queryset = models.ProjectTag.objects.all()
    serializer_class = serializers.ProjectTagSerializer

    # set filtering options
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filter_fields = ["name"]
    search_fields = ["name"]

    # set permissions
    def get_permissions(self):
        permission_classes = []
        if self.action in permissions.WRITE_ACTIONS:
            permission_classes = [permissions.ProjectTagWrite]
        return [permission() for permission in permission_classes]

#########################
# project join requests #
#########################

class ProjectJoinRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows project join requests to be viewed or edited.
    """
    # default query-set and serializer for all actions
    queryset = models.ProjectJoinRequest.objects.all()
    serializer_class = serializers.ProjectJoinRequestSerializer

    # set filtering options
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_fields = ["user", "project"]
    search_fields = ["request"]
    ordering_fields = ["timestamp"]

    # set permissions
    def get_permissions(self):
        permission_classes = []
        if self.action in permissions.WRITE_ACTIONS:
            permission_classes = [permissions.ProjectJoinRequestWrite]
        return [permission() for permission in permission_classes]

####################
# project comments #
####################

class ProjectCommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows project comments to be viewed or edited.
    """
    # default query-set and serializer for all actions
    queryset = models.ProjectComment.objects.all().order_by('-timestamp')
    serializer_class = serializers.ProjectCommentSerializer

    # set filtering options
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_fields = ["user", "project"]
    search_fields = ["comment"]
    ordering_fields = ["timestamp"]

    # set permissions
    def get_permissions(self):
        permission_classes = []
        if self.action in permissions.WRITE_ACTIONS:
            permission_classes = [permissions.ProjectCommentWrite]
        return [permission() for permission in permission_classes]

#################
# project posts #
#################

class ProjectPostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows project posts to be viewed or edited.
    """
    # default query-set and serializer for all actions
    queryset = models.ProjectPost.objects.all().order_by('-timestamp')
    serializer_class = serializers.ProjectPostSerializer

    # set filtering options
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_fields = ["project"]
    search_fields = ["post"]
    ordering_fields = ["timestamp"]

    # TODO: how to prevent people creating posts in list view and associating
    # them with any random project?

    # set permissions
    def get_permissions(self):
        # for read actions
        if self.action in permissions.READ_ACTIONS:
            permission_classes = [permissions.ProjectPostRead]
        else: 
            permission_classes = [permissions.ProjectPostWrite]
        return [permission() for permission in permission_classes]
