from django.db import models

# Create your models here.

class Post(models.Model):

    STATUS_CHOICES = (
        (1, _('Draft')),
        (2, _('Publics')),
    )

    title = models.CharField(max_length=150)
    body = models.TextField()
    status = models.IntegerField(_('status'), choices=STATUS_CHOICES, 
                                 default=2)

class ExtendedPost(models.Model, Post):
    pass

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
