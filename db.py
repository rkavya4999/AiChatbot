import mysql.connector
from mysql.connector import Error

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
        phone VARCHAR(15),
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

def insert_dummy_data(connection):
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

    # Insert into Students
    cursor.executemany("""
    INSERT INTO students (usn, name, department_id, cgpa, email, phone, gender, date_of_birth) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, [
        ('CS001', 'Alice Johnson', 1, 8.5, 'alice.johnson@example.com', '9876543210', 'Female', '2000-05-15'),
        ('CS002', 'Bob Smith', 1, 7.8, 'bob.smith@example.com', '9123456780', 'Male', '1999-11-22'),
        ('IT001', 'Charlie Brown', 2, 9.2, 'charlie.brown@example.com', '9876512345', 'Male', '2001-03-10'),
        ('EC001', 'Diana Green', 3, 8.0, 'diana.green@example.com', '9876540987', 'Female', '1998-09-30'),
        ('ME001', 'Edward Davis', 4, 7.5, 'edward.davis@example.com', '9876523451', 'Male', '2000-01-20'),
        ('CE001', 'Fiona Harris', 5, 8.9, 'fiona.harris@example.com', '9876598765', 'Female', '1999-07-18')
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

    # Insert into Placements
    cursor.executemany("""
    INSERT INTO placements (student_id, company_id, status, package_offered) VALUES (%s, %s, %s, %s)
    """, [
        (1, 1, 'Placed', 35.00),
        (2, 2, 'Placed', 12.00),
        (3, 1, 'Not Placed', None),
        (4, 4, 'Placed', 3.80),
        (5, 5, 'Placed', 3.50),
        (6, 3, 'Pending', None)
    ])

    connection.commit()
    print("Dummy data inserted successfully.")

def run_query(connection, query):
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query)
    results = cursor.fetchall()
    return results

if __name__ == "__main__":
    # Replace with your credentials
    HOST = "localhost"
    USER = "kavya"
    PASSWORD = "kavya"
    DATABASE = "placementdb"

    # Connect to MySQL
    conn = connect_to_database(HOST, USER, PASSWORD, DATABASE)

    # Create Database if it doesn't exist
    conn.cursor().execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE}")
    conn.commit()

    # Connect to the newly created database
    conn.database = DATABASE

    # Create schema and insert data
    create_schema_and_tables(conn)
    insert_dummy_data(conn)

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

    conn.close()
