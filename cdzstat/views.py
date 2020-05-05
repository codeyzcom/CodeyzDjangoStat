from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from cdzstat.services import (
    HeightLevelService,
    StatisticalService,
)


@csrf_exempt
def collector(request):
    if request.method == 'GET':
        hls = HeightLevelService(request)
        hls.process()
    if request.method == 'POST':
        stat_srv = HeightLevelService(request)
        stat_srv.process()
    return HttpResponse(status=204)
