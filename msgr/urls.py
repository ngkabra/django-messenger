from django.conf.urls import url
from . import views as v

urlpatterns = [
    url(r'^fbmsg/$',
        v.FBMessengerProcessor.as_view(),
        name='msgr-fb-message-processor'),
]

