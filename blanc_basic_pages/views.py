from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.template import loader, RequestContext
from django.views.decorators.csrf import csrf_protect
from .models import Page
from . import get_page_model


DEFAULT_TEMPLATE = 'pages/default.html'


def page(request, url):
    if not url.startswith('/'):
        url = '/' + url
    
    try:
        page_cls = get_page_model()
        obj = get_object_or_404(page_cls, url=url, published=True)
    except Http404:
        if not url.endswith('/') and settings.APPEND_SLASH:
            url += '/'
            obj = get_object_or_404(page_cls, url=url, published=True)
            return HttpResponsePermanentRedirect('%s/' % request.path)
        else:
            raise
    return render_page(request, obj)


@csrf_protect
def render_page(request, obj):
    # If registration is required for accessing this page, and the user isn't
    # logged in, redirect to the login page.
    if obj.login_required and not request.user.is_authenticated():
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.path)

    # We intentionally want an exception if the template is unavailable.
    # Go update your database if you remove a template!
    t = loader.get_template(obj.template_name or DEFAULT_TEMPLATE)

    c = RequestContext(request, {
        'page': obj,
    })
    response = HttpResponse(t.render(c))
    return response
    
def lazy_page(request):
    return page(request, request.path_info)
