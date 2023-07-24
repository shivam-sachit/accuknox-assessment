from django.urls import path

from social_api.api import (
    AcceptFriendRequestView,
    ListFriendsView,
    ListPendingFriendRequestsView,
    RejectFriendRequestView,
    SendFriendRequestView,
    UserLoginView,
    UserRegistrationView,
)

urlpatterns = [
    path('users/register', UserRegistrationView.as_view(), name='user-registration'),
    path('users/login', UserLoginView.as_view(), name='user-login'),
    path('users/send_friend_request', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('users/accept_friend_request/<int:pk>', AcceptFriendRequestView.as_view(), name='accept-friend-request'),
    path('users/reject_friend_request/<int:pk>', RejectFriendRequestView.as_view(), name='reject-friend-request'),
    path('users/friends/', ListFriendsView.as_view(), name='list-friends'),
    path('users/pending_friend_requests', ListPendingFriendRequestsView.as_view(), name='list-pending-friend-requests'),
]
