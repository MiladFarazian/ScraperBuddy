import csv

def extract_course_info(input_file, output_file):
    """
    Extract course number, title, and instructor from a CSV file and save to a new CSV.
    
    Args:
        input_file (str): Path to the input CSV file
        output_file (str): Path to the output CSV file
    """
    # Lists to store the extracted data
    course_data = []
    
    # Read the input CSV file
    with open(input_file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        
        # Extract the required fields for each row
        for row in reader:
            course_info = {
                'Course number': row['Course number'],
                'Course title': row['Course title'],
                'Instructor': row['Instructor']
            }
            course_data.append(course_info)
    
    # Write the extracted data to the output CSV file
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['Course number', 'Course title', 'Instructor']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for course in course_data:
            writer.writerow(course)
    
    print(f"Extraction complete. Data saved to {output_file}")

# Example usage
if __name__ == "__main__":
    input_file = "usc_all_classes.csv"
    output_file = "usc_all_courses_simplified.csv"
    extract_course_info(input_file, output_file)
