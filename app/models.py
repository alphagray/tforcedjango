from __future__ import unicode_literals
"""
Definition of models.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from model_utils.managers import PassThroughManager
from autoslug import AutoSlugField
from app.utils.twitter import can_tweet
from app.utils.querysetsequence import QuerySetSequence

def get_show_upload_folder(instance, pathname):
    "A standardized pathname for uploaded files and images."
    root, ext = os.path.splitext(pathname)
    return "img/podcasts/{0}/{1}{2}".format(instance.slug, slugify(root), ext)


def get_episode_upload_folder(instance, pathname):
    "A standardized pathname for uploaded files and images."
    root, ext = os.path.splitext(pathname)
    if instance.shows.count() == 1:
        return "img/podcasts/{0}/episodes/{1}{2}".format(
            instance.shows.all()[0].slug, slugify(root), ext
        )
    else:
        return "img/podcasts/episodes/{0}/{1}{2}".format(instance.slug, slugify(root), ext)

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

from django.contrib.sites.models import Site

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

class LowerCaseCharField(models.CharField):
    def to_python(self, value):
        value = super(LowerCaseCharField, self).to_python(value)
        if isinstance(value, basestring):
            return value.lower()
        return value
    def contribute_to_class(self, cls, name):
        super(LowerCaseCharField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, ModifyingFieldDescriptor(self))


"""
utility methods
"""

# optional external dependencies
try:
    from licenses.models import License
except:
    License = None

try:
    from imagekit.models import ImageSpecField
    from imagekit.processors import ResizeToFill
except ImportError:
    ResizeToFill = ImageSpecField = None

try:
    from easy_thumbnails.fields import ThumbnailerImageField as ImageField
    custom_image_field = True
except ImportError:
    custom_image_field = False

if not custom_image_field:
    try:
        from sorl.thumbnail import ImageField  # noqa
        custom_image_field = True
    except ImportError:
        custom_image_field = False

if not custom_image_field:
    # image-kit uses the standard ImageField as well
    from django.db.models import ImageField  # noqa

if "taggit" in settings.INSTALLED_APPS:
    from taggit.managers import TaggableManager
else:
    def TaggableManager(blank=True):  # noqa
        return None
try:
    import twitter
except ImportError:
    twitter = None  # noqa

try:
    from embed_video.fields import EmbedVideoField
except ImportError:
    EmbedVideoField = None

# Create your models here.

class Profile(models.Model):
    USER_LEVEL_CHOICES = ((1, "Free"),(2, "Premium"),)
    user = models.OneToOneField(User, null=True, blank=False)
    userLevel = models.PositiveSmallIntegerField(verbose_name="User Level", choices=USER_LEVEL_CHOICES, default=1, null=True, blank=False)
    firstName = models.CharField(max_length=142, blank=False, null=True)
    lastName = models.CharField(max_length=142, blank=False, null=True)

    datejoined = models.DateField(verbose_name="Date Joined", auto_now_add=True, editable=False)
    birthday = models.DateField(verbose_name="Birthday", null=True, blank=True)
    lanzobotpts = models.PositiveIntegerField(verbose_name="Lanzobot Points", null=True, blank=True)
    avatar_height = models.IntegerField(null=True, blank=True, editable=False)
    avatar_width = models.IntegerField(null=True, blank=True, editable=False)
    avatar = models.ImageField(width_field="avatar_width", height_field="avatar_height", null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    
    placeheld = models.BooleanField(default=False)
    placeholderName = models.CharField(max_length=25, blank=False, null=True, unique=True)

    bio = models.TextField(blank = False, null=True)

    @property
    def last_appeared_on(self): 
        return Content.objects.exclude(published=None).filter(members__contains=self).orderby("-published").first()

    @property
    def fullname(self):
        if not self.placeheld:
            return self.firstName + " " + self.lastName 
        else:
            return self.placeholderName

    @property
    def is_staff(self):
        return (self.user.is_staff and self.user.is_active) and not self.placeheld
    
    @property
    def is_active(self):
        return self.user.is_active and not self.placeheld

    @classmethod
    def create(cls, username):
        profile = cls(user=User.objects.get_by_natural_key(username))
        return profile

    def save(self, *args, **kwargs):
        if not self.placeheld:
            if self.is_staff:
                #make a few fields required.
                self.clean_fields([placeheld, placeholderName])
                super(Profile, self).save(*args, **kwargs)
            else:
                self.clean_fields([bio, last_appeared, placeheld, placeholderName])
                super(Profile, self).save(*args, **kwargs)
        else:
            self.clean_fields([bio, last_appeared])

    def __str__(self):
        if not self.placeheld:
            return self.user.username
        else:
            return self.placeholderName

class Channel(models.Model):

    title = models.CharField(max_length=150, unique=True, null=False, blank=False)
    members = models.ManyToManyField(Profile, limit_choices_to={"user__is_staff":True}, blank=False, null=True, default=None)
    tags = TaggableManager(blank=True)
    objects = models.Manager()
    
    @property
    def shows(self):
        return self.content_set.exclude(show__exact=None)

    @property
    def episodes(self):
        from django.db.models import Q
        return Episode.objects.filter(Q(content_ptr__channel__in=[self])|Q(shows__in=list(self.shows)))
    
    @property
    def blogs(self):
        return self.content_set.exclude(blog__exact=None)

    @property
    def posts(self):
        return Post.objects.filter(Q(content_ptr__channel__in=[self])|Q(blogs__in=list(self.blogs)))

    @property
    def latest_published(self):
        return self.content_set.latest("published")

    @property
    def latest_episode(self):
        return self.episodes.latest("published")


    def __str__(self):
        return self.title

#Abstract base class for all content that goes into a channel. 
class Content(models.Model):
    from model_utils import managers as mum
    title = models.CharField(max_length=255, unique=True, null=False, blank=False)
    members = models.ManyToManyField(Profile, limit_choices_to={"user__is_staff":True}, null=True, default=None)
    created = models.DateTimeField(_("created"), auto_now_add=True, editable=False)
    updated = models.DateTimeField(_("updated"), auto_now=True, editable=False)
    published = models.DateTimeField(_("published"), null=True, blank=True, editable=False)
    objects = PassThroughManager.for_queryset_class(mngr.ContentManager)()
    channel = models.ManyToManyField(Channel, null=True, default=None)

    STATUS_CHOICES = ((1, "Draft"), (2, "Published"),)

    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)

    def publish(self):
        self.status = 1
        self.published = datetime.datetime.now().__str__()
        return self.save()

    @property
    def channels(self):
        if(type(self) is Content):
            return self.channel.all()
        else:
            return self.content_ptr.channels

class Community(models.Model):
    users = models.ManyToManyField(Profile, related_name="communities")
    content = models.ForeignKey(Content, related_name="communities")

    def __str__(self):
        return self.content.title + " Users"

class Show(Content):
    """ 
    A podcast show, which has several episodes
    """
    

    EXPLICIT_CHOICES = (
        (1, _("yes")),
        (2, _("no")),
        (3, _("clean")),
    )
    
    #uuid = UUIDField(_("id"), unique=True)

    

    #sites = models.ManyToManyField(Site, verbose_name=_('Sites'))

    ttl = models.PositiveIntegerField(
        _("ttl"), default=1440,
        help_text=_("""``Time to Live,`` the number of minutes a channel can be
        cached before refreshing."""))

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="podcast_shows",
        verbose_name=_("owner"),
        help_text=_("""Make certain the user account has a name and e-mail address."""))

    editor_email = models.EmailField(
        _("editor email"), blank=True,
        help_text=_("Email address of the person responsible for the feed's content."))
    webmaster_email = models.EmailField(
        _("webmaster email"), blank=True,
        help_text=_("Email address of the person responsible for channel publishing."))

    if 'licenses' in settings.INSTALLED_APPS:
        license = models.ForeignKey(License, verbose_name=_("license"))
    else:
        license = models.CharField(
            _("license"), max_length=255,
            help_text=_("To publish a podcast to iTunes it is required to set a license type."))

    organization = models.CharField(
        _("organization"), max_length=255,
        help_text=_("Name of the organization, company or Web site producing the podcast."))
    link = models.URLField(_("link"), help_text=_("""URL of either the main website or the
        podcast section of the main website."""))

    enable_comments = models.BooleanField(default=True)

    author_text = models.CharField(
        _("author text"), max_length=255, help_text=_("""
            This tag contains the name of the person or company that is most
            widely attributed to publishing the Podcast and will be
            displayed immediately underneath the title of the Podcast.
            The suggested format is: 'email@example.com (Full Name)'
            but 'Full Name' only, is acceptable. Multiple authors
            should be comma separated."""))

    #title = models.CharField(_("title"), max_length=255)
    slug = AutoSlugField(_("slug"), populate_from="title", unique="True")

    subtitle = models.CharField(
        _("subtitle"), max_length=255,
        help_text=_("Looks best if only a few words, like a tagline."))

    # If the show is not on iTunes, many fields may be ignored in your user forms
    on_itunes = models.BooleanField(
        _("iTunes"), default=True,
        help_text=_("Checked if the podcast is submitted to iTunes"))

    description = models.TextField(
        _("description"), max_length=4000, help_text=_("""
            This is your chance to tell potential subscribers all about your
            podcast. Describe your subject matter, media format,
            episode schedule, and other relevant info so that they
            know what they'll be getting when they subscribe. In
            addition, make a list of the most relevant search terms
            that you want yourp podcast to match, then build them into
            your description. Note that iTunes removes podcasts that
            include lists of irrelevant words in the itunes:summary,
            description, or itunes:keywords tags. This field can be up
            to 4000 characters."""))

    original_image = ImageField(
        _("image"), upload_to=get_show_upload_folder, blank=True, help_text=_("""
            A podcast must have 1400 x 1400 pixel cover art in JPG or PNG
            format using RGB color space. See our technical spec for
            details. To be eligible for featuring on iTunes Stores,
            choose an attractive, original, and square JPEG (.jpg) or
            PNG (.png) image at a size of 1400x1400 pixels. The image
            will be scaled down to 50x50 pixels at smallest in iTunes.
            For reference see the <a
            href="http://www.apple.com/itunes/podcasts/specs.html#metadata">iTunes
            Podcast specs</a>.<br /><br /> For episode artwork to
            display in iTunes, image must be <a
            href="http://answers.yahoo.com/question/index?qid=20080501164348AAjvBvQ">
            saved to file's <strong>metadata</strong></a> before
            enclosure uploading!"""))

    if ResizeToFill:
        admin_thumb_sm = ImageSpecField(source="original_image",
                                        processors=[ResizeToFill(50, 50)],
                                        options={"quality": 100})
        admin_thumb_lg = ImageSpecField(source="original_image",
                                        processors=[ResizeToFill(450, 450)],
                                        options={"quality": 100})
        img_show_sm = ImageSpecField(source="original_image",
                                     processors=[ResizeToFill(120, 120)],
                                     options={"quality": 100})
        img_show_lg = ImageSpecField(source="original_image",
                                     processors=[ResizeToFill(550, 550)],
                                     options={"quality": 100})
        img_itunes_sm = ImageSpecField(source="original_image",
                                       processors=[ResizeToFill(144, 144)],
                                       options={"quality": 100})
        img_itunes_lg = ImageSpecField(source="original_image",
                                       processors=[ResizeToFill(1400, 1400)],
                                       options={"quality": 100})

    feedburner = models.URLField(
        _("feedburner url"), blank=True,
        help_text=_("""Fill this out after saving this show and at least one
            episode. URL should look like "http://feeds.feedburner.com/TitleOfShow".
            See <a href="http://code.google.com/p/django-podcast/">documentation</a>
            for more. <a href="http://www.feedburner.com/fb/a/ping">Manually ping</a>"""))

    # iTunes specific fields
    explicit = models.PositiveSmallIntegerField(
        _("explicit"), default=1, choices=EXPLICIT_CHOICES,
        help_text=_("``Clean`` will put the clean iTunes graphic by it."))
    redirect = models.URLField(
        _("redirect"), blank=True,
        help_text=_("""The show's new URL feed if changing
            the URL of the current show feed. Must continue old feed for at least
            two weeks and write a 301 redirect for old feed."""))
    keywords = models.CharField(
        _("keywords"), max_length=255, blank=True,
        help_text=_("""A comma-demlimitedlist of up to 12 words for iTunes
            searches. Perhaps include misspellings of the title."""))
    itunes = models.URLField(
        _("itunes store url"), blank=True,
        help_text=_("""Fill this out after saving this show and at least one
            episode. URL should look like:
            "http://phobos.apple.com/WebObjects/MZStore.woa/wa/viewPodcast?id=000000000".
            See <a href="http://code.google.com/p/django-podcast/">documentation</a> for more."""))

    twitter_tweet_prefix = models.CharField(
        _("Twitter tweet prefix"), max_length=80,
        help_text=_("Enter a short ``tweet_text`` prefix for new episodes on this show."),
        blank=True)

    objects = PassThroughManager.for_queryset_class(mngr.ShowManager)()
    tags = TaggableManager(blank = True)

    class Meta:
        verbose_name = _("Show")
        verbose_name_plural = _("Shows")
        ordering = ("organization", "slug")

    def __str__(self):
        return self.title

    def get_share_url(self):
        return "http://{0}{1}".format(Site.objects.get_current(), self.get_absolute_url())

    def get_absolute_url(self):
        return reverse("podcasting_show_detail", kwargs={"slug": self.slug})

    @property
    def current_episode(self):
        try:
            return self.episodes.published().order_by("-published")[0]
        except IndexError:
            return None

    @classmethod
    def create(cls, username, **kwargs):
        show = cls(owner=User.objects.get_by_natural_key(username), **kwargs)
        return show


class Episode(Content):
    shows = models.ManyToManyField(Show, related_name=_("episodes"))
    objects = PassThroughManager.for_queryset_class(mngr.EpisodeManager)()
    tags = TaggableManager(blank = True)
    SIXTY_CHOICES = tuple((x, x) for x in range(60))
    
    enable_comments = models.BooleanField(default=True)

    slug = AutoSlugField(_("slug"), populate_from="title", unique="True")

    subtitle = models.CharField(
        _("subtitle"), max_length=255, blank=True,
        help_text=_("Looks best if only a few words like a tagline."))

    description = models.TextField(
        _("description"), max_length=4000, blank=True, help_text=_("""
            This is your chance to tell potential subscribers all about your podcast.
            Describe your subject matter, media format, episode schedule, and other
            relevant info so that they know what they'll be getting when they
            subscribe. In addition, make a list of the most relevant search terms
            that you want your podcast to match, then build them into your
            description. Note that iTunes removes podcasts that include lists of
            irrelevant words in the itunes:summary, description, or
            itunes:keywords tags. This field can be up to 4000 characters."""))
    tracklist = models.TextField(
        _("tracklist"), blank=True,
        help_text=_("""One track per line, machine will automatically add the numbers."""))

    tweet_text = models.CharField(_("tweet text"), max_length=140, editable=False)

    original_image = ImageField(
        _("image"), upload_to=get_episode_upload_folder, blank=True, help_text=_("""
            A podcast must have 1400 x 1400 pixel cover art in JPG or PNG
            format using RGB color space. See our technical spec for
            details. To be eligible for featuring on iTunes Stores,
            choose an attractive, original, and square JPEG (.jpg) or
            PNG (.png) image at a size of 1400x1400 pixels. The image
            will be scaled down to 50x50 pixels at smallest in iTunes.
            For reference see the <a
            href="http://www.apple.com/itunes/podcasts/specs.html#metadata">iTunes
            Podcast specs</a>.<br /><br /> For episode artwork to
            display in iTunes, image must be <a
            href="http://answers.yahoo.com/question/index?qid=20080501164348AAjvBvQ">
            saved to file's <strong>metadata</strong></a> before
            enclosure uploading!"""))

    if ImageSpecField:
        admin_thumb_sm = ImageSpecField(source="original_image",
                                        processors=[ResizeToFill(50, 50)],
                                        options={"quality": 100})
        admin_thumb_lg = ImageSpecField(source="original_image",
                                        processors=[ResizeToFill(450, 450)],
                                        options={"quality": 100})
        img_episode_sm = ImageSpecField(source="original_image",
                                        processors=[ResizeToFill(120, 120)],
                                        options={"quality": 100})
        img_episode_lg = ImageSpecField(source="original_image",
                                        processors=[ResizeToFill(550, 550)],
                                        options={"quality": 100})
        img_itunes_sm = ImageSpecField(source="original_image",
                                       processors=[ResizeToFill(144, 144)],
                                       options={"quality": 100})
        img_itunes_lg = ImageSpecField(source="original_image",
                                       processors=[ResizeToFill(1400, 1400)],
                                       options={"quality": 100})

    # iTunes specific fields
    hours = models.SmallIntegerField(_("hours"), max_length=2, default=0)
    minutes = models.SmallIntegerField(_("minutes"), max_length=2, default=0, choices=SIXTY_CHOICES)
    seconds = models.SmallIntegerField(_("seconds"), max_length=2, default=0, choices=SIXTY_CHOICES)
    keywords = models.CharField(
        _("keywords"), max_length=255, blank=True,
        help_text=_("A comma-delimited list of words for searches, up to 12; "
                    "perhaps include misspellings."))
    explicit = models.PositiveSmallIntegerField(
        _("explicit"), choices=Show.EXPLICIT_CHOICES,
        help_text=_("``Clean`` will put the clean iTunes graphic by it."), default=1)
    block = models.BooleanField(
        _("block"), default=False,
        help_text=_("Check to block this episode from iTunes because <br />its "
                    "content might cause the entire show to be <br />removed from iTunes."""))

    author_text = models.CharField(
        _("author text"), max_length=255, help_text=_("""
            This tag contains the name of the person or company that is most
            widely attributed to publishing the Podcast and will be
            displayed immediately underneath the title of the Podcast.
            The suggested format is: 'email@example.com (Full Name)'
            but 'Full Name' only, is acceptable. Multiple authors
            should be comma separated."""))

    ### The following fields relate to the actual audo file itself.

    try:
        MIME_CHOICES = settings.PODCASTING_MIME_CHOICES
    except AttributeError:
        MIME_CHOICES = (
            ("aiff", "audio/aiff"),
            ("flac", "audio/flac"),
            ("mp3", "audio/mpeg"),
            ("mp4", "audio/mp4"),
            ("ogg", "audio/ogg"),
            ("flac", "audio/flac"),
            ("wav", "audio/wav"),
        )

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
    sound_channel = models.CharField(
        _("sound_channel"), max_length=1, default=2,
        help_text=_("Number of channels; 2 for stereo, 1 for mono."))
    duration = models.IntegerField(
        _("duration"), max_length=1,
        help_text=_("Duration of the audio file, in seconds (always as integer)."))

    class Meta:
        ordering = ("published", "url", "mime",)
        verbose_name = "Episode"
        verbose_name_plural = "Episodes"

    def __unicode__(self):
        return "{0} - {1}".format(self.title, self.mime)

    def __str__(self):
        return "{0} - {1}".format(self.title, self.mime)
    
    def get_absolute_url(self):
        return reverse("podcasting_episode_detail",
                       kwargs={"show_slug": self.shows.all()[0].slug, "slug": self.slug})

    def as_tweet(self):
        if not self.tweet_text:
            current_site = Site.objects.get_current()
            api_url = "http://api.tr.im/api/trim_url.json"
            u = urlopen("{0}?url=http://{1}{2}".format(
                api_url,
                current_site.domain,
                self.get_absolute_url(),
            ))
            result = json.loads(u.read())
            self.tweet_text = "{0} {1} - {2}".format(
                self.shows.all()[0].episode_twitter_tweet_prefix,
                self.title,
                result["url"],
            )
        return self.tweet_text

    def tweet(self):
        if can_tweet():
            account = twitter.Api(
                username=settings.TWITTER_USERNAME,
                password=settings.TWITTER_PASSWORD)
            account.PostUpdate(self.as_tweet())
        else:
            raise ImproperlyConfigured(
                "Unable to send tweet due to either "
                "missing python-twitter or required settings.")

    def seconds_total(self):
        try:
            return self.minutes * 60 + self.seconds
        except:
            return 0

    def get_share_url(self):
        return "http://{0}{1}".format(Site.objects.get_current(), self.get_absolute_url())

    def get_share_title(self):
        return self.title

    def get_share_description(self):
        return "{0}...".format(self.description[:512])

    @property
    def is_show_published(self):
        for show in self.shows.all():
            if show.published:
                return True
        return False

    @property
    def parents(self):
        return self.shows.all()

class Blog(Content):
    #title = models.CharField(max_length = "200", unique=True)
    #members = models.ForeignKey(User, limit_choices_to={"is_staff":True})
    
    body = models.TextField()
    slug = AutoSlugField(_("slug"), populate_from="title", unique=True)
    pass
#End blog
    


class Post(Content):
    blog = models.ManyToManyField(Blog, related_name="posts", null=False, blank=False)
    author = models.ForeignKey(Profile, related_name="author", limit_choices_to={'user__is_staff':True})
    tags = TaggableManager(blank = True)
    slug = AutoSlugField(populate_from="title", unique=True)
    
    def save(self):
        # here we're just appending the author's name to the title if this is the first time it's been saved.
        if not self.created:
            tempTitle = self.title + " - " + self.author.fullname
            self.title = tempTitle
        return super(Post, self).save()
        
    @property
    def parents(self):
        return self.blog.all()

    pass
#End post



class Feed(models.Model):
    ''' This is a custom feed that is created and saved for a given user. 
        It's really just a record with UUID that points to a feed URL so that we can push notifications out 
        whenever their feed would be updated. '''
    link = models.URLField()
    profile = models.ForeignKey(Profile , related_name="feeds", null=False)

    @property
    def user(self):
        return self.profile.user

    pass
#end feed


class Calendar(Content):
    pass
#End calendar

class Event(Content):

    calendars = models.ManyToManyField(Calendar, related_name="events", null=False)

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
    tags = TaggableManager(blank = True)

    @property
    def parent(self):
        return self.calendars.all()

    def clean(self):
        if self.use_signups < 2:
            self.sign_up = None
# end Event
