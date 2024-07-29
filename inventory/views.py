from django.shortcuts import render
from .models import Receipt, Item, ItemInReceipt
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.db.models.functions import Lower
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

## SUGGESTIONS ##
# add add receipt in sidenav to make it starting point

def home(request):
    all_items = Item.objects.order_by(Lower('brand'), Lower('model'))
    context = {}

    laptops = all_items.filter(type__iexact="laptop")
    total_laptops = 0

    for item in laptops:
        total_laptops += item.benerson_qty + item.qlinx_qty

    context["total_laptops"] = total_laptops
    
    if request.method == "POST":
        if request.POST.get("editItem"):
            for item in all_items:
                if request.POST.get("c" + str(item.id)) == "clicked":
                    return HttpResponseRedirect('/i%i' %item.id)
            
        elif request.POST.get("delItem"):
            for item in all_items:
                if request.POST.get("c" + str(item.id)) == "clicked":
                    item.delete()
                    
            return HttpResponseRedirect("/inventory")
                    
        elif request.POST.get("searchItem"):
            search = [word for word in request.POST.get("item_searched").split()]
            
            for word in search:
                all_items = all_items.filter(
                    Q(brand__contains=word) |
                    Q(type__contains=word) |
                    Q(model__contains=word) |
                    Q(specs__contains=word)
                )
                    
    context["item_set"] = all_items

    return render(request, 'inventory/home.html', context)
   
def addItem(request, action):
    if request.method == "POST":
        if request.POST.get("newItem"):
            type = request.POST.get("type")
            model = request.POST.get("model")
            brand = request.POST.get("brand")
            specs = request.POST.get("description")
            costPrice = makeStrPriceTwoDecimalPlaces(request.POST.get("costPrice"))
            srp = makeStrPriceTwoDecimalPlaces(request.POST.get("srp"))
            benerson_qty = 0
            qlinx_qty = 0

            next_url = f"/{action}"

            if action == "inventory":
                benerson_qty = request.POST.get("bQty")
                qlinx_qty = request.POST.get("qQty")
            
            new = Item(type=type, model=model, brand=brand, specs=specs, costPrice=costPrice, srp=srp, benerson_qty=benerson_qty, qlinx_qty=qlinx_qty)
            new.save()
            
            # pop-up showing that item is saved

            return HttpResponseRedirect(next_url)

    current_brand = "Brand"
    current_model = "Model"
    current_specs = "Specs"

    if 'brand' in request.session:
        if request.session['brand'] != "null":
            current_brand = request.session.get('brand')
            current_model = request.session.get('model')
            current_specs = request.session.get('specs')

    return render(request, 'inventory/additem.html', {"action": action, "brand": current_brand, "model": current_model, "specs": current_specs})
    
#logs
def searchReceipt(request):
    all_receipts = Receipt.objects.order_by('date').reverse()
    
    if request.method == "POST":
        if request.POST.get("search_receipt"):
            search = request.POST.get("receipt_searched")
            
            results = Receipt.objects.filter(number=search)
            
            return render(request, 'inventory/searchreceipt.html', {"receipt_set": results})
    
    return render(request, 'inventory/searchreceipt.html', {"receipt_set": all_receipts})

@login_required    
def addReceipt(request):
    if request.method == "POST":
        if request.POST.get("newReceipt"):
            number = request.POST.get("number")
            type = request.POST.get("type")
            date = request.POST.get("date")
            store = request.POST.get("store")
            
            new = Receipt(number=number,date=date,type=type,store=store)
            new.save()
            
            return HttpResponseRedirect(f"/r{new.id}")
        
    return render(request, 'inventory/addreceipt.html', {})
   
#edit item
def showItem(request, id):
    current_item = Item.objects.get(id=id)
    
    if request.method == "POST":
        if request.POST.get("editItem"):
            current_item.type = request.POST.get("type")
            current_item.model = request.POST.get("model")
            current_item.brand = request.POST.get("brand")
            current_item.specs = request.POST.get("description")
            current_item.costPrice = makeStrPriceTwoDecimalPlaces(request.POST.get("costPrice"))
            current_item.srp = makeStrPriceTwoDecimalPlaces(request.POST.get("srp"))
            current_item.benerson_qty = request.POST.get("bQty")
            current_item.qlinx_qty = request.POST.get("qQty")
            
            current_item.save()
            
            # pop-up showing that item is edited

            return HttpResponseRedirect("/inventory")
    
    return render(request, 'inventory/edititem.html', {"item":current_item})

#edit receipt
def showReceipt(request, id):
    current_receipt = Receipt.objects.get(id=id)
    items_in_receipt = ItemInReceipt.objects.filter(receipt=current_receipt)

    current_brand = "Brand"
    current_model = "Model"
    current_specs = "Specs"

    if 'brand' in request.session:
        if request.session['brand'] != "null":
            current_brand = request.session.get('brand')
            current_model = request.session.get('model')
            current_specs = request.session.get('specs')

            request.session['brand'] = "null"
            request.session['model'] = "null"
            request.session['specs'] = "null"

    if request.method == "POST":
        if request.POST.get("addItem"):
            item_brand = request.POST.get("brand")
            item_model = request.POST.get("model")
            item_specs = request.POST.get("specs")
            item_quantity = int(request.POST.get("quantity"))
            item_price = makeStrPriceTwoDecimalPlaces(request.POST.get("price"))

            try:
                item = Item.objects.get(brand=item_brand, model=item_model, specs=item_specs)

                # update item model's quantity
                if current_receipt.type == "Supplier Invoice":
                    item.benerson_qty += item_quantity
                    
                else:
                    if current_receipt.store == "Qlinx":
                        item.qlinx_qty -= item_quantity
                        
                        if current_receipt.type == "Transfer Slip":
                            item.benerson_qty += item_quantity
                        
                    if current_receipt.store == "Benerson":
                        item.benerson_qty -= item_quantity
                        
                        if current_receipt.type == "Transfer Slip":
                            item.qlinx_qty += item_quantity
                            
                item.save()

                receipt_item = ItemInReceipt(item=item, receipt=current_receipt, quantity=item_quantity, price=item_price)
                receipt_item.save()

                if current_receipt.type != "Transfer Slip":
                    current_price = float(current_receipt.total_price) + float(item_quantity) * float(item_price)

                    current_receipt.total_price = makeStrPriceTwoDecimalPlaces(str(current_price))
                    current_receipt.save()

            except ObjectDoesNotExist:
                request.session['brand'] = item_brand
                request.session['model'] = item_model
                request.session['specs'] = item_specs
                return HttpResponseRedirect(f"/additem-action=r{current_receipt.id}")

        elif request.POST.get("save"):
            for entry in items_in_receipt:
                new_quantity = int(request.POST.get(f"{entry.id}qty"))
                new_price = request.POST.get(f"{entry.id}price")
                item = entry.item

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

                # update receipt's total price as needed
                if current_receipt.type != "Transfer Slip":
                    current_price = float(current_receipt.total_price) - float(entry.quantity) * float(entry.price)
                    current_price = str(current_price + float(new_quantity) * float(new_price))

                    current_receipt.total_price = makeStrPriceTwoDecimalPlaces(current_price)
                    current_receipt.save()

                # update item in receipt quantity as needed
                entry.quantity = new_quantity
                entry.price = makeStrPriceTwoDecimalPlaces(new_price)
                entry.save()

    return render(request, 'inventory/editreceipt.html', 
        {"receipt": current_receipt, "items_in_receipt": items_in_receipt, "item_set": Item.objects.all(),
         "brand": current_brand, "model": current_model, "specs": current_specs})

# helper function to make prices have two decimal places
def makeStrPriceTwoDecimalPlaces(price):
    offset = 0.0001
    price = str(round(float(price) + offset,2))

    if '.' not in price:
        return price + '.00'
    elif price[-2] == '.':
        return price + '0'
    else:
        return price
