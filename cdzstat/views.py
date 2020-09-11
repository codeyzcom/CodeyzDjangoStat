from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def dummy_view(request):
    '''
    Dummy view
    '''
    return HttpResponse(status=204)
