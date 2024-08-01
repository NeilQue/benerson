from django.db import models

# might use but idk yet
# class Store(models.Model):
    # name = models.CharField(max_length=100)
    
    # def __str__(self):
        # return self.name

class Customer(models.Model):
    name = models.CharField(max_length=255)

    # address
    street = models.CharField(max_length=255, null=True)
    barangay = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=75)
    province = models.CharField(max_length=75)
    region = models.CharField(max_length=15)

    demographic = models.CharField(max_length=255) # teacher, student, soldier
                                                   # for companies / institutions: school, hospital, office

    def __str__(self):
        return self.name

class Receipt(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True)
    number = models.CharField(max_length=50)
    date = models.DateField()
    type = models.CharField(max_length=100) # supplier invoice, transfer slip, sales invoice
    store = models.CharField(max_length=100, null=True) # source of stock
                                            # SupI >> supplier - Benerson; TS >> Benerson - Qlinx (vice-versa);
                                            # SalI / CI>> Benerson/Qlinx - customer
    total_price = models.CharField(max_length=15, default="0.00")
    amount_paid = models.CharField(max_length=15, default="0.00")
    
    def __str__(self):
        return f'Receipt #{self.number}'

class Item(models.Model):
    type = models.CharField(max_length=100) # laptop, desktop, computer part
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=200)
    specs = models.CharField(max_length=300)
    costPrice = models.CharField(max_length=50)
    srp = models.CharField(max_length=50)
    benerson_qty = models.IntegerField()
    qlinx_qty = models.IntegerField()
    # total quantity will be added to database shown to user (as of now)
    
    def __str__(self):
        return f'{self.brand} {self.model} {self.specs}'

class ItemInReceipt(models.Model):
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.item} in {self.receipt}'

class ReceiptInReceipt(models.Model):
    paid_receipt = models.ForeignKey(Receipt, on_delete=models.PROTECT, related_name="paid_receipt")     # receipt that has remaining balance
    source_document = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name="source_document")  # receipt that contains payment towards balance
    amount_paid = models.CharField(max_length=15, default="0.00")

    def __str__(self):
        return f'{self.paid_receipt} in {self.source_document}'