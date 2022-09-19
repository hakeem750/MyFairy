from index.views.auth import *
from index.views.post_view import *
from index.views.cycle_view import *
# from index.views.chat import *


from django.urls import path


urlpatterns = [
    path("register", RegisterView.as_view(), name="register"),
    path("user_details/<int:pk>/", UserDetails.as_view()),
    path("login", Login.as_view()),
    path("forgot-password", ForgotPasswordView.as_view()),
    path("verify-password", VerifyForgotPasswordView.as_view()),
    path("enter-password", EnterPasswordView.as_view()),
    path("verify-email", VerifyEmail.as_view(), name="verify-email"),
    path("parent-email", ParentEmail.as_view()),
    path("get-conscent", GetConsent.as_view(), name="get-parent-consent"),
    path("posts/", PostList.as_view()),
    path("posts/<int:pk>/", PostDetail.as_view()),
    path("categories/", CategoryList.as_view()),
    path("categories/<int:pk>/", CategoryDetail.as_view()),
    path("like/<int:pk>/", LikeBlog.as_view(), name="like"),
    path("cycle-event/", ListEvent.as_view(), name="list-cycle"),
    path("create-cycles/", CreateCycleView.as_view(), name="create-cycle"),
    path("comments/<int:pk>/", CommentList.as_view()),
    path('follow_unfollow/',FollowUnfollowView.as_view(),name="follow_unfollow"),
    path('refer-a-friend/', ReferAFriend.as_view(), name="refer-a-friend"),
    path('add-a-fairy/', CreateFairyCycleView.as_view(), name="add-a-fairy"),
    path('share-cycle/', ShareCycleView.as_view(), name="share-cycle"),
    path('get-contacts/', GetContacts.as_view(), name="get-contacts"),
    path('search/', SearchView.as_view(), name="search"),
    
    
    # path("comments/<int:pk>/", CommentDetail.as_view()),
]
