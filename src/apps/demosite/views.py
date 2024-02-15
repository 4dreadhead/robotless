from django.shortcuts import render
from http import HTTPStatus


def analyze(request):
    return render(request, "analyze.html")


def share(request):
    return render(request, "share.html")


def error_handler(request, status=400):
    context = {
        "status_code": status,
        "reason_phrase": HTTPStatus(status).phrase
    }
    return render(request, '400_599.html', context=context, status=status)
