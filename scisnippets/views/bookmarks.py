"""
Views which deal with Bookmarks, allowing them to be added, removed,
and viewed according to various criteria.

"""

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.generic import list_detail
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from ..models import Bookmark, Language, Snippet, Tag

base_generic_dict = {
    'allow_empty': True,
    'paginate_by': 20,
    }

def add_bookmark(request, snippet_id):
    """
    Bookmarks a Snippet for a User.
    
    Context::
    None, returns a redirect to the Snippet.
    
    Template::
    None, returns a redirect to the Snippet.
    
    """
    snippet = get_object_or_404(Snippet, pk=snippet_id)
    try:
        Bookmark.objects.get(user__pk=request.user.id,
                             snippet__pk=snippet.id)
    except Bookmark.DoesNotExist:
        bookmark = Bookmark.objects.create(user=request.user,
                                           snippet=snippet)
    return HttpResponseRedirect(snippet.get_absolute_url())
add_bookmark = login_required(add_bookmark)

def bookmarks(request):
    """
    List of a User's bookmarks.
    
    Context::
    Same as the generic ``list_detail.object_list`` view.
    
    Template::
        cab/user_bookmarks.html
    
    """
    return list_detail.object_list(request,
                                   queryset=Bookmark.objects.get_for_user(request.user.username).select_related(),
                                   template_name='cab/user_bookmarks.html',
                                   **base_generic_dict)
bookmarks = login_required(bookmarks)

def bookmark_author_list(request):
    """
    Lists the authors of a User's Bookmarks.
    
    Context::
    Same as the ``list_detail.object_list`` generic view.
    
    Template::
        cab/bookmark_author_list.html
    
    """
    return list_detail.object_list(request,
                                   queryset=Bookmark.objects.distinct_list('author',
                                                                           request.user.username).select_related(),
                                   template_name='cab/bookmarks_author_list.html',
                                   **base_generic_dict)
bookmark_author_list = login_required(bookmark_author_list)

def bookmarks_by_author(request, author_username):
    """
    List of a User's bookmarks written by a particular author.
    
    Context::
    Same as the generic ``list_detail.object_list`` view, with one
    extra variable:
    
        object
            The author
    
    Template::
        cab/bookmarks_by_author.html
    
    """
    author = get_object_or_404(User, username__exact=author_username)
    return list_detail.object_list(request,
                                   queryset=Bookmark.objects.get_by_author(request.user.username,
                                                                           author_slug).select_related(),
                                   extra_context={ 'object': author },
                                   template_name='cab/bookmarks_by_author.html',
                                   **base_generic_dict)
bookmarks_by_author = login_required(bookmarks_by_author)

def bookmarks_by_language(request, language_slug):
    """
    List of a User's bookmarks which are written in a
    particular language.
    
    Context::
    Same as the generic ``list_detail.object_list`` view, with
    one extra variable:
    
        object
            The Language
    
    Template::
        cab/bookmarks_by_language.html
    
    """
    language = get_object_or_404(Language, slug__exact=language_slug)
    return list_detail.object_list(request,
                                   queryset=Bookmark.objects.get_by_language(request.user.username,
                                                                             language_slug).select_related(),
                                   extra_context={ 'object': language},
                                   template_name='cab/bookmarks_by_language.html',
                                   **base_generic_dict)
bookmarks_by_language = login_required(bookmarks_by_language)

def bookmarks_by_tag(request, tag_slug):
    """
    List of a User's bookmarks which have a particular tag.
    
    Context::
    Same as the generic ``list_detail.object_list`` view, with
    one extra variable:
    
        object
            The Tag
    
    Template::
        snipppets/bookmarks_by_tag.html
    
    """
    tag = get_object_or_404(Tag, slug__exact=tag_slug)
    return list_detail.object_list(request,
                                   queryset=Bookmark.objects.get_by_tag(request.user.username,
                                                                   tag_slug).select_related(),
                                   extra_context={ 'object': tag },
                                   template_name='cab/bookmarks_by_tag.html',
                                   **base_generic_dict)
bookmarks_by_tag = login_required(bookmarks_by_tag)

def bookmark_language_list(request):
    """
    Lists the Languages a User's Bookmarks are written in.
    
    Context::
    Same as the ``list_detail.object_list`` generic view.
    
    Template::
        cab/bookmark_language_list.html
    
    """
    return list_detail.object_list(request,
                                   queryset=Bookmark.objects.distinct_list('language',
                                                                           request.user.username).select_related(),
                                   template_name='cab/bookmarks_language_list.html',
                                   **base_generic_dict)
bookmark_language_list = login_required(bookmark_language_list)

def bookmark_tag_list(request):
    """
    Lists the Tags attached to a User's Bookmarks.
    
    Context::
    Same as the ``list_detail.object_list`` generic view.
    
    Template::
        cab/bookmark_tag_list.html
    
    """
    return list_detail.object_list(request,
                                   queryset=Bookmark.objects.distinct_list('tag',
                                                                           request.user.username).select_related(),
                                   template_name='cab/bookmarks_tag_list.html',
                                   **base_generic_dict)
bookmark_tag_list = login_required(bookmark_tag_list)    

def delete_bookmark(request, bookmark_id):
    """
    Removes a User's bookmarked Snippet.
    
    Context::
    None, returns a redirect to the HTTP referer.
    
    Template::
    None, returns a redirect to the HTTP referer.
    
    """
    bookmark = get_object_or_404(Bookmark, user__pk=request.user.id,
                                 pk=bookmark_id)
    bookmark.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
delete_bookmark = login_required(delete_bookmark)
