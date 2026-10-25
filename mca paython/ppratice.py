'''def check_prime(n):
    if n <= 1:
        return False

    for i in range(2, n):
        if n % i == 0:
            return False

    return True


num = int(input("Enter a number: "))

if check_prime(num):
    print("Prime number")
else:
    print("Not prime ")
    '''

def grade(mark):
    if mark >= 90 and mark <= 100:
        return "A+"
    elif mark >= 80:
        return "A"
    elif mark >= 70:
        return "B"
    elif mark >= 60:
        return "C"
    elif mark >= 50:
        return "D"
    else:
        return "F"


mark = int(input("Enter student's mark: "))
print("Grade =", grade(mark))
