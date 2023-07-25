from django.shortcuts import render, redirect

def index(request):
    return render(request, 'index.html')

def render_react_app(request):
    return render(request,'index.html')