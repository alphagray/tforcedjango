from django.db.models import Q
from django.db.models.query import QuerySet


class EpisodeManager(QuerySet):
    """ Returns public episodes that are currently activated."""

    def itunespublished(self):
        return self.get_queryset().exclude(Q(published=None) | Q(block=True))

    def published(self):
        return self.exclude(published=None)

    def current(self):
        try:
            return self.published().order_by("-published")[0]
        except IndexError:
            return None

    def onchannel(self, channel):
        self.filter(show__channel=channel)




    pass

class ShowManager(QuerySet):
    """Returns shows that are on the current channel."""

    def published(self):
        return self.exclude(published=None)

    def onchannel(self, channel):
        self.filter(show__channel=channel)

    pass

class ContentManager(QuerySet):
    """ returns all content for a channel, regardless of its model type 
    by serializing the data a common object. Uses a few fields for managing
    internal concepts """ 
    pass