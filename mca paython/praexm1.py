'''inventory = {
    "Laptop": 15,
    "Mouse": 50,
    "Keyboard": 30,
    "Monitor": 10,
    "Webcam": 20
}

# a) Display all products
for product, stock in inventory.items():
    print(product, stock)

# b) Add new product
inventory["Printer"] = 12

# c) Increase Laptop stock
inventory["Laptop"] += 10

# d) Products with stock less than 15
print("Products with stock less than 15:")

for product, stock in inventory.items():
    if stock < 15:
        print(product, stock)

# e) Total number of products
print("Total products:", len(inventory))
'''


name = input("Enter consumer name: ")
units = int(input("Enter units consumed: "))

if units <= 100:
    bill = units * 2

elif units <= 200:
    bill = 100 * 2 + (units - 100) * 3

else:
    bill = 100 * 2 + 100 * 3 + (units - 200) * 5

print("Consumer Name:", name)
print("Total Bill: ₹", bill)
