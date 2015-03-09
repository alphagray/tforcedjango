from __future__ import unicode_literals
"""
Definition of models.
"""

from podcasting import models as pd
from model_utils.managers import PassThroughManager

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

import datetime
import app.managers as mngr

"""
Imports for incorporating django_podcasting content
"""
import json
import os
try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


"""
These two classes are useful for us to auto-convert channel names to lower case for searching. 
"""
class ModifyingFieldDescriptor(object):
    """ Modifies a field when set using the field's (overriden) .to_python() method. """
    def __init__(self, field):  
        self.field = field  
    def __get__(self, instance, owner=None):
        if instance is None:
            raise AttributeError('Can only be accessed via an instance.')  
        return instance.__dict__[self.field.name]
    def __set__(self, instance, value):
        instance.__dict__[self.field.name] = self.field.to_python(value)

class LowerCaseCharField(CharField):
    def to_python(self, value):
        value = super(LowerCaseCharField, self).to_python(value)
        if isinstance(value, basestring):
            return value.lower()
        return value
    def contribute_to_class(self, cls, name):
        super(LowerCaseCharField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, ModifyingFieldDescriptor(self))

# Create your models here.
 
class Channel(models.Model):
    name = LowerCaseCharField(max_length="50", primary_key=True)
    title = models.CharField(max_length="50", blank = False, editable = False, null = True) # this needs to be a nice name for the channel's lowercase name.
    members = models.ForeignKey(User, limit_choices_to={"is_staff":True})

    def clean(self): 
        self.title = self.name

    def __str__(self):
        return self.title
    pass


class Show(pd.Show):
    """ 
    A podcast show, which has several episodes
    """
    channel = models.ForeignKey(Channel)
    objects = PassThroughManager.for_queryset_class(mngr.ShowManager)()
    content = PassThroughManager.for_queryset_class(mngr.ContentManager)()
    pass

class Episode(pd.Episode):
    show = models.ForeignKey(Show)
    members = models.ForeignKey(User, limit_choices_to={"is_staff":True})
    objects = PassThroughManager.for_queryset_class(mngr.EpisodeManager)()
    content = PassThroughManager.for_queryset_class(mngr.ContentManager)()

    url = models.URLField(
        _("url"),
        help_text=_("""URL of the media file. <br /> It is <strong>very</strong>
            important to remember that for episode artwork to display in iTunes, image must be
            <a href="http://answers.yahoo.com/question/index?qid=20080501164348AAjvBvQ">
            saved to file's <strong>metadata</strong></a> before enclosure uploading!<br /><br />
            For best results, choose an attractive, original, and square JPEG (.jpg) or PNG (.png)
            image at a size of 1400x1400 pixels. The image will be
            scaled down to 50x50 pixels at smallest in iTunes."""))

    size = models.PositiveIntegerField(
        _("size"), help_text=_("The length attribute is the file size in bytes. "
                               "Find this information in the files properties "
                               "(on a Mac, ``Get Info`` and refer to the size row)"))
    mime = models.CharField(
        _("mime format"), max_length=4, choices=MIME_CHOICES,
        help_text=_("Supports mime types of: {0}".format(
            ", ".join([mime[0] for mime in MIME_CHOICES]))))
    bitrate = models.CharField(
        _("bit rate"), max_length=5, default="192",
        help_text=_("Measured in kilobits per second (kbps), often 128 or 192."))
    sample = models.CharField(
        _("sample rate"), max_length=5, default="44.1",
        help_text=_("Measured in kilohertz (kHz), often 44.1."))
    channel = models.CharField(
        _("channel"), max_length=1, default=2,
        help_text=_("Number of channels; 2 for stereo, 1 for mono."))
    duration = models.IntegerField(
        _("duration"), max_length=1,
        help_text=_("Duration of the audio file, in seconds (always as integer)."))

    class Meta:
        ordering = ("published", "url", "mime",)
        verbose_name = "Episode"
        verbose_name_plural = "Episodes"

    def __unicode__(self):
        return "{0} - {1}".format(self.url, self.mime)

    def __str__(self):
        return "{0} - {1}".format(self.url, self.mime)
    pass

class Blog(models.Model):
    title = models.CharField(max_length = "200", blank=False)
    members = models.ForeignKey(User, limit_choices_to={"is_staff":True})
    
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now_add=True, editable=False)
    published = models.DateTimeField(null=True, blank=True, editable=False)


    pass

class Post(models.Model):
    pass
#End post

class Calendar(models.Model):
    pass
#End calendar

class Signup(models.Model):
    event = models.ForeignKey(Event, "sign_up", blank=False)
    signedupusers = models.ManyToManyField(User)
    is_public = models.NullBooleanField(default=False, blank=False)
    sign_up_start_date = models.DateTimeField(blank=True)
    sign_up_end_date = models.DateTimeField(blank=True)

    pass
#End Signup

class Event(models.Model):
    IS_EXCLUSIVE = (
            (1, "Public"),
            (2, "By Sign-up Only"),
            (3, "Paid"),
    )

    use_signups = models.PositiveSmallIntegerField("Registration Type", choices=IS_EXCLUSIVE, default=1, help_text="""Select "Public" to remove sign ups for this event. Select "Sign-Up Only" to 
                                                                                                                      Add a Sign-Up task that will be advertised in the announcements section. Select
                                                                                                                      "Paid" to indicate that users have to buy access to this event via donation.""")
    
    start_date = models.DateTimeField(blank=False)
    end_date = models.DateTimeField(blank=False)
    

    def clean(self):
        if self.use_signups < 2:
            self.sign_up = None


# end Event
