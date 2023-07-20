from django.db import models

# might use but idk yet
# class Store(models.Model):
    # name = models.CharField(max_length=100)
    
    # def __str__(self):
        # return self.name

class Receipt(models.Model):
    number = models.CharField(max_length=50)
    date = models.DateField()
    type = models.CharField(max_length=100) # supplier invoice, transfer slip, sales invoice
    store = models.CharField(max_length=100) # source of stock
    # SupI >> supplier - Benerson; TS >> Benerson - Qlinx (vice-versa); SalI >> Benerson/Qlinx - customer
    quantities = models.CharField(max_length=500)
    
    def __str__(self):
        return self.number

class Item(models.Model):
    receipts = models.ManyToManyField(Receipt)
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