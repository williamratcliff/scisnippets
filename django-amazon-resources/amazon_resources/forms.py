import re

from django import forms

from amazon_resources.libs.amazon import asin_from_url

class ResourceForm(forms.Form):
    url = forms.CharField(max_length=255, help_text='URL of Amazon product')
    
    def clean_url(self):
        url = self.cleaned_data.get('url')
        if asin_from_url(url):
            return url
        else:
            raise forms.ValidationError('Could not determine ASIN from url')
