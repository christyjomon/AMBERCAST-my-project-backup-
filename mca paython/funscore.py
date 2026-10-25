'''def calc_average(s1, s2, s3, s4, s5):
    return (s1 + s2 + s3 + s4 + s5) / 5

def determine_grade(score):
    if 90 <= score <= 100:
        return 'A'
    elif 80 <= score < 90:
        return 'B'
    elif 70 <= score < 79:
        return 'C'
    elif 60 <= score < 69:
        return 'D'
    else:
        return 'F'

# Collecting 5 scores
scores = []
for i in range(1, 6):
    s = float(input(f"Enter test score {i}: "))
    scores.append(s)

print("\nTest Scores and Letter Grades:")
for i, s in enumerate(scores, start=1):
    print(f"Test {i}: {s} - Grade: {determine_grade(s)}")

avg = calc_average(*scores)
print(f"Average Test Score: {avg:.2f} - Grade: {determine_grade(avg)}")'''

class Employee:
    def __init__(self, name, employee_id, base_salary, department):
        self.name = name
        self.employee_id = employee_id
        self.base_salary = base_salary
        self.department = department

    def calculate_total_salary(self, bonus_percent=10):
        return self.base_salary + (self.base_salary * (bonus_percent / 100))

    def display_details(self):
        total = self.calculate_total_salary()
        return f"Name: {self.name} | Employee ID: {self.employee_id} | Department: {self.department} | Base Salary: ${self.base_salary} | Total Salary: ${int(total)}"

class Payroll:
    def __init__(self):
        self.employees = []

    def add_employee(self, emp):
        self.employees.append(emp)

    def display_all(self):
        print("Employee List:")
        for idx, emp in enumerate(self.employees, start=1):
            print(f"{idx}. {emp.display_details()}")
payroll = Payroll()
payroll.add_employee(Employee("John Doe", 101, 5000, "HR"))
payroll.add_employee(Employee("Jane Smith", 102, 6000, "IT"))
payroll.display_all()            
