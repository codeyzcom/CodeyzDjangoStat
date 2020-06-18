from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin

from cdzstat.services import HeightLevelService


@csrf_exempt
def collector(request):
    if request.method == 'POST':
        stat_srv = HeightLevelService(request)
        stat_srv.process()
    return HttpResponse(status=204)


class AdminSuperuserMixin(UserPassesTestMixin, View):

    def test_func(self):
        return self.request.user.is_superuser and self.request.user.is_staff


class IndexAdminPage(TemplateView, AdminSuperuserMixin):
    template_name = 'admin/base_cdzstat_admin.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        return ctx
