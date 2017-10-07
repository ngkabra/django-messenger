from django.conf.urls import patterns, include, url
from views import FBMessengerProcessor

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'rsmessenger.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^fbmsg/$', FBMessengerProcessor.as_view(), name='msgr-fb-message-processor'),
)
