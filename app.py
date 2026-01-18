import streamlit as st
import sqlite3
from datetime import date

# Database connection
conn = sqlite3.connect("attendance.db", check_same_thread=False)
cur = conn.cursor()

# Create tables
cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    student_id INTEGER,
    date TEXT,
    status TEXT
)
""")
conn.commit()

st.title("🎓 Student Attendance Management System")

menu = st.sidebar.selectbox(
    "Menu",
    ["Add Student", "Mark Attendance", "View Attendance"]
)

# Add Student
if menu == "Add Student":
    st.subheader("Add New Student")
    name = st.text_input("Student Name")

    if st.button("Add"):
        cur.execute("INSERT INTO students (name) VALUES (?)", (name,))
        conn.commit()
        st.success("Student Added Successfully")

# Mark Attendance
elif menu == "Mark Attendance":
    st.subheader("Mark Attendance")

    cur.execute("SELECT * FROM students")
    students = cur.fetchall()

    for student in students:
        status = st.radio(
            student[1],
            ("Present", "Absent"),
            key=student[0]
        )

        if st.button(f"Save {student[1]}"):
            cur.execute(
                "INSERT INTO attendance VALUES (?, ?, ?)",
                (student[0], str(date.today()), status)
            )
            conn.commit()
            st.success(f"Attendance saved for {student[1]}")

# View Attendance
elif menu == "View Attendance":
    st.subheader("Attendance Records")

    cur.execute("""
    SELECT students.name, attendance.date, attendance.status
    FROM attendance
    JOIN students ON students.id = attendance.student_id
    """)
    data = cur.fetchall()

    st.table(data)
