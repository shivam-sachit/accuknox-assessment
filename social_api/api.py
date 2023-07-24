from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, views, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from social_api.models import FriendRequest, User
from social_api.paginators import UserPagination
from social_api.serializers import (
    FriendRequestSerializer,
    FriendSerializer,
    UserLoginSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)


class UserRegistrationView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User successfully registered.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(ObtainAuthToken):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

class UserSearchViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        search_term = request.query_params.get('search_term', None)

        if not search_term:
            return Response(
                'Please provide a search term.',
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email__iexact=search_term)
        except User.DoesNotExist:
            users = User.objects.filter(name__icontains=search_term).order_by('name')
            paginator = UserPagination()
            page = paginator.paginate_queryset(users, request)
            if page is not None:
                serializer = UserSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)
        else:
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({}, status=status.HTTP_200_OK)


class SendFriendRequestView(generics.CreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def post(self, request):
        from_user = request.user
        to_user_id = request.data.get('to_user')

        if not to_user_id:
            return Response({'error': 'Please provide a "to_user" ID.'}, status=status.HTTP_400_BAD_REQUEST)

        to_user = get_object_or_404(User, id=to_user_id)
        if from_user == to_user:
            return Response({'error': 'You cannot send a friend request to yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            return Response({'error': 'You have already sent a friend request to this user.'}, status=status.HTTP_400_BAD_REQUEST)

        friend_request = FriendRequest(from_user=from_user, to_user=to_user)
        friend_request.save()
        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AcceptFriendRequestView(generics.UpdateAPIView):
    queryset = FriendRequest.objects.all()

    def update(self, request, *args, **kwargs):
        friend_request = self.get_object()
        if friend_request.to_user != request.user:
            return Response({'error': 'You are not authorized to accept this friend request.'}, status=status.HTTP_403_FORBIDDEN)

        friend_request.accepted = True
        friend_request.save()
        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data)

class RejectFriendRequestView(generics.DestroyAPIView):
    queryset = FriendRequest.objects.all()

    def delete(self, request, *args, **kwargs):
        friend_request = self.get_object()
        if friend_request.to_user != request.user:
            return Response({'error': 'You are not authorized to reject this friend request.'}, status=status.HTTP_403_FORBIDDEN)

        friend_request.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ListFriendsView(generics.ListAPIView):
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        friend_requests = FriendRequest.objects.filter(
            Q(from_user=user) | Q(to_user=user), accepted=True,
        )
        friend_ids = list(friend_requests.values_list('from_user', flat=True)) + list(friend_requests.values_list('to_user', flat=True))
        return User.objects.filter(id__in=friend_ids)

class ListPendingFriendRequestsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return FriendRequest.objects.filter(to_user=user, accepted=False)