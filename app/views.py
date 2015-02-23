"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext
from tforce import models as tfm
from podcasting import models as podcasting
from datetime import datetime


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        context_instance=RequestContext(request,
            {
                'title':'Home Page',
                'year':datetime.now().year,
            })
    )

def tforce(request):
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/tforce.html',
        context_instance=RequestContext(request, 
            {
                'title': 'Trinity Force Podcast',
                'year': datetime.now().year,
            })
    )

def ozlol(request):
    try:
        ozlolShow = tfm.ShowWrapper.objects.get(podcastShow__title="OzLol")
        currentEpisode = ozlolShow.current_episode()
    except:
        currentEpisode = None
    return render(
        request,
        'tforce/ozlol.html',
        context_instance=RequestContext(request,
                                        {
                                            'title': 'OzLol Podcast',
                                            'year': datetime.now().year,
                                            'current_episode': currentEpisode 
                                            }))

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        context_instance=RequestContext(request,
            {
                'title':'Contact',
                'message':'Your contact page.',
                'year':datetime.now().year,
            })
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        context_instance=RequestContext(request,
            {
                'title':'About',
                'message':'Your application description page.',
                'year':datetime.now().year,
            })
    )
