from django.template import RequestContext

def debug_mode(request):
    from django.conf import settings
    return {
        'debug_mode': settings.DEBUG,
        'media': settings.MEDIA_URL
    }