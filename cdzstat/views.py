from django.http import HttpResponse

from cdzstat.services import HeightLevelService


def collector(request):
    hls = HeightLevelService(request)
    hls.process()
    return HttpResponse(status=204)
