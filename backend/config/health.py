from django.http import JsonResponse


def healthz(_request):
    """Confirma que el proceso web está disponible sin consultar la base."""
    return JsonResponse({'status': 'ok'})
