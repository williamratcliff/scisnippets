from django import forms
from django.contrib import admin

from haystack.forms import SearchForm

from cab.models import Language, Snippet, DJANGO_VERSIONS


class SnippetForm(forms.ModelForm):
    class Meta:
        model = Snippet
        exclude = ('author', 'bookmark_count', 'rating_score',)


class AdvancedSearchForm(SearchForm):
    language = forms.ModelChoiceField(queryset=Language.objects.all(), required=False)
    django_version = forms.MultipleChoiceField(choices=DJANGO_VERSIONS, required=False)
    minimum_pub_date = forms.DateTimeField(widget=admin.widgets.AdminDateWidget,
        required=False)
    minimum_bookmark_count = forms.IntegerField(required=False)
    minimum_rating_score = forms.IntegerField(required=False)

    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(AdvancedSearchForm, self).search()
        
        if self.cleaned_data['language']:
            sqs = sqs.filter(language=self.cleaned_data['language'].name)
        
        if self.cleaned_data['django_version']:
            sqs = sqs.filter(django_version__in=self.cleaned_data['django_version'])
        
        if self.cleaned_data['minimum_pub_date']:
            sqs = sqs.filter(pub_date__gte=self.cleaned_data['minimum_pub_date'])
        
        if self.cleaned_data['minimum_bookmark_count']:
            sqs = sqs.filter(bookmark_count__gte=self.cleaned_data['minimum_bookmark_count'])
        
        if self.cleaned_data['minimum_rating_score']:
            sqs = sqs.filter(rating_score__gte=self.cleaned_data['minimum_rating_score'])

        return sqs

