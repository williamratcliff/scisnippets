from haystack.indexes import *
from haystack import site
from cab.models import Snippet

class SnippetIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    author = CharField()
    title = CharField(model_attr='title')
    tags = CharField()
    tag_list = MultiValueField()
    language = CharField()
    pub_date = DateTimeField(model_attr='pub_date')
    django_version = FloatField(model_attr='django_version')
    bookmark_count = IntegerField(model_attr='bookmark_count')
    rating_score = IntegerField(model_attr='rating_score')
    url = CharField(indexed=False)

    def prepare_author(self, obj):
        return obj.author.username

    def prepare_language(self, obj):
        return obj.language.name

    def prepare_tags(self, obj):
        return ' '.join([tag.name for tag in obj.tags.all()])

    def prepare_tag_list(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def prepare_url(self, obj):
        return obj.get_absolute_url()

    def get_updated_field(self):
        return 'updated_date'

site.register(Snippet, SnippetIndex)
