from django.http import HttpResponse


def nodes(request):
    return HttpResponse('{"europe": ["127.0.0.1"]}')
