'''name=input("enter the name of the counsumer")
units=int(input("enter the units consumed"))
if units <= 100:
    bill= units*2
elif units <= 200:
    bill= 100*2 +(units-100)*3
else:
    bill= 100*2 + 100*3 +(units-200)*5
print("Counsumer Name:", name)
print("Total bill: ",bill)'''

'''Vechilenumber=input("enter the numbef of the vechile")
hours=int(input("enter the parking hours"))
if hours <=2 :
    fee= hours*20
elif hours <=5 :
    fee=2*20 + (hours-2)*15
else:
    fee=2*20 + 3*15 +(hours-5)*10
print("VechileNumber:",Vechilenumber)
print("TotalParkingFee:",fee)'''

inventory = {
    "Laptop":15,
    "Mouse":50,
    "Monitor":10,
    }
'''#display all products
for product,stock in inventory.items():
    print(product,stock)

#add new product
inventory["printer"]=12

#inceres laptop stock
inventory["Laptop"]+=10

#less than 15
print("Products with less than 15 stock: ")
for product,srock in inventory.items():
    if stock < 15:
        print(product,stock)
#total no of products
print("Total no of products:",len(inventory))'''

'''name=input("Enter the name of the customer")
days=int(input("Enter the no of days"))
bill=0
if days <=2:
    bill=days*1500
elif days<=5:
    bill=(1500*2 )+((days-2)*1200)
else:
    bill=(1500*2)+(1200*3)+((days-5)*1000)
print("Costomer name:",name)
print("Total bill:",bill)'''

'''name=input("Enter the name of the student")
mark=int(input("Enter the mark"))
if mark>=101 or mark<0:
    print("Invalid mark")
elif mark>=90:
    print'''


inventory = {
    "Laptop":15,
    "Mouse":50,
    "Monitor":10,
    }

for product,stock in inventory.items():
    print(product,stock)

inventory["printer"]=12
for product,stock in inventory.items():
    print(product,stock)




    




