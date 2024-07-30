from django.shortcuts import render
from .models import Customer, Receipt, Item, ItemInReceipt
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.db.models.functions import Lower
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

## SUGGESTIONS ##
# add add receipt in sidenav to make it starting point

# inventory
def home(request):
    all_items = Item.objects.order_by(Lower('brand'), Lower('model'))
    context = {}

    laptops = all_items.filter(type__iexact="laptop")
    total_laptops = 0

    for item in laptops:
        total_laptops += item.benerson_qty + item.qlinx_qty

    context["total_laptops"] = total_laptops
    
    if request.method == "POST":
        if request.POST.get("addItem"):
            return HttpResponseRedirect('/additem-action=inventory')

        elif request.POST.get("editItem"):
            for item in all_items:
                if request.POST.get("c" + str(item.id)) == "clicked":
                    return HttpResponseRedirect('/i%i' %item.id)
                    
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

            if action == "inventory":
                benerson_qty = request.POST.get("bQty")
                qlinx_qty = request.POST.get("qQty")
            
            new = Item(type=type, model=model, brand=brand, specs=specs, costPrice=costPrice, srp=srp, benerson_qty=benerson_qty, qlinx_qty=qlinx_qty)
            new.save()
            
            # pop-up showing that item is saved

            next_url = f"/{action}"

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
    current_number = "Receipt Number"
    current_date = "Date"
    current_store = "From Which Store/Supplier?"
    current_customer = "Customer Name (FirstName LastName) / Name of Company"

    if 'number' in request.session:
        if request.session['number'] != "null":
            current_number = request.session.get('number')
            current_date = request.session.get('date')
            current_store = request.session.get('store')
            current_customer = request.session.get('customer')

            request.session['number'] = "null"
            request.session['date'] = "null"
            request.session['store'] = "null"
            request.session['customer'] = "null"

    if request.method == "POST":
        if request.POST.get("newReceipt"):
            number = request.POST.get("number")
            type = request.POST.get("type")
            date = request.POST.get("date")
            store = request.POST.get("store")
            new = Receipt(number=number,date=date,type=type,store=store)
            
            if type == "Sales Invoice":
                try:
                    customer = Customer.objects.get(name=request.POST.get("customerName"))
                    new.customer = customer
                except ObjectDoesNotExist:
                    request.session['number'] = number
                    request.session['date'] = date
                    request.session['store'] = store
                    request.session['customer'] = request.POST.get("customerName")
                    return HttpResponseRedirect("/addcustomer-action=''") # add customer view
                except MultipleObjectsReturned:
                    pass

            new.save()
            
            return HttpResponseRedirect(f"/r{new.id}")
        
    return render(request, 'inventory/addreceipt.html',
        {'customer_set': Customer.objects.all(),
        'number': current_number, 'date': current_date, 'store': current_store, 'customer': current_customer})
   
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
    message = ""

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
                        if item_quantity <= item.qlinx_qty:
                            item.qlinx_qty -= item_quantity
                        
                            if current_receipt.type == "Transfer Slip":
                                item.benerson_qty += item_quantity
                        else:
                            message = f"There are only {item.qlinx_qty} {item}'s in Qlinx. Enter a quantity less than or equal to {item.qlinx_qty} for {item}."
                        
                    if current_receipt.store == "Benerson":
                        if item_quantity <= item.benerson_qty:
                            item.benerson_qty -= item_quantity
                        
                            if current_receipt.type == "Transfer Slip":
                                item.qlinx_qty += item_quantity
                        else:
                            message = f"There are only {item.benerson_qty} {item}'s in Benerson. Enter a quantity less than or equal to {item.benerson_qty} for {item}."
                
                if message == "":    
                    item.save()

                    receipt_item = ItemInReceipt(item=item, receipt=current_receipt, quantity=item_quantity, price=item_price)
                    receipt_item.save()

                    if current_receipt.type != "Transfer Slip":
                        current_price = float(current_receipt.total_price) + float(item_quantity) * float(item_price)

                        current_receipt.total_price = makeStrPriceTwoDecimalPlaces(str(current_price))
                        current_receipt.save()

            except ObjectDoesNotExist:
                if current_receipt.type == "Supplier Invoice":
                    request.session['brand'] = item_brand
                    request.session['model'] = item_model
                    request.session['specs'] = item_specs
                    return HttpResponseRedirect(f"/additem-action=r{current_receipt.id}")

            except MultipleObjectsReturned:
                pass

        elif request.POST.get("save"):
            for entry in items_in_receipt:
                new_quantity = int(request.POST.get(f"{entry.id}qty"))
                new_price = request.POST.get(f"{entry.id}price")
                item = entry.item

                new_message = ""

                # update item model's quantity
                if current_receipt.type == "Supplier Invoice":
                    item.benerson_qty = item.benerson_qty - entry.quantity + new_quantity
                    
                else:
                    if current_receipt.store == "Qlinx":
                        if item.qlinx_qty + entry.quantity - new_quantity >= 0:
                            item.qlinx_qty = item.qlinx_qty + entry.quantity - new_quantity
                        
                            if current_receipt.type == "Transfer Slip":
                                item.benerson_qty = item.benerson_qty - entry.quantity + new_quantity
                        else:
                            if message != "":
                                new_message = "\n"

                            new_message += f"There are only {item.qlinx_qty + entry.quantity} {item}'s in Qlinx. Enter a quantity less than or equal to {item.qlinx_qty + entry.quantity} for {item}."
                            message += new_message
                        
                    if current_receipt.store == "Benerson":
                        if item.benerson_qty + entry.quantity - new_quantity >= 0:
                            item.benerson_qty = item.benerson_qty + entry.quantity - new_quantity
                        
                            if current_receipt.type == "Transfer Slip":
                                item.qlinx_qty = item.qlinx_qty - entry.quantity + new_quantity
                        else:
                            if message != "":
                                new_message = "\n"

                            new_message += f"There are only {item.benerson_qty + entry.quantity} {item}'s in Benerson. Enter a quantity less than or equal to {item.benerson_qty + entry.quantity} for {item}."
                            message += new_message

                if new_message == "":
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
         "brand": current_brand, "model": current_model, "specs": current_specs, "message": message})

def customersList(request):
    all_customers = Customer.objects.order_by('name')
    context = {}

    if request.method == "POST":
        if request.POST.get("addCustomer"):
            return HttpResponseRedirect('/addcustomer-action=customersList')

        elif request.POST.get("editCustomer"):
            for customer in all_customers:
                if request.POST.get("c" + str(customer.id)) == "clicked":
                    return HttpResponseRedirect('/c%i' %customer.id)
                    
        elif request.POST.get("searchCustomer"):
            search = [word for word in request.POST.get("customer_searched").split()]
            
            for word in search:
                all_customers = all_customers.filter(
                    Q(name__contains=word) |
                    Q(demographic__contains=word) |
                    Q(street__contains=word) |
                    Q(barangay__contains=word) |
                    Q(city__contains=word) |
                    Q(province__contains=word) |
                    Q(region__contains=word)
                )
                    
    context["customer_set"] = all_customers

    return render(request, 'inventory/customersList.html', context)

def addCustomer(request, action):
    if request.method == "POST":
        if request.POST.get("newCustomer"):
            name = request.POST.get("name")
            demographic = request.POST.get("demographic")
            street = request.POST.get("street")
            barangay = request.POST.get("barangay")
            city = request.POST.get("city")
            province = request.POST.get("province")
            region = request.POST.get("region")
            
            new = Customer(name=name, street=street, barangay=barangay, city=city, province=province, region=region, demographic=demographic)
            new.save()
            
            # pop-up showing that customer is saved

            next_url = "/"

            if action == "customersList":
                next_url += action

            return HttpResponseRedirect(next_url)

    current_customer = "*Customer Name (FirstName LastName) / Name of Company"

    if 'customer' in request.session:
        if request.session['customer'] != "null":
            current_customer = request.session.get('customer')

    return render(request, 'inventory/addcustomer.html', {"customerName": current_customer})

#edit customer
def showCustomer(request, id):
    current_customer = Customer.objects.get(id=id)
    
    if request.method == "POST":
        if request.POST.get("editCustomer"):
            current_customer.name = request.POST.get("name")
            current_customer.demographic = request.POST.get("demographic")
            current_customer.street = request.POST.get("street")
            current_customer.barangay = request.POST.get("barangay")
            current_customer.city = request.POST.get("city")
            current_customer.province = request.POST.get("province")
            current_customer.region = request.POST.get("region")
            
            current_customer.save()
            
            # pop-up showing that customer is edited

            return HttpResponseRedirect("/customersList")
    
    return render(request, 'inventory/editcustomer.html', {"customer":current_customer})

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
