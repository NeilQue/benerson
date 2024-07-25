from django.shortcuts import render
from .models import Receipt, Item, ItemInReceipt
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.db.models.functions import Lower
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

## SUGGESTIONS ##
# add add receipt in sidenav to make it starting point

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
                    
            return HttpResponseRedirect("/inventory")
                    
        elif response.POST.get("searchItem"):
            search = [word for word in response.POST.get("item_searched").split()]
            
            for word in search:
                all_items = all_items.filter(
                    Q(brand__contains=word) |
                    Q(type__contains=word) |
                    Q(model__contains=word) |
                    Q(specs__contains=word)
                )
                    
    context["item_set"] = all_items

    return render(response, 'inventory/home.html', context)
   
def addItem(response, action="/additem/"):
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
            if action == "/additem/":
                new.benerson_qty = response.POST.get("bQty")
                new.qlinx_qty = response.POST.get("qQty")
            
            new.save()
            
            # pop-up showing that item is saved

    return render(response, 'inventory/additem.html', {"action": action})
    
#logs
def searchReceipt(response):
    all_receipts = Receipt.objects.order_by('date').reverse()
    
    if response.method == "POST":
        if response.POST.get("search_receipt"):
            search = response.POST.get("receipt_searched")
            
            results = Receipt.objects.filter(number=search)
            
            return render(response, 'inventory/searchreceipt.html', {"receipt_set": results})
    
    return render(response, 'inventory/searchreceipt.html', {"receipt_set": all_receipts})

@login_required    
def addReceipt(response):
    if response.method == "POST":
        if response.POST.get("newReceipt"): 
            new = Receipt(number='null',date='1970-01-01',type='null',store='null')
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
    items_in_receipt = ItemInReceipt.objects.filter(receipt=current_receipt)

    if response.method == "POST":
        if response.POST.get("addItem"):
            item_brand = response.POST.get("brand")
            item_model = response.POST.get("model")
            item_specs = response.POST.get("specs")
            item_quantity = response.POST.get("quantity")
            item_price = response.POST.get("price")

            try:
                item = Item.objects.get(brand=item_brand, model=item_model, specs=item_specs)

                receipt_item = ItemInReceipt(item=item, receipt=current_receipt, quantity=item_quantity, price=item_price)
                receipt_item.save()
            except ObjectDoesNotExist:
                return addItem(response, f"/r{current_receipt.id}/")

        elif response.POST.get("save"):
            for entry in items_in_receipt:
                new_quantity = int(response.POST.get(f"{entry.id}qty"))

                # update item model's quantity
                if current_receipt.type == "Supplier Invoice":
                    item.benerson_qty = item.benerson_qty - entry.quantity + new_quantity
                    
                else:
                    if current_receipt.store == "Qlinx":
                        item.qlinx_qty = item.qlinx_qty + entry.quantity - new_quantity
                        
                        if current_receipt.type == "Transfer Slip":
                            item.benerson_qty = item.benerson_qty - entry.quantity + new_quantity
                        
                    if current_receipt.store == "Benerson":
                        item.benerson_qty = item.benerson_qty + entry.quantity - new_quantity
                        
                        if current_receipt.type == "Transfer Slip":
                            item.qlinx_qty = item.qlinx_qty - entry.quantity + new_quantity
                            
                item.save()

                # update item in receipt quantity as needed
                entry.quantity = new_quantity
                entry.price = response.POST.get(f"{entry.id}price")
                entry.save()

    return render(response, 'inventory/editreceipt.html', 
        {"receipt": current_receipt,
        "items_in_receipt": items_in_receipt,
        "item_set": Item.objects.all()})