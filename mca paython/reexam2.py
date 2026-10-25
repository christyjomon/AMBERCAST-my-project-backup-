marks = {
    "Anu": 78,
    "Rahul": 65,
    "Meera": 89,
    "Arun": 55,
    "Neha": 92
}

# a) Display all students and their marks
print("Students and Marks:")
for name, mark in marks.items():
    print(name, ":", mark)

# b) Add new student Vishnu
marks["Vishnu"] = 81

# c) Increase Rahul's marks by 5
marks["Rahul"] = marks["Rahul"] + 5

# d) Display students who scored more than 80
print("\nStudents who scored more than 80:")
for name, mark in marks.items():
    if mark > 80:
        print(name, ":", mark)

# e) Display total number of students
print("\nTotal number of students:", len(marks))
