from rest_framework.routers import DefaultRouter

from social_api.api import UserSearchViewSet

api_router = DefaultRouter()
api_router.register(r'users', UserSearchViewSet, basename='user')