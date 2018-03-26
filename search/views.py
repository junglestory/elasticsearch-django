from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse

def search(request):
    msg = 'My Message'
    return render(request, 'search.html', {'message': msg})