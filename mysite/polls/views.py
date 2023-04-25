from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import loader
from django.http import JsonResponse

def index(request):
    template = loader.get_template("polls/index.html")
    context = {}
    return HttpResponse(template.render(context, request))
    return HttpResponse("<h1>Hello, world. You're at the polls index.</h1>")

def load_more(request):  
    print("yooooooooo", request)
    return JsonResponse({'data': 'fuck you bitch'})