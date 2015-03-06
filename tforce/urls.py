from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView
from app import views
from tforce.models import *
from tforce.views import *

urlpatterns = patterns('',
    url(r'^$',
        ListView.as_view(
            queryset=Poll.objects.order_by('-pub_date')[:5],
            context_object_name='latest_poll_list',
            template_name='tforce/index.html'),
        name='index'),
    url(r'^(?P<pk>\d+)/$',
        DetailView.as_view(
            model=Poll,
            template_name='tforce/detail.html'),
        name='detail'),
    url(r'^(?P<pk>\d+)/results/$',
        DetailView.as_view(
            model=Poll,
            template_name='tforce/results.html'),
        name='results'),
    url(r'^(?P<poll_id>\d+)/vote/$', 'tforce.views.vote', name='vote'),
    url(r'^(?P<channel_name>[-\w]+)/$', ChannelDetailView.as_view(), name="tforce_channel"),
    url(r'^(?P<channel_name>[-\w]+)/archive/$', ChannelContentListView.as_view(), name="tforce_channel_archive"),
        #ShowDetailView.as_view(), name="tforce_show"),
    url(r'^(?P<channel_name>[-\w]+)/(?P<show_slug>[-\w]+)/(?P<
)