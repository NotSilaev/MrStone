from django.conf import settings
from django.http import HttpResponse, JsonResponse

import logs
from utils import getClientIP, getCurrentDateTime
from cache import Cache

import json
import traceback


class ExceptionMiddleware:
    """Intercepts all project exceptions and logs them in the log file."""

    def __init__(self, next):
        self.next = next

    def __call__(self, request):
        response = self.next(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs) -> None:
        try:
            self.view = str(view_func.view_class)
        except AttributeError:
            self.view = view_func.__name__
        self.view_module = view_func.__module__
        self.view_args = view_args
        self.view_kwargs = view_kwargs

    def process_exception(self, request, exception) -> JsonResponse:
        logs.addLog(
            level='error', 
            text=traceback.format_exc(), 
            details=(
                f"Called view: {self.view}\n"
                + f"View module: {self.view_module}\n"
                + f"View args: {self.view_args}\n"
                + f"View kwargs: {self.view_kwargs}"
            ),
            send_telegram_message=True
        )

        if settings.DEBUG:
            error_detail = str(exception)
        else:
            error_detail = None

        response = {
            'errors': [{
                'status': 500,
                'title': 'Unexpected error',
                'detail': error_detail,
                'source': {
                    'endpoint': self.view
                }
            }]
        }
        return JsonResponse(response, status=500)
