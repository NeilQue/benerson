from django.shortcuts import render
from django.http import HttpResponse
from .forms import CreateNewList

# Create your views here.
def index(response, id):
    return render(response, "sampleapp/anothaone.html", {'id':id})

def home(response):
    return render(response, "sampleapp/home.html", {})
    
def create(response):
    if response.method == "POST":
        form = CreateNewList(response.POST)
        
        if form.is_valid():
            pass
    else:
        form = CreateNewList()
    
    return render(response, "sampleapp/create.html", {'form':form})