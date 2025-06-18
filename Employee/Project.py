from abc import ABC, abstractmethod
import json
from typing import Optional

class Employee(ABC):
    def __init__(self, employee_id, name, department):
        self._employee_id, self._name, self._department = employee_id, name, department

    @property
    def employee_id(self): return self._employee_id
    @property
    def name(self): return self._name
    @property
    def department(self): return self._department
    @department.setter
    def department(self, value): self._department = value

    @abstractmethod
    def calculate_salary(self) -> float: pass

    def display_details(self) -> str:
        return f"ID: {self.employee_id}, Name: {self.name}, Dept: {self.department}"

    def to_dict(self) -> dict:
        return {'employee_id': self.employee_id, 'name': self.name, 'department': self.department, 'type': self.__class__.__name__.lower()}

class FullTimeEmployee(Employee):
    def __init__(self, emp_id, name, dept, monthly_salary):
        super().__init__(emp_id, name, dept)
        self.monthly_salary = monthly_salary

    @property
    def monthly_salary(self): return self._monthly_salary
    @monthly_salary.setter
    def monthly_salary(self, value):
        if value < 0: raise ValueError("Salary can't be negative.")
        self._monthly_salary = value

    def calculate_salary(self) -> float: return self.monthly_salary
    def display_details(self) -> str: return f"{super().display_details()}, Monthly Salary: ${self.monthly_salary:,.2f}"

class PartTimeEmployee(Employee):
    def __init__(self, emp_id, name, dept, rate, hours):
        super().__init__(emp_id, name, dept)
        self.hourly_rate, self.hours_worked = rate, hours

    def calculate_salary(self) -> float: return self.hourly_rate * self.hours_worked
    def display_details(self) -> str:
        return f"{super().display_details()}, Hourly Rate: ${self.hourly_rate:,.2f}, Hours Worked: {self.hours_worked}"

class Manager(FullTimeEmployee):
    def __init__(self, emp_id, name, dept, salary, bonus):
        super().__init__(emp_id, name, dept, salary)
        self.bonus = bonus

    def calculate_salary(self) -> float: return super().calculate_salary() + self.bonus
    def display_details(self) -> str: return f"{super().display_details()}, Bonus: ${self.bonus:,.2f}"

class Company:
    def __init__(self, data_file='employees.json'):
        self._employees, self._data_file = {}, data_file
        self._load_data()

    def _load_data(self):
        try:
            with open(self._data_file, 'r', encoding='utf-8') as f:
                for data in json.load(f):
                    emp = self._create_employee(data)
                    if emp: self._employees[emp.employee_id] = emp
        except: pass

    def _create_employee(self, data: dict) -> Optional[Employee]:
        try:
            t = data.get('type')
            return {
                'fulltime': lambda: FullTimeEmployee(data['employee_id'], data['name'], data['department'], data['monthly_salary']),
                'parttime': lambda: PartTimeEmployee(data['employee_id'], data['name'], data['department'], data['hourly_rate'], data['hours_worked_per_month']),
                'manager': lambda: Manager(data['employee_id'], data['name'], data['department'], data['monthly_salary'], data['bonus'])
            }.get(t, lambda: None)()
        except: return None

    def _save_data(self):
        with open(self._data_file, 'w', encoding='utf-8') as f:
            json.dump([e.to_dict() for e in self._employees.values()], f, indent=2)

    def add_employee(self, emp: Employee) -> bool:
        if emp.employee_id in self._employees: return False
        self._employees[emp.employee_id] = emp
        self._save_data()
        return True

    def remove_employee(self, eid: str) -> bool:
        if eid in self._employees:
            del self._employees[eid]
            self._save_data()
            return True
        return False

    def find_employee(self, eid: str) -> Optional[Employee]:
        return self._employees.get(eid)

    def search_employees_by_name(self, name: str):
        return [e for e in self._employees.values() if name.lower() in e.name.lower()]

    def calculate_total_payroll(self) -> float:
        return sum(e.calculate_salary() for e in self._employees.values())

    def display_all_employees(self):
        if not self._employees: print("No employees found.")
        else: [print(e.display_details()) for e in self._employees.values()]

    def generate_payroll_report(self):
        print("Payroll Report:\n" + "-"*60)
        print(f"{'ID':<12} {'Name':<25} {'Type':<10} {'Salary':>10}")
        print("-"*60)
        for e in self._employees.values():
            print(f"{e.employee_id:<12} {e.name:<25} {e.to_dict()['type'].capitalize():<10} ${e.calculate_salary():>10,.2f}")
        print("-"*60)
        print(f"{'Total Payroll:':<49} ${self.calculate_total_payroll():>10,.2f}")

def add_employee_interactive(company: Company):
    print("Select Type:\n1. Full-Time\n2. Part-Time\n3. Manager")
    t = input("Choice (1-3): ").strip()
    if t not in '123': print("Invalid choice."); return
    eid = input("Enter ID: ").strip()
    if company.find_employee(eid): print("Employee ID exists."); return
    name = input("Name: ").strip()
    dept = input("Department: ").strip()
    try:
        if t == '1':
            salary = float(input("Monthly Salary: "))
            emp = FullTimeEmployee(eid, name, dept, salary)
        elif t == '2':
            rate = float(input("Hourly Rate: "))
            hours = float(input("Hours Worked: "))
            emp = PartTimeEmployee(eid, name, dept, rate, hours)
        else:
            salary = float(input("Monthly Salary: "))
            bonus = float(input("Bonus: "))
            emp = Manager(eid, name, dept, salary, bonus)
        print("Employee added." if company.add_employee(emp) else "Add failed.")
    except ValueError:
        print("Invalid input.")

def main():
    company = Company()
    menu = """
Employee Management System
--------------------------
1. Add Employee
2. Remove Employee
3. View All Employees
4. Search Employee by ID
5. Search Employees by Name
6. Calculate Total Payroll
7. Generate Payroll Report
8. Exit"""

    while True:
        print(menu)
        c = input("Enter choice (1-8): ").strip()
        if c == '1': add_employee_interactive(company)
        elif c == '2': print("Removed." if company.remove_employee(input("Enter ID: ").strip()) else "Not found.")
        elif c == '3': company.display_all_employees()
        elif c == '4':
            emp = company.find_employee(input("Enter ID: ").strip())
            print(emp.display_details() if emp else "Not found.")
        elif c == '5':
            name = input("Enter name: ").strip()
            res = company.search_employees_by_name(name)
            print(f"{len(res)} found:" if res else "No matches.")
            for e in res: print(e.display_details())
        elif c == '6': print(f"Total Payroll: ${company.calculate_total_payroll():,.2f}")
        elif c == '7': company.generate_payroll_report()
        elif c == '8': print("Goodbye."); break
        else: print("Invalid choice.")

if __name__ == "__main__":
    main()
