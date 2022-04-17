from django.shortcuts import render


def page_not_found(request, exception):
    template = 'core/404.html'
    context = {'path': request.path}
    return render(request=request, template_name=template, context=context,
                  status=404)


def permission_denied(request, exception):
    return render(request, 'core/403.html', status=403)


def server_error(request):
    return render(request, 'core/500.html', status=500)


def csrf_failure(request):
    return render(request, 'core/403csrf.html')
