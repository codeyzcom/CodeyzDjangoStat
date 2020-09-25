from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required

from cdzstat import settings as native_settings

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


@staff_member_required
def sessions_board(request):
    ctx = {'is_popup': False, 'is_nav_sidebar_enabled': True}

    return render(request, 'cdzstat/sessions_board.html', ctx)


@staff_member_required
def settings_board(request):
    ctx = {'is_popup': False, 'is_nav_sidebar_enabled': True}

    native = set([item for item in dir(native_settings) if item.startswith('CDZSTAT_')])
    django = set([item for item in dir(settings) if item.startswith('CDZSTAT_')])

    native.difference_update(django)

    native_data = {}
    django_data = {}

    for item in native:
        native_data[item] = native_settings.__dict__.get(item)

    for item in django:
        django_data[item] = settings.__dict__.get(item)


    ctx['settings_native'] = native_data
    ctx['settings_django'] = django_data

    return render(request, 'cdzstat/settigns_board.html', ctx)
