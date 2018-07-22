###########
# imports #
###########

from rest_framework import permissions
from api import models

SAFE_METHODS = ["GET", "HEAD", "OPTIONS"]
WRITE_ACTIONS = ["create", "update", "partial_update", "destroy"]
READ_ACTIONS = ["list", "retrieve"]

#########################
# convenience functions #
#########################


def CanWriteGeneric(user, obj_with_user_field):
    if user.is_staff:
        return True
    elif user == obj_with_user_field.user:
        return True
    else:
        return False

class Nope(permissions.BasePermission):
    def has_permission(self, request, view):
        return False

    def has_object_permission(self, request, view, obj):
        return False

#########
# users #
#########


class IsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

def CanWriteUser(user, user_obj):
    if user.is_staff:
        return True
    elif (user == user_obj):
        return True
    else:
        return False

class UserWrite(permissions.BasePermission):
    def has_permission(self, request, view):
        """ Anyone can create a user """
        return True

    def has_object_permission(self, request, view, obj):
        """ Only staff members, owning user can write existing user """
        return CanWriteUser(request.user, obj)

class UserHeart(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if request.user != obj:
                return True
        return False

class UserDestroy(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if request.user == obj:
                return True
        return False

class UserUpdate(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            if request.user == obj:
                return True
        return False

###########
# courses #
###########

class CourseWrite(permissions.BasePermission):
    def has_permission(self, request, view):
        """ Only staff members can create courses """
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        """ Only staff members can write existing courses """
        return request.user.is_staff

############
# projects #
############

def CanWriteProject(user, project):
    if user.is_staff:
        return True
    elif (user in project.leaders.all()):
        return True
    else:
        return False

class ProjectWrite(permissions.BasePermission):
    def has_permission(self, request, view):
        """ All authenticated users can create projects """
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """ Staff members, project leaders can write to existing projects """
        return CanWriteProject(request.user, obj)

#########################
# project join requests #
#########################

class ProjectJoinRequestWrite(permissions.BasePermission):
    def has_permission(self, request, view):
        """ All authenticated users can create join requests """
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """ Staff members, join request owners can write to existing join requests """
        return CanWriteGeneric(request.user, obj)

###############################
# project tags and categories #
###############################

class ProjectTagWrite(permissions.BasePermission):
    def has_permission(self, request, view):
        """ All authenticated users can create tags """
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """ Only staff members can write existing tags """
        return request.user.is_staff

class ProjectCategoryWrite(permissions.BasePermission):
    def has_permission(self, request, view):
        """ Only staff members can create categories """
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        """ Only staff members can write existing categories """
        return request.user.is_staff

####################
# project comments #
####################

class ProjectCommentWrite(permissions.BasePermission):
    def has_permission(self, request, view):
        """ All authenticated users can create comments """
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """ Staff members, comment owners can write existing comments """
        return CanWriteGeneric(request.user, obj)

#################
# project posts #
#################

def CanReadPrivateProjectPost(user, post):
    if user.is_staff:
        return True
    elif (user in post.project.members.all()) or (user in post.project.leaders.all()):
        return True
    else:
        return False

class ProjectPostRead(permissions.BasePermission):
    def has_permission(self, request, view):
        """ Everyone can read posts list. However, some information may be 
        hidden for private posts. View seralizers.py """
        return True
    
    def has_object_permission(self, request, view, obj):
        """ Only staff members, project members, project leaders can read private posts. 
        Everyone can read public posts """
        if obj.private:
            return CanReadPrivateProjectPost(request.user, obj)
        else:
            return True

def CanWriteProjectPost(user, post):
    if user.is_staff:
        return True
    elif (user in post.project.leaders.all()):
        return True
    else:
        return False

class ProjectPostWrite(permissions.BasePermission):
    def has_permission(self, request, view):
        """ All authenticated users can create posts """
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """ Staff members, project leaders can write to existing post objects """
        return CanWriteProjectPost(request.user, obj)

