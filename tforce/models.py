from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Post(models.Model):

    STATUS_CHOICES = (
        (1, 'Draft'),
        (2, 'Public'),
    )

    title = models.CharField(max_length=150)
    body = models.TextField()
    status = models.IntegerField('status', choices=STATUS_CHOICES, 
                                 default=2)


class TforceUser(models.Model):

    STATUS_CHOICES = (
        (1, "Active"),
        (2, "Inactive"),
        (3, "Restricted")
        (4, "Banned")
    )

    status = models.IntegerField('status', choices=STATUS_CHOICES, default=2)
    user = models.ForeignKey(User, relatedName = "base_user")
    # socialuser = models.ForeignKey(SocialUser, relatedName = "social_user")

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
