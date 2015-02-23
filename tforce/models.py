from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from podcasting import models as podcasts

# Create your models here.

class TForceUser(models.Model):
    user = models.OneToOneField(User) #ForeignKey(User)

    def __unicode__(self):
        return self.user.username



class Channel(models.Model):
    name = models.CharField(max_length=240)
    members = models.ManyToManyField(TForceUser, related_name="channels", limit_choices_to=Q(user__is_staff=True))
    def __unicode__(self):
        return self.name

class ShowWrapper(models.Model):
    podcastShow = models.OneToOneField(podcasts.Show)
    channel = models.ForeignKey(Channel)
    members = models.ManyToManyField(TForceUser, related_name="shows_featured_in", limit_choices_to=Q(user__is_staff=True))

    def __unicode__(self):
        return self.podcastShow.title

    def last_updated_on(self):
        pass

class EpisodeWrapper(models.Model):
    '''STATUS_CHOICES = (
        (1, 'Draft'),
        (2, 'Published'),
    )
    '''
    #title = models.CharField(max_length=300)
    #number = models.IntegerField(auto
    synopsis = models.TextField()
    #originalPublishDate = models.DateField()
    #status = models.IntegerField('status', choices=STATUS_CHOICES, default=1)
    #episode_url = models.URLField()
    show = models.ForeignKey(ShowWrapper)
    podcastEpisode = models.OneToOneField(podcasts.Episode)
    members = models.ManyToManyField(TForceUser, related_name="episodes_featured_in", limit_choices_to=Q(user__is_staff=True))

    def __unicode__(self):
        return self.podcastEpisode.title
    
class Post(models.Model):
    STATUS_CHOICES = (
        (1, 'Draft'),
        (2, 'Public'),
    )

    title = models.CharField(max_length=150)
    body = models.TextField()
    status = models.IntegerField('status', choices=STATUS_CHOICES, 
                                 default=2)
    channel = models.ForeignKey(Channel, related_name='posts')

    def __unicode__(self):
        return self.name
     

class Poll(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __unicode__(self):
        return self.question

class Choice(models.Model):
    poll = models.ForeignKey(Poll)
    choice_text = models.CharField(max_length = 200)
    votes = models.IntegerField(default = 0)

    def __unicode__(self):
        return self.choice_text
