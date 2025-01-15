import mysql.connector
from mysql.connector import Error
import random
from faker import Faker

def connect_to_database(host, user, password, database=None):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

def create_schema_and_tables(connection):
    cursor = connection.cursor()
    
    # Create Departments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS departments (
        department_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE
    );
    """)

# Create Students table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id INT AUTO_INCREMENT PRIMARY KEY,
        usn VARCHAR(10) NOT NULL UNIQUE,
        name VARCHAR(100) NOT NULL,
        department_id INT NOT NULL,
        cgpa DECIMAL(3, 2) NOT NULL,
        email VARCHAR(100),
        phone VARCHAR(20),  # Increased size
        gender ENUM('Male', 'Female', 'Other'),
        date_of_birth DATE,
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
    );
    """)

    # Create Companies table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS companies (
        company_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE,
        eligibility_cgpa DECIMAL(3, 2) NOT NULL,
        max_package DECIMAL(10, 2),
        min_package DECIMAL(10, 2)
    );
    """)

    # Create Placements table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS placements (
        placement_id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT NOT NULL,
        company_id INT NOT NULL,
        status ENUM('Placed', 'Not Placed', 'Pending'),
        package_offered DECIMAL(10, 2),
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (company_id) REFERENCES companies(company_id)
    );
    """)

    connection.commit()
    print("Schema and tables created successfully.")

def insert_initial_data(connection):
    cursor = connection.cursor()

    # Insert into Departments
    cursor.executemany("""
    INSERT INTO departments (name) VALUES (%s)
    """, [
        ('Computer Science',),
        ('Information Technology',),
        ('Electronics and Communication',),
        ('Mechanical Engineering',),
        ('Civil Engineering',)
    ])

    # Insert into Companies
    cursor.executemany("""
    INSERT INTO companies (name, eligibility_cgpa, max_package, min_package) VALUES (%s, %s, %s, %s)
    """, [
        ('Google', 8.0, 35.00, 15.00),
        ('Microsoft', 7.5, 30.00, 12.00),
        ('Amazon', 8.0, 28.00, 10.00),
        ('Infosys', 6.5, 8.00, 3.50),
        ('TCS', 6.0, 6.00, 3.00)
    ])

    connection.commit()
    print("Initial data inserted successfully.")

def generate_dummy_data(num_records):
    fake = Faker()
    departments = [1, 2, 3, 4, 5]  # Department IDs
    students = []
    for i in range(1, num_records + 1):
        usn = f"S{i:03d}"
        name = fake.name()
        department_id = random.choice(departments)
        cgpa = round(random.uniform(6.0, 10.0), 2)
        email = fake.email()
        phone = fake.phone_number()[:15]  # Ensure phone number fits the column
        gender = random.choice(['Male', 'Female', 'Other'])
        date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=25).isoformat()
        students.append((usn, name, department_id, cgpa, email, phone, gender, date_of_birth))
    return students


def insert_bulk_students(connection, num_records):
    cursor = connection.cursor()
    students = generate_dummy_data(num_records)
    cursor.executemany("""
    INSERT INTO students (usn, name, department_id, cgpa, email, phone, gender, date_of_birth)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, students)
    connection.commit()
    print(f"{num_records} records inserted into students table.")

def insert_bulk_placements(connection, num_records):
    cursor = connection.cursor()
    student_ids = list(range(1, num_records + 1))
    company_ids = [1, 2, 3, 4, 5]  # Company IDs
    placements = []
    for student_id in student_ids:
        company_id = random.choice(company_ids)
        status = random.choice(['Placed', 'Not Placed', 'Pending'])
        package_offered = round(random.uniform(3.0, 35.0), 2) if status == 'Placed' else None
        placements.append((student_id, company_id, status, package_offered))
    cursor.executemany("""
    INSERT INTO placements (student_id, company_id, status, package_offered)
    VALUES (%s, %s, %s, %s)
    """, placements)
    connection.commit()
    print(f"{num_records} records inserted into placements table.")

def run_query(connection, query):
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query)
    results = cursor.fetchall()
    return results

if __name__ == "__main__":
    # Replace with your credentials
    HOST = "54.190.25.85"
    # HOST = "localhost"
    USER = "kavya"
    PASSWORD = "kavya"
    DATABASE = "placementdb"

    # Connect to MySQL
    conn = connect_to_database(HOST, USER, PASSWORD)

    # Create Database if it doesn't exist
    if conn:
        conn.cursor().execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE}")
        conn.commit()

        # Connect to the newly created database
        conn.database = DATABASE

        # Create schema and insert initial data
        create_schema_and_tables(conn)
        insert_initial_data(conn)

        # Insert bulk data
        num_records = 50
        insert_bulk_students(conn, num_records)
        insert_bulk_placements(conn, num_records)

        # Test queries
        print("Number of Students Placed:")
        print(run_query(conn, "SELECT COUNT(*) AS placed_students FROM placements WHERE status = 'Placed';"))

        print("\nList of Eligible Students for Google:")
        print(run_query(conn, """
        SELECT s.usn, s.name, s.cgpa
        FROM students s
        JOIN companies c ON c.name = 'Google'
        WHERE s.cgpa >= c.eligibility_cgpa;
        """))

        # Close the connection
        conn.close()
