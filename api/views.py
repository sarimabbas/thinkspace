###########
# imports #
###########

# Shortcuts and Models
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.http import Http404

# View Builders
from rest_framework import viewsets, mixins, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

# Filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

# Models and Serializers
from api import models
from api import serializers

# Permissions
from api import permissions

#########
# users #
#########

class UserViewSet(viewsets.GenericViewSet,
                  mixins.ListModelMixin, mixins.RetrieveModelMixin, 
                  mixins.CreateModelMixin, mixins.DestroyModelMixin,
                  mixins.UpdateModelMixin):

    queryset = models.User.objects.all()

    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filter_fields = ["username", "email"]
    ordering_fields = ["hearts", "date_joined"]
    search_fields = ["username", "email"]
    
    def get_permissions(self):
        permission_classes = []
        if self.action in ["list", "retrieve"]:
            permission_classes = []
        if self.action in ["heart"]:
            permission_classes = [permissions.UserHeart]
        if self.action in ["destroy"]:
            permission_classes = [permissions.UserDestroy]
        if self.action in ["update", "partial_update"]:
            permission_classes = [permissions.UserUpdate]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ["create"]:
            return serializers.UserCreate
        if self.action in ["update", "partial_update"]:
            return serializers.UserUpdate
        return serializers.UserListRetrieve

    @action(detail=True)
    def heart(self, request, pk=None):
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
        serializer = serializers.UserListRetrieve(target_user, context={"request" : request})
        return Response(serializer.data)



    # def list(self, request):
    #     pass


    # def retrieve(self, request, pk=None):
    #     pass

    # def update(self, request, pk=None):
    #     pass

    # def partial_update(self, request, pk=None):
    #     pass

    # def destroy(self, request, pk=None):
    #     pass


    

# class UserViewSet(generics.):
#     authentication_classes = [BasicAuthentication]

#     # default query-set and serializer for all actions
#     queryset = models.User.objects.all()
#     serializer_class = serializers.UserReadSerializer

#     # set filtering options
#     filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
#     filter_fields = ["username", "email"]
#     search_fields = ["username", "email"]
#     ordering_fields = ["hearts", "date_joined"]

#     def get_serializer_class(self):
#         if self.action in permissions.WRITE_ACTIONS:
#             return serializers.UserWriteSerializer
#         return serializers.UserReadSerializer

#     # custom actions
#     @action(detail=True)
#     def heart_user(self, request, pk=None):
#         """
#         API endpoint that allows users to be hearted. If authenticated, 
#         a simple visit to this endpoint will heart or unheart the user.
#         """
#         target_user = self.get_object()
#         source_user = request.user
#         if target_user in source_user.hearted_users.all():
#             source_user.hearted_users.remove(target_user)
#         else:
#             source_user.hearted_users.add(target_user)
#         serializer = serializers.UserReadSerializer(source_user, context={"request" : request})
#         return Response(serializer.data)

#     # set permissions
#     def get_permissions(self):
#         permission_classes = []
#         if self.action in permissions.WRITE_ACTIONS:
#             permission_classes = [permissions.UserWrite]
#         elif self.action == "heart_user":
#             permission_classes = [permissions.UserHeart]
#         return [permission() for permission in permission_classes]

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

class ProjectViewSet(viewsets.ViewSet):
    # default query-set and serializer for all actions
    serializer_class = serializers.ProjectSerializer
    queryset = models.Project.objects.all().order_by('-timestamp')

    # set filtering options
    # filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    # filter_fields = ["category", "tags", "name"]
    # search_fields = ["name", "description"]
    # ordering_fields = ["timestamp", "hearts"]

    def list(self, request):
        queryset = models.Project.objects.filter()
        serializer = serializers.ProjectSerializer(queryset, many=True, context={"request" : request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = models.Project.objects.filter()
        project = get_object_or_404(queryset, pk=pk)
        serializer = serializers.ProjectSerializer(project, context={"request": request})
        return Response(serializer.data)

    # # make a join request
    # @action(methods=["get", "post", "delete"], detail=True)
    # def join_request(self, request, pk=None):
    #     """ Endpoint to allow for viewing and creation of join requests. """
    #     if self.method == "post":
    #     project = self.get_object()
    #     user = request.user
    #     # check if a join request exists
    #     join_request = models.ProjectJoinRequest.objects.filter(
    #         user=user, project=project)[0]
    #     # if it exists, delete the join request
    #     if join_request:
    #         join_request.delete()
    #     # if it does not, make the join request
    #     else:
    #         # it might be confusing: request means join_request. It also happens
    #         # to mean the HTTP request.
    #         join_request_serializer = serializers.ProjectJoinRequestSerializer(
    #             project=project, user=user, request=request.data, context={"request": request})
    #         if join_request_serializer.is_valid():
    #             join_request_serializer.save()
    #         else:
    #             return Response(join_request_serializer.errors,
    #                             status=status.HTTP_400_BAD_REQUEST)
    #     # return the project
    #     project_serializer = serializers.ProjectSerializer(
    #         project=project, context={"request": request})
    #     return Response(project_serializer.data)

    # set permissions
    # def get_permissions(self):
    #     permission_classes = []
    #     if self.action in permissions.WRITE_ACTIONS:
    #         permission_classes = [permissions.ProjectWrite]
    #     return [permission() for permission in permission_classes]

#########################
# project join requests #
#########################

class ProjectJoinRequestViewSet(viewsets.ViewSet):
    """
    API endpoint that allows project join requests to be viewed or edited.
    """
    serializer_class = serializers.ProjectJoinRequestSerializer
    queryset = models.ProjectJoinRequest.objects.all()

    def list(self, request, project_pk=None):
        queryset = models.ProjectJoinRequest.objects.filter(project=project_pk)
        serializer = serializers.ProjectJoinRequestSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None, project_pk=None):
        queryset = models.ProjectJoinRequest.objects.filter(pk=pk, project=project_pk)
        project_join_request = get_object_or_404(queryset, pk=pk)
        serializer = serializers.ProjectJoinRequestSerializer(project_join_request, context={'request': request})
        return Response(serializer.data)
    
    # set filtering options
    # filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    # filter_fields = ["user", "project"]
    # search_fields = ["request"]
    # ordering_fields = ["timestamp"]

    # set permissions
    # def get_permissions(self):
    #     permission_classes = []
    #     if self.action in permissions.WRITE_ACTIONS:
    #         permission_classes = [permissions.ProjectJoinRequestWrite]
    #     return [permission() for permission in permission_classes]

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
