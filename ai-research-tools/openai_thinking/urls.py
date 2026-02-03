from django.urls import path
from . import views

app_name = "openai_thinking"
urlpatterns = [
    path("", views.thinking_test_view, name="thinking_test"),
]
