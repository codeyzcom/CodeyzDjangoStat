from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from cdzstat.services import CollectorService


@csrf_exempt
def collector(request):
    if request.method == 'POST':
        collector_service = CollectorService(request)
        collector_service.height_level_collector()
        collector_service.process()
    return HttpResponse(status=204)
