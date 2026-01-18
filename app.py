import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# -------------------- LOGIN --------------------
def login():
    st.title("🔐 Teacher Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state["logged_in"] = True
            st.success("Login Successful")
        else:
            st.error("Invalid Username or Password")

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    login()
    st.stop()

# -------------------- DATABASE --------------------
conn = sqlite3.connect("attendance.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS students (
    roll INTEGER PRIMARY KEY,
    name TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    roll INTEGER,
    date TEXT,
    status TEXT
)
""")

conn.commit()

# -------------------- APP --------------------
st.title("🎓 Student Attendance Management System")

menu = st.sidebar.selectbox(
    "Menu",
    [
        "Add Student",
        "Mark Attendance",
        "View Attendance",
        "Monthly Report",
        "Export to Excel",
        "Logout"
    ]
)

# -------------------- ADD STUDENT --------------------
if menu == "Add Student":
    st.subheader("➕ Add Student")

    roll = st.number_input("Roll Number", min_value=1, step=1)
    name = st.text_input("Student Name")

    if st.button("Add Student"):
        if name.strip() == "":
            st.warning("Student name cannot be empty")
        else:
            try:
                cur.execute("INSERT INTO students VALUES (?, ?)", (roll, name))
                conn.commit()
                st.success("Student Added Successfully")
            except sqlite3.IntegrityError:
                st.error("Roll number already exists")

# -------------------- MARK ATTENDANCE --------------------
elif menu == "Mark Attendance":
    st.subheader("📝 Mark Attendance")

    cur.execute("SELECT * FROM students")
    students = cur.fetchall()

    if len(students) == 0:
        st.warning("No students found. Please add students first.")
    else:
        for student in students:
            status = st.radio(
                f"Roll {student[0]} - {student[1]}",
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

# -------------------- VIEW ATTENDANCE --------------------
elif menu == "View Attendance":
    st.subheader("📋 All Attendance Records")

    cur.execute("SELECT COUNT(*) FROM attendance")
    count = cur.fetchone()[0]

    if count == 0:
        st.warning("No attendance records found.")
    else:
        df = pd.read_sql_query("""
        SELECT students.roll, students.name, attendance.date, attendance.status
        FROM attendance
        JOIN students ON students.roll = attendance.roll
        """, conn)

        st.dataframe(df)

# -------------------- MONTHLY REPORT --------------------
elif menu == "Monthly Report":
    st.subheader("📅 Monthly Attendance Report")

    month = st.selectbox(
        "Select Month",
        ["01","02","03","04","05","06","07","08","09","10","11","12"]
    )

    cur.execute("SELECT COUNT(*) FROM attendance")
    count = cur.fetchone()[0]

    if count == 0:
        st.warning("No attendance data available.")
    else:
        df = pd.read_sql_query("""
        SELECT students.roll, students.name, attendance.date, attendance.status
        FROM attendance
        JOIN students ON students.roll = attendance.roll
        """, conn)

        df["month"] = df["date"].str[5:7]
        monthly_df = df[df["month"] == month]

        if len(monthly_df) == 0:
            st.info("No records found for this month.")
        else:
            st.dataframe(monthly_df)

# -------------------- EXPORT TO EXCEL --------------------
elif menu == "Export to Excel":
    st.subheader("⬇ Export Attendance to Excel")

    cur.execute("SELECT COUNT(*) FROM attendance")
    count = cur.fetchone()[0]

    if count == 0:
        st.warning("No data to export.")
    else:
        df = pd.read_sql_query("""
        SELECT students.roll, students.name, attendance.date, attendance.status
        FROM attendance
        JOIN students ON students.roll = attendance.roll
        """, conn)

        file_name = "attendance_report.xlsx"
        df.to_excel(file_name, index=False)

        with open(file_name, "rb") as f:
            st.download_button(
                label="Download Excel File",
                data=f,
                file_name=file_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# -------------------- LOGOUT --------------------
elif menu == "Logout":
    st.session_state["logged_in"] = False
    st.success("Logged out successfully")
    st.experimental_rerun()
