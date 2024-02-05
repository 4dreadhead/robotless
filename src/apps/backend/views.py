from django.shortcuts import render


def analyze(request):
    return render(request, "analyze.html")


def share(request):
    return render(request, "share.html")
