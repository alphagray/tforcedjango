from django.conf.urls import *
from django.views.static import serve

urlpatterns = patterns(
    'app.views',
    url(r'^authtest/', 'app.views.authtest'),
    url(r'^complete/(P?<backend>[\w]+)/?', 'app.views.done'),
    url(r'^user/(P?<username>[\w]+)/$', 'app.userviews.profile', name='profile'),
)