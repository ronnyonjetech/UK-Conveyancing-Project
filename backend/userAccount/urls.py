from django.urls import path
from . import views
from .views import CustomUserCreate,BlacklistTokenView
from .views import MyTokenObtainPairView
from rest_framework_simplejwt.views import (
    #TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns=[
    path('',views.getRoutes),
    path('token/',MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/',CustomUserCreate.as_view(),name="create_user"),
    path('logout/blacklist/', BlacklistTokenView.as_view(),
         name='blacklist')
]
