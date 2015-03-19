from django.db.models import Q
from django.db.models.query import QuerySet
from django.db.models.fields.related import SingleRelatedObjectDescriptor

class _DerivedNamesMixin(object):
    def _get_derived_names(self):
        return [k for k, v in self.model.__dict__.iteritems()
                if isinstance(v, SingleRelatedObjectDescriptor)
                and issubclass(v.related.model, self.model)]

class DerivedQuerySet(_DerivedNamesMixin, QuerySet):
    def iterator(self):
        prefetched = super(DerivedQuerySet, self).select_related(
            *self._get_derived_names())
        for obj in super(DerivedQuerySet, prefetched).iterator():
            yield self._get_derived(obj)

    def _get_derived(self, instance):
        from django.core.exceptions import ObjectDoesNotExist
        for derived_name in self._get_derived_names():
            try:
                return getattr(instance, derived_name)
            except ObjectDoesNotExist:
                pass
        return instance

class ContentManager(DerivedQuerySet):
    """ returns all content for a channel, regardless of its model type 
    by serializing the data a common object. Uses a few fields for managing
    internal concepts """ 
    
    def get_query_set(self, *args, **kwargs):
        return DerivedQuerySet(self.model, using=self._db).select_related(*self._get_derived_names())


    def onchannel(self, channel):
        self.filter(channel__contains=channel)
    
    def published(self):
        return self.exclude(published=None)

    pass

class EpisodeManager(ContentManager):
    """ Returns public episodes that are currently activated."""

    def itunespublished(self):
        return self.get_queryset().exclude(Q(published=None) | Q(block=True))

    def onchannel(self, channel):
        return self.get_queryset().filter(Q(shows__channel_set__contains=channel)|Q(channel_set__contains=channel))


    def current(self):
        try:
            return self.published().order_by("-published")[0]
        except IndexError:
            return None

    pass

class ShowManager(ContentManager):
    """Returns shows that are on the current channel."""
    
    pass