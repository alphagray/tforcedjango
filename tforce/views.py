# Create your views here.
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from tforce.models import *
from django.views.generic import DetailView, ListView
import tforce.utils


class ChannelDetailView(DetailView):
    def get_queryset(self):
        return Channel.objects.filter(title=self.kwargs["channel_name"])
        #return Channel.objects.all()

class ChannelContentListView(ListView):
    def get_queryset(self):
        try:
            channel = get_object_or_404(Channel.objects.get(name=self.kwargs["channel_name"]))
            shows = ShowWrapper.objects.filter(channel_id=channel.id)
            #posts = ShowWrapper.objects.filter(channel_id=
        return QuerySetChain(ShowWrapper.objects.filter(
        return 


class ShowDetailView(DetailView):
    def get_queryset(self):
        return ShowWrapper.objects.filter(podcastShow_title=self.kwargs["show_title"])

def vote(request, poll_id):
    p = get_object_or_404(Poll, pk=poll_id)
    try:
        selected_choice = p.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'tforce/detail.html', {
                'poll': p,
                'error_message': 'You didn\'t select a choice.'
            })

    else:
        selected_choice.votes += 1
        selected_choice.save()

        #Always return an HttpResponseRedirect after successfully dealing with
        # POST data. This prevents data from being posted twice if a user hits
        # the Back button

        return HttpResponseRedirect('polls:results', args=(p.id),)

