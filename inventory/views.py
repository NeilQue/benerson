from django.shortcuts import render
from .models import Receipt, Item
from django.http import HttpResponseRedirect
from django.db.models import Q

## SUGGESTIONS ##
# add sort button (alphabetically)
# add filter button (by item type)
# get total number of laptops

def home(response):
    all_items = Item.objects.order_by('brand', 'model')
    
    if response.method == "POST":
        if response.POST.get("makeTransaction"):
            new = Receipt(number='null',date='1970-01-01',type='null',store='null', quantities='null')
            new.save()
            
            for item in all_items:
                if response.POST.get("c" + str(item.id)) == "clicked":
                    item.receipts.add(new)
            
            return HttpResponseRedirect("/r%i" %new.id)
            
        elif response.POST.get("editItem"):
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
                
            return render(response, 'inventory/home.html', {"item_set": results})
                    
    return render(response, 'inventory/home.html', {"item_set": all_items})
    
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
    
#page after make transaction
def addReceipt(response, id):
    current_receipt = Receipt.objects.get(id=id)    
    
    if current_receipt.quantities == "null":
        zipped_list = []
    else:
        quantities_list = current_receipt.quantities.split('.')
        items_list = list(current_receipt.item_set.all())
        zipped_list = zip(items_list, quantities_list)
    
    if response.method == "POST":
        if response.POST.get("newReceipt"):
            current_receipt.number = response.POST.get("number")
            current_receipt.date = response.POST.get("date")
            current_receipt.store = response.POST.get("store")
            
            temp_string = ""
            
            for item in current_receipt.item_set.all():
                if response.POST.get("type") == "supplierInvoice":
                    current_receipt.type = "Supplier Invoice"
                    
                    item.benerson_qty += int(response.POST.get(str(item.id) + "Qty"))
                    
                elif response.POST.get("type") == "transferSlip":
                    current_receipt.type = "Transfer Slip"
                    
                    if current_receipt.store == "Benerson":
                        item.benerson_qty -= int(response.POST.get(str(item.id) + "Qty"))
                        item.qlinx_qty += int(response.POST.get(str(item.id) + "Qty"))
                        
                    elif current_receipt.store == "Qlinx":
                        item.benerson_qty += int(response.POST.get(str(item.id) + "Qty"))
                        item.qlinx_qty -= int(response.POST.get(str(item.id) + "Qty"))
                        
                elif response.POST.get("type") == "salesInvoice":
                    current_receipt.type = "Sales Invoice"
                    
                    if current_receipt.store == "Benerson":
                        item.benerson_qty -= int(response.POST.get(str(item.id) + "Qty"))
                        
                    elif current_receipt.store == "Qlinx":
                        item.qlinx_qty -= int(response.POST.get(str(item.id) + "Qty"))
                        
                item.save()
                
                temp_string += str(response.POST.get(str(item.id) + "Qty")) + "."
            
            current_receipt.quantities = temp_string
            current_receipt.save()            
            
            quantities_list = current_receipt.quantities.split('.')
            items_list = list(current_receipt.item_set.all())
            zipped_list = zip(items_list, quantities_list)
            
            # pop-up showing that receipt is saved
            
    return render(response, 'inventory/addreceipt.html', {"receipt":current_receipt, "zipped_list":zipped_list})
   
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