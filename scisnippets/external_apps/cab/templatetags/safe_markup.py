from django import template
from django.conf import settings

register = template.Library()

@register.filter
def safe_markdown(value, arg=''):
    """
    Runs Markdown over a given value, optionally using various
    extensions python-markdown supports.
    
    Syntax::
    
        {{ value|markdown:"extension1_name,extension2_name..." }}
    
    To enable safe mode, which strips raw HTML and only returns HTML
    generated by actual Markdown syntax, pass "safe" as the first
    extension in the list.
    
    If the version of Markdown in use does not support extensions,
    they will be silently ignored.
    
    """
    try:
        import markdown
    except ImportError:
        if settings.DEBUG:
            raise template.TemplateSyntaxError('Error in markdown filter: Markdown could not be imported.')
        else:
            # Try to salvage this; whatever we do, we shouldn't
            # return potentially unsafe HTML.
            from django.utils.html import escape, linebreaks
            return linebreaks(escape(value))
    else:
        extensions=arg.split(",")
        if len(extensions) > 0 and extensions[0] == "safe":
            extensions = extensions[1:]
            safe_mode = True
        else:
            safe_mode = False
        return markdown.markdown(value, extensions, safe_mode=safe_mode)
