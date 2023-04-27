from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.template import loader
from django.http import JsonResponse

import json
import os

print(os.getcwd())

data_mem = open('./polls/static/polls/ResultFiles/DataForwarding/data_out_Data_mem.json') 
data_out = open('./polls/static/polls/ResultFiles/DataForwarding/data_out_printing.json') 
register = open('./polls/static/polls/ResultFiles/DataForwarding/data_out_register.json') 
stats = open('./polls/static/polls/ResultFiles/DataForwarding/data_out_Stats.json') 
btb = open('./polls/static/polls/ResultFiles/DataForwarding/data_out_btb.json')

stats2 = open('./polls/static/polls/stats/stats.json')
D_data = open('./polls/static/polls/stats/JSONArr.json')
I_data = open('./polls/static/polls/Istats/JSONArr.json')

D_victims = open('./polls/static/polls/stats/VictimBlocks.json')
I_victims = open('./polls/static/polls/Istats/VictimBlocks.json')

data_mem_data = json.load(data_mem)
data_out_data = json.load(data_out)
register_data = json.load(register)
stats_data = json.load(stats)
btb_data = json.load(btb)

stats2_data = json.load(stats2)
D_data_data = json.load(D_data)
I_data_data = json.load(I_data)

D_victims_data = json.load(D_victims)
I_victims_data = json.load(I_victims)

cycle = 0
print(len(data_mem_data), len(data_out_data), len(register_data), len(stats_data), len(btb_data))
last_cycle = len(data_mem_data) - 1
# print(data1)
# data2 = json.dumps(data1) # json formatted string
data_mem.close()
data_out.close()
register.close()
stats.close()
btb.close()

stats2.close()
D_data.close()
I_data.close()

D_victims.close()
I_victims.close()

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
    Merge(stats_data[0], stats2_data)
    stats_response = [stats2_data]

    D_response = D_data_data[cycle]
    I_response = I_data_data[cycle]

    D_victims_response = D_victims_data[cycle]
    I_victims_response = I_victims_data[cycle]
    
    return JsonResponse({'cycle':cycle, 'data_mem': data_mem_response, 'data_out': data_out_response, 'register': register_response, 'stats': stats_response, 'btb': btb_response, 'D_data': D_response, 'I_data': I_response, 'D_victims': D_victims_response, 'I_victims': I_victims_response})

def load_next(request):
    global cycle
    if(cycle == last_cycle):
        data_mem_response = data_mem_data[cycle]
        data_out_response = data_out_data[cycle]
        register_response = register_data[cycle]
        btb_response = btb_data[cycle]
        Merge(stats_data[0], stats2_data)
        stats_response = [stats2_data]
        D_response = D_data_data[cycle]
        I_response = I_data_data[cycle]
        
        D_victims_response = D_victims_data[cycle]
        I_victims_response = I_victims_data[cycle]
        
        return JsonResponse({'cycle':cycle, 'data_mem': data_mem_response, 'data_out': data_out_response, 'register': register_response, 'stats': stats_response, 'btb': btb_response, 'D_data': D_response, 'I_data': I_response, 'D_victims': D_victims_response, 'I_victims': I_victims_response})
        
    cycle += 1
    data_mem_response = data_mem_data[cycle]
    data_out_response = data_out_data[cycle]
    register_response = register_data[cycle]
    btb_response = btb_data[cycle]
    Merge(stats_data[0], stats2_data)
    stats_response = [stats2_data]
    
    D_response = D_data_data[cycle]
    I_response = I_data_data[cycle]
    
    D_victims_response = D_victims_data[cycle]
    I_victims_response = I_victims_data[cycle]
    
    return JsonResponse({'cycle':cycle, 'data_mem': data_mem_response, 'data_out': data_out_response, 'register': register_response, 'stats': stats_response, 'btb': btb_response, 'D_data': D_response, 'I_data': I_response, 'D_victims': D_victims_response, 'I_victims': I_victims_response})

def load_run(request):
    global cycle
    cycle = last_cycle
        
    data_mem_response = data_mem_data[cycle]
    data_out_response = data_out_data[cycle]
    register_response = register_data[cycle]
    btb_response = btb_data[cycle]
    Merge(stats_data[0], stats2_data)
    stats_response = [stats2_data]
    
    D_response = D_data_data[cycle]
    I_response = I_data_data[cycle]
    
    D_victims_response = D_victims_data[cycle]
    I_victims_response = I_victims_data[cycle]
    
    return JsonResponse({'cycle':cycle, 'data_mem': data_mem_response, 'data_out': data_out_response, 'register': register_response, 'stats': stats_response, 'btb': btb_response, 'D_data': D_response, 'I_data': I_response, 'D_victims': D_victims_response, 'I_victims': I_victims_response})
    # return JsonResponse({'run': 'fuck you bitch'})

def load_reset(request):
    global cycle
    
    cycle = 0    
    
    data_mem_response = data_mem_data[cycle]
    data_out_response = data_out_data[cycle]
    register_response = register_data[cycle]
    btb_response = btb_data[cycle]
    Merge(stats_data[0], stats2_data)
    stats_response = [stats2_data]

    
    D_response = D_data_data[cycle]
    I_response = I_data_data[cycle]
    
    D_victims_response = D_victims_data[cycle]
    I_victims_response = I_victims_data[cycle]
    
    return JsonResponse({'cycle':cycle, 'data_mem': data_mem_response, 'data_out': data_out_response, 'register': register_response, 'stats': stats_response, 'btb': btb_response, 'D_data': D_response, 'I_data': I_response, 'D_victims': D_victims_response, 'I_victims': I_victims_response})

def Merge(dict1, dict2):
    return(dict2.update(dict1))