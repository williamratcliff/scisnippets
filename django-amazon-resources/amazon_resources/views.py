from django.conf import settings
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list

from amazon_resources.models import Resource, ResourceCategory

def category_list(request, template_name='amazon_resources/category_list.html'):
    return object_list(
        request=request,
        queryset=ResourceCategory.objects.all(),
        template_name=template_name)
    

def resource_list(request, category_slug=None,
        template_name='amazon_resources/resource_list.html'):
    qs = Resource.objects.all()
    extra_context = {}
    if category_slug:
        category = get_object_or_404(ResourceCategory, slug=category_slug)
        qs = qs.filter(category=category)
        extra_context['category'] = category
    return object_list(
        request=request,
        queryset=qs,
        template_name=template_name,
        page=int(request.GET.get('page', 0)),
        paginate_by=20,
        extra_context=extra_context,)
