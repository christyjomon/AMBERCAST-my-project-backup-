mark=float(input("enter the mark"))
if mark>100 or mark<0:
    print("mark is invalid")
elif mark>=90:
    print("A+")
elif mark>=80:
    print("A")
elif mark>=70:
    print("B+")
elif mark>=60:
    print("B")
elif mark<50 and mark>10:
    print("D")
else:
    print("failed")
    
    
