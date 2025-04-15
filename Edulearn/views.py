from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages


def home_view(request):
    return render(request, 'home/index.html')
def home_view(request):
    return render(request, 'home/description.html')
