from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required

@csrf_exempt
def dummy_view(request):
    '''
    Dummy view
    '''
    return HttpResponse(status=204)


@staff_member_required
def dashboard(request):
    ctx = {'is_popup': False, 'is_nav_sidebar_enabled': True}

    return render(request, 'cdzstat/dashboard.html', context=ctx)


@staff_member_required
def exceptions(request):
    ctx = {'is_popup': False, 'is_nav_sidebar_enabled': True}

    return render(request, 'cdzstat/exceptions.html', context=ctx)
