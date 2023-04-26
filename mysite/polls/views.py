from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import loader
from django.http import JsonResponse

import json
import os

print(os.getcwd())

data_mem = open('./polls/static/polls/ResultFiles/data_out_Data_mem.json') 
data_out = open('./polls/static/polls/ResultFiles/data_out_printing.json') 
register = open('./polls/static/polls/ResultFiles/data_out_register.json') 
stats = open('./polls/static/polls/ResultFiles/data_out_Stats.json') 
btb = open('./polls/static/polls/ResultFiles/data_out_btb.json')

data_mem_data = json.load(data_mem)
data_out_data = json.load(data_out)
register_data = json.load(register)
stats_data = json.load(stats)
btb_data = json.load(btb)

cycle = 0
# print(len(data_mem_data), len(data_out_data), len(register_data), len(stats_data), len(btb_data))
last_cycle = len(data_mem_data) - 1
# print(data1)
# data2 = json.dumps(data1) # json formatted string
data_mem.close()
data_out.close()
register.close()
stats.close()
btb.close()

def index(request):
    template = loader.get_template("polls/index.html")
    context = {}
    return HttpResponse(template.render(context, request))
    return HttpResponse("<h1>Hello, world. You're at the polls index.</h1>")

def load_prev(request):  
    # print("yooooooooo", request)
    global cycle
    if(cycle == 0):
        return JsonResponse({'error':'error'})
        
    cycle -= 1
    data_mem_response = data_mem_data[cycle]
    data_out_response = data_out_data[cycle]
    register_response = register_data[cycle]
    btb_response = btb_data[cycle]
    stats_response = stats_data
    
    return JsonResponse({'cycle':cycle, 'data_mem': data_mem_response, 'data_out': data_out_response, 'register': register_response, 'stats': stats_response, 'btb': btb_response})

def load_next(request):
    global cycle
    if(cycle == last_cycle):
        return JsonResponse({'error':'error'})
        
    cycle += 1
    data_mem_response = data_mem_data[cycle]
    data_out_response = data_out_data[cycle]
    register_response = register_data[cycle]
    btb_response = btb_data[cycle]
    stats_response = stats_data
    
    return JsonResponse({'cycle':cycle, 'data_mem': data_mem_response, 'data_out': data_out_response, 'register': register_response, 'stats': stats_response, 'btb': btb_response})

def load_run(request):
    global cycle
    cycle = last_cycle
        
    data_mem_response = data_mem_data[cycle]
    data_out_response = data_out_data[cycle]
    register_response = register_data[cycle]
    btb_response = btb_data[cycle]
    stats_response = stats_data
    
    return JsonResponse({'cycle':cycle, 'data_mem': data_mem_response, 'data_out': data_out_response, 'register': register_response, 'stats': stats_response, 'btb': btb_response})
    # return JsonResponse({'run': 'fuck you bitch'})

def load_reset(request):
    global cycle
    
    cycle = 0    
    
    data_mem_response = data_mem_data[cycle]
    data_out_response = data_out_data[cycle]
    register_response = register_data[cycle]
    btb_response = btb_data[cycle]
    stats_response = stats_data
    
    return JsonResponse({'cycle':cycle, 'data_mem': data_mem_response, 'data_out': data_out_response, 'register': register_response, 'stats': stats_response, 'btb': btb_response})