from django.urls import path
from .views import *
from django.conf import settings


urlpatterns = [
    path("", landing, name="landing"), #for landing page
    path("home", home, name="home"),
    path("habib/", habib_chatbot, name="habib_chatbot"),
    path("hannibal/", hannibal_chatbot, name="hannibal_chatbot"),
    path("elissa/", elissa_chatbot, name="elissa_chatbot"),
    path("api/chatbot/<str:personality>/", chatbot_api, name="chatbot-api"),
    path("api/generate-speech/", generate_speech, name="generate_speech"),
]
