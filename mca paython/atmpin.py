'''
balance=500
pin=456

for i in range(1,6):
    n=int(input("enter the pin"))
    if pin==n:
        print("correct pin")
        break
    else:
        print("not correct")
     '''
        
    
balance=500
pin=456

for i in range(1,6):
    n=int(input("enter the pin"))
    if pin==n:
        print("correct pin " "\nThe balance is",balance)
        break
    else:
        print("not correct")
        print("you have",5-i,"chance left")
