from django.conf.urls import patterns, url
from django.views.generic import DetailView, ListView
from tforce.models import Poll

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
)