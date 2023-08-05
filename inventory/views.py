from django.shortcuts import render
from .models import Receipt, Item
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.db.models.functions import Lower
from django.contrib.auth.decorators import login_required

## SUGGESTIONS ##
# add add receipt in sidenav to make it starting point

@login_required
def home(response):
    all_items = Item.objects.order_by(Lower('brand'), Lower('model'))
    context = {}

    laptops = all_items.filter(type__iexact="laptop")
    total_laptops = 0

    for item in laptops:
        total_laptops += item.benerson_qty + item.qlinx_qty

    context["total_laptops"] = total_laptops
    
    if response.method == "POST":
        if response.POST.get("editItem"):
            for item in all_items:
                if response.POST.get("c" + str(item.id)) == "clicked":
                    return HttpResponseRedirect('/i%i' %item.id)
            
        elif response.POST.get("delItem"):
            for item in all_items:
                if response.POST.get("c" + str(item.id)) == "clicked":
                    item.delete()
                    
            return HttpResponseRedirect("/")
                    
        elif response.POST.get("searchItem"):
            search = [word for word in response.POST.get("item_searched").split()]
            
            results = Item.objects.all()
            
            for word in search:
                results = results.filter(
                    Q(brand__contains=word) |
                    Q(type__contains=word) |
                    Q(model__contains=word) |
                    Q(specs__contains=word)
                )

            context["item_set"] = results
                
            return render(response, 'inventory/home.html', context)
                    
    context["item_set"] = all_items

    return render(response, 'inventory/home.html', context)
   
def addItem(response):
    if response.method == "POST":
        if response.POST.get("newItem"):
            new = Item(type="null", model="null", brand="null", specs="null", costPrice="null", srp="null", benerson_qty=0, qlinx_qty=0)
            new.save()
        
            new.type = response.POST.get("type")
            new.model = response.POST.get("model")
            new.brand = response.POST.get("brand")
            new.specs = response.POST.get("description")
            new.costPrice = response.POST.get("costPrice")
            new.srp = response.POST.get("srp")
            new.benerson_qty = response.POST.get("bQty")
            new.qlinx_qty = response.POST.get("qQty")
            
            new.save()
            
            # pop-up showing that item is saved

    return render(response, 'inventory/additem.html', {})
    
#logs
def searchReceipt(response):
    all_receipts = Receipt.objects.order_by('date').reverse()
    
    if response.method == "POST":
        if response.POST.get("search_receipt"):
            search = response.POST.get("receipt_searched")
            
            results = Receipt.objects.filter(number=search)
            
            return render(response, 'inventory/searchreceipt.html', {"receipt_set": results})
    
    return render(response, 'inventory/searchreceipt.html', {"receipt_set": all_receipts})
    
def addReceipt(response, id):
    if response.method == "POST":
        if response.POST.get("newReceipt"): 
            new = Receipt(number='null',date='1970-01-01',type='null',store='null', quantities='null')
            new.save()
            
            new.number = response.POST.get("number")
            new.type = response.POST.get("type")
            new.date = response.POST.get("date")
            new.store = response.POST.get("store")
            
            new.save()
            
            return HttpResponseRedirect(f"/r{new.id}")
        
    return render(response, 'inventory/addreceipt.html', {})
   
#edit item
def showItem(response, id):
    current_item = Item.objects.get(id=id)
    
    if response.method == "POST":
        if response.POST.get("editItem"):
            current_item.type = response.POST.get("type")
            current_item.model = response.POST.get("model")
            current_item.brand = response.POST.get("brand")
            current_item.specs = response.POST.get("description")
            current_item.costPrice = response.POST.get("costPrice")
            current_item.srp = response.POST.get("srp")
            current_item.benerson_qty = response.POST.get("bQty")
            current_item.qlinx_qty = response.POST.get("qQty")
            
            current_item.save()
            
            # pop-up showing that item is edited
    
    return render(response, 'inventory/edititem.html', {"item":current_item})

#edit receipt
def showReceipt(response, id):
    current_receipt = Receipt.objects.get(id=id)
    quantities_list = current_receipt.quantities.split('.')
    items_list = list(current_receipt.item_set.all())
    temp_string = ""
    
    if response.method == "POST":
        if response.POST.get("addItem"):
            item_name = response.POST.get("newItem")
            item_quantity = response.POST.get("quantity")
            
            item_brand, item_model, item_specs = item_name.split()
            try:
                item = Item.objects.get(brand=item_brand, model=item_model, specs=item_specs)
            
                item.receipts.add(current_receipt)
                current_receipt.quantities = '.'.join(quantities_list + [item_quantity])
                current_receipt.save()
                
                if current_receipt.type == "Supplier Invoice":
                    item.benerson_qty = item.benerson_qty + item_quantity
                    
                else:
                    if current_receipt.store == "Qlinx":
                        item.qlinx_qty = item.qlinx_qty - item_quantity
                        
                        if current_receipt.type == "Transfer Slip":
                            item.benerson_qty = item.benerson_qty + item_quantity
                        
                    if current_receipt.store == "Benerson":
                        item.benerson_qty = item.benerson_qty - item_quantity
                        
                        if current_receipt.type == "Transfer Slip":
                            item.qlinx_qty = item.qlinx_qty + item_quantity
                            
                item.save()
            except ObjectDoesNotExist:
                #TODO
                return HttpResponseRedirect('/additem', )
                
            except MultipleObjectsReturned:
                pass
        
        elif response.POST.get("save"):
            for item, quantity in zip(items_list, quantities_list):
                new_quantity = int(response.POST.get(f"{item.id}qty"))
                
                if current_receipt.type == "Supplier Invoice":
                    item.benerson_qty = item.benerson_qty - quantity + new_quantity
                    
                else:
                    if current_receipt.store == "Qlinx":
                        item.qlinx_qty = item.qlinx_qty + quantity - new_quantity
                        
                        if current_receipt.type == "Transfer Slip":
                            item.benerson_qty = item.benerson_qty - quantity + new_quantity
                        
                    if current_receipt.store == "Benerson":
                        item.benerson_qty = item.benerson_qty + quantity - new_quantity
                        
                        if current_receipt.type == "Transfer Slip":
                            item.qlinx_qty = item.qlinx_qty - quantity + new_quantity
                            
                item.save()
                
                temp_string += f"{new_quantity}."
                
            current_receipt.quantities = temp_string
            current_receipt.save()
    
    return render(response, 'inventory/editreceipt.html', 
        {"zipped_list": zip(list(current_receipt.item_set.all()), current_receipt.quantities.split('.')),
        "item_set": Item.objects.all()})