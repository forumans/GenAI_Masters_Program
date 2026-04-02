"""Check Jane's hire date in the database."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'hr_assistant_api'))

from app.database import SessionLocal
from app.models.employee import Employee

def check_jane_date():
    """Check Jane's hire date directly from database."""
    print("=== Checking Jane's Hire Date ===")
    
    db = SessionLocal()
    try:
        # Find Jane
        jane = db.query(Employee).filter(
            (Employee.first_name.ilike('Jane')) |
            (Employee.last_name.ilike('Jane'))
        ).first()
        
        if jane:
            print(f"Found: {jane.full_name}")
            print(f"Raw hire_date: {jane.hire_date}")
            print(f"Type: {type(jane.hire_date)}")
            print(f"Year: {jane.hire_date.year}")
            print(f"Month: {jane.hire_date.month}")
            print(f"Day: {jane.hire_date.day}")
            print(f"Formatted (MM/DD/YYYY): {jane.hire_date.strftime('%m/%d/%Y')}")
            print(f"Formatted (YYYY-MM-DD): {jane.hire_date.strftime('%Y-%m-%d')}")
        else:
            print("Jane not found in database")
            
            # Try Smith
            smith = db.query(Employee).filter(Employee.last_name.ilike('Smith')).all()
            if smith:
                print(f"\nFound {len(smith)} employees with last name Smith:")
                for emp in smith:
                    print(f"  - {emp.full_name}: {emp.hire_date}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_jane_date()
