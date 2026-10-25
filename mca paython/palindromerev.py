n=9656
rev=0
temp=n
while n>0:
    rem=n%10
    rev=rev*10+rem
    n=n//10
print (rev)
if rev==temp:
    print("it is pali")
else:
    print("it is not pali")
