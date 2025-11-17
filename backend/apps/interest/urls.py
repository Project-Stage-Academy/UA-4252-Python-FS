from django.urls import path
from .views import ExpressInterestView

urlpatterns = [
    path("", ExpressInterestView.as_view(), name="express-interest"),
]
