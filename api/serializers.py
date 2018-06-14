###########
# imports #
###########

from rest_framework import serializers
from django.contrib.auth.models import Group
from api import models
from api import permissions

###################
# base serializer #
###################

# DRF serializers are weird because they either allow fields='' or exclude='',
# but not both. Usually, this would be fine, but we also want to show
# related_name fields in our API which correspond to ManyToMany and OneToMany
# back-references. So we use the BaseSerializer which gives us the
# "extra_fields" meta attribute "extra_fields" is useful because now we can
# explicitly add related_names

class BaseSerializer(serializers.HyperlinkedModelSerializer):
    def get_field_names(self, declared_fields, info):
        expanded_fields = super(BaseSerializer, self).get_field_names(
            declared_fields, info)
        if getattr(self.Meta, 'extra_fields', None):
            return expanded_fields + self.Meta.extra_fields
        else:
            return expanded_fields

#####################
# model serializers #
#####################

########
# user #
########

class UserWriteSerializer(BaseSerializer):
    class Meta:
        model = models.User
        fields = ["username", "password", "email", "first_name", 
        "last_name", "links", "image", "description"]

    def create(self, validated_data):
        user = models.User.objects.create_user(username=validated_data["username"],
                                               password=validated_data["password"],
                                               email=validated_data["email"])
        user.save()
        return user

class UserReadSerializer(BaseSerializer):
    class Meta:
        model = models.User
        exclude = ["is_superuser", "user_permissions", "groups"]
        extra_fields = ["member_projects", "leader_projects",
                        "hearted_by", "hearted_projects", "join_requests", "courses"]
        extra_kwargs = {'password': {'write_only': True}}

###########
# courses #
###########

class CourseSerializer(BaseSerializer):
    class Meta:
        model = models.Course
        fields = "__all__"
        
class ProjectCategorySerializer(BaseSerializer):
    class Meta:
        model = models.ProjectCategory
        fields = "__all__"
        extra_fields = ["projects"]

class ProjectTagSerializer(BaseSerializer):
    class Meta:
        model = models.ProjectTag
        extra_fields = ["projects"]
        fields = "__all__"

class ProjectSerializer(BaseSerializer):
    class Meta:
        model = models.Project
        fields = "__all__"
        extra_fields = ["join_requests", "comments", "posts"]
        
class ProjectJoinRequestSerializer(BaseSerializer):
    class Meta:
        model = models.ProjectJoinRequest
        fields = "__all__"

class ProjectCommentSerializer(BaseSerializer):
    class Meta:
        model = models.ProjectComment
        fields = "__all__"

    # exclude fields on a per-instance basis
    # but whose fields we still want to show on the browsable API on a list basis
    def to_representation(self, obj):
        representation = super(ProjectCommentSerializer,
                               self).to_representation(obj)
        if obj.anonymous:
            representation.pop("user")
        return representation

class ProjectPostSerializer(BaseSerializer):
    class Meta:
        model = models.ProjectPost
        fields = "__all__"

    # exclude fields on a per-instance basis
    # but whose fields we still want to show on the browsable API on a list basis
    def to_representation(self, obj):
        representation = super(ProjectPostSerializer,
                               self).to_representation(obj)
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        if obj.private:
            if permissions.CanReadPrivateProjectPost(user, obj) == False:
                representation.pop("post")
        return representation


