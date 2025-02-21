import os
import requests
import time

global serverIP
serverIP = 'localhost:5000'

def main():
    while True:
        print("What would you like to do? (1, 2)")
        print("1. Add your own classes")
        print("2. Check who your closest link is\n")
        
        choice = input()
        
        if choice not in ['1', '2']:
            print("Not a valid input, please try again!")
        else:
            break
    
    match choice:
        case '1':
            formatted_name, student_id, classes = add_user_classes()
            # Send data to server
            try:
                response = requests.get(f"http://{serverIP}/add/{formatted_name}/{student_id}/{classes}")
                if response.status_code == 200:
                    print("\nSuccessfully added your classes to the database!")
                else:
                    print("\nError: Failed to add classes to database")
                time.sleep(2)
            except Exception as e:
                print(f"\nError connecting to server: {e}")
                time.sleep(2)
        case '2':
            check_user_classes_with_others()
        case _:
            print("Invalid choice")

def check_user_classes_with_others():
    os.system('cls')  # Clear screen only at start
    print("\n=== Find Your Class Links ===")
    
    classes = []
    identifier = ""
    match_history = []  # Store all matches
    
    # Get user identifier
    while True:
        identifier = input("Enter your student ID or full name (or press Enter to skip): ").strip()
        if not identifier:  # Skip to manual class entry
            break
            
        try:
            if identifier.isdigit() and len(identifier) >= 4:
                response = requests.get(f"http://{serverIP}/get/student/{identifier}")
            elif len(identifier.split()) >= 2:
                formatted_name = identifier.replace(" ", "_")
                response = requests.get(f"http://{serverIP}/get/student/name/{formatted_name}")
            else:
                print("Please enter a valid student ID (4+ digits) or full name (first and last name)")
                continue

            if response.status_code == 200:
                classes = response.json()['classes'].split(',')
                print(f"\nFound your existing classes: {', '.join(classes)}")
                time.sleep(1)
                break
            else:
                print("No existing classes found. You can enter them manually.")
                time.sleep(1)
                break
                
        except Exception as e:
            print(f"Error connecting to server: {e}")
            time.sleep(1)
            break
    
    # Manual class entry loop
    while True:
        print("\n=== Your Class Links ===")
        if identifier:
            print(f"Your ID/Name: {identifier}")
        print(f"Current Classes: {', '.join(classes) if classes else 'None'}\n")
        
        class_code = input("Input your class (or 'done' to finish): ").strip().upper()
        
        if class_code.lower() == 'done':
            if not classes:
                print("Please add at least one class")
                time.sleep(1)
                continue
            # Show final match before exiting
            try:
                classes_string = ",".join(classes)
                response = requests.get(f"http://{serverIP}/get/{classes_string}")
                
                if response.status_code == 200 and response.json().get('match'):
                    match_data = response.json()['match']
                    print("\n═══ Final Match Result ═══")
                    print(f"Name: {match_data['name'].replace('_', ' ')}")
                    print(f"Matching Classes: {', '.join(match_data['matching_classes'])}")
                    print(f"Their Total Classes: {', '.join(match_data['classes'])}")
                    print("═════════════════════════\n")
                else:
                    print("\nNo matching students found with your classes.\n")
            except Exception as e:
                print(f"\nError connecting to server: {e}\n")
            break
            
        if not validate_class_code(class_code):
            print("Invalid class code format. Examples: 11SE1, 10ENGW, 9MAT3")
            continue
            
        if class_code not in classes:  # Prevent duplicate classes
            classes.append(class_code)

        # Request matches from server
        try:
            classes_string = ",".join(classes)
            response = requests.get(f"http://{serverIP}/get/{classes_string}")
            
            if response.status_code == 200 and response.json().get('match'):
                match_data = response.json()['match']
                # Store the match in history
                match_display = (
                    f"\n═══ Match Found ═══\n"
                    f"Name: {match_data['name'].replace('_', ' ')}\n"
                    f"Matching Classes: {', '.join(match_data['matching_classes'])}\n"
                    f"Their Total Classes: {', '.join(match_data['classes'])}\n"
                    f"═════════════════════════\n"
                )
                match_history.append(match_display)
                # Show all previous matches
                for match in match_history:
                    print(match)
            else:
                print("\nNo matching students available at this time.\n")
                
        except Exception as e:
            print(f"\nError connecting to server: {e}\n")
        
        time.sleep(1)

    return classes

count = 0
global total_classes 
total_classes = []

def add_user_classes():
    global count, total_classes
    print("\n=== Student Information ===")
    
    # Get student name
    while True:
        full_name = input("Enter your full name: ").strip()
        if len(full_name.split()) >= 2:  # Ensure at least first and last name
            break
        print("Please enter your full name (first and last name)")
    
    # Get student ID
    while True:
        student_id = input("Enter your student ID: ").strip()
        if student_id.isdigit() and len(student_id) >= 4:  # Assuming student IDs are at least 4 digits
            break
        print("Invalid student ID format. Please enter a number with at least 4 digits")

    print("\nAdd your classes in CLASSCODE format")
    print("Examples: 11SE1, 11PHY2, 10ENGW")
    print("Enter 'done' to finish adding classes")
    print("Tip: Check your sentral to see the CLASSCODE\n")
    
    count = 0
    total_classes = []
    
    while True:
        count += 1
        class_code = input(f"Input Class {count} (or 'done' to finish): ").strip().upper()
        
        if class_code.lower() == 'done':
            if count == 1:  # No classes added yet
                print("Please add at least one class")
                count = 0
                continue
            break
            
        # Validate class code format
        if not validate_class_code(class_code):
            print("Invalid class code format. Examples: 11SE1, 10ENGW, 9MAT3")
            count -= 1
            continue
            
        total_classes.append(class_code)
    
    # Format data for server request
    formatted_name = full_name.replace(" ", "_")
    classes_string = ",".join(total_classes)
    
    print("\nSummary:")
    print(f"Name: {full_name}")
    print(f"Student ID: {student_id}")
    print(f"Classes: {', '.join(total_classes)}")
    
    return formatted_name, student_id, classes_string

def validate_class_code(code):
    # Basic validation rules:
    # 1. Must be at least 4 characters long
    # 2. Must start with a grade number (7-12)
    # 3. Middle part must contain letters
    
    if len(code) < 4:
        return False
        
    # Check grade number
    if not code[:2].isdigit() or int(code[:2]) not in range(7, 13):
        return False
        
    # Middle part should contain letters (at least one)
    middle = code[2:]
    if not any(c.isalpha() for c in middle):
        return False
        
    return True

main()