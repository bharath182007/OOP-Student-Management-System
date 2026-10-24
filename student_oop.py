
import json
import os


# ---------- Student Class ----------

class Student:
    PASS_MARK = 40

    def __init__(self, student_id, name, department,
                 marks, attendance, status="Active"):
        if not student_id.strip():
            raise ValueError("Student ID cannot be empty.")
        if not name.strip():
            raise ValueError("Student name cannot be empty.")
        if not department.strip():
            raise ValueError("Department cannot be empty.")

        self.student_id = student_id.strip()
        self.name = name.strip()
        self.department = department.strip()
        self.status = status
        self.update_marks(marks)
        self.update_attendance(attendance)

    def update_marks(self, marks):
        try:
            marks = [float(mark) for mark in marks]
        except (TypeError, ValueError):
            raise ValueError("Marks must be valid numbers.")

        if not marks or any(not 0 <= mark <= 100 for mark in marks):
            raise ValueError("Marks must be between 0 and 100.")

        self.marks = marks

    def update_attendance(self, attendance):
        try:
            attendance = float(attendance)
        except (TypeError, ValueError):
            raise ValueError("Attendance must be a number.")

        if not 0 <= attendance <= 100:
            raise ValueError("Attendance must be between 0 and 100.")

        self.attendance = attendance

    @property
    def average(self):
        return sum(self.marks) / len(self.marks)

    @property
    def result(self):
        return (
            "PASS"
            if all(mark >= self.PASS_MARK for mark in self.marks)
            else "FAIL"
        )

    @property
    def performance(self):
        if self.average >= 75:
            return "Excellent"
        elif self.average >= 60:
            return "Good"
        elif self.average >= 40:
            return "Average"
        return "Needs Improvement"

    def to_dict(self):
        return {
            "student_id": self.student_id,
            "name": self.name,
            "department": self.department,
            "marks": self.marks,
            "attendance": self.attendance,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["student_id"],
            data["name"],
            data["department"],
            data["marks"],
            data["attendance"],
            data.get("status", "Active")
        )


# ---------- File Manager Class ----------

class FileManager:
    def __init__(self, filename="student_records.json"):
        self.filename = filename

    def save(self, students):
        temporary_file = self.filename + ".tmp"

        try:
            with open(temporary_file, "w", encoding="utf-8") as file:
                json.dump(
                    [student.to_dict() for student in students],
                    file,
                    indent=4
                )

            os.replace(temporary_file, self.filename)
            return True

        except (OSError, TypeError, ValueError) as error:
            print(f"Error saving records: {error}")

            try:
                if os.path.exists(temporary_file):
                    os.remove(temporary_file)
            except OSError:
                pass

            return False

    def load(self):
        if not os.path.exists(self.filename):
            return []

        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, list):
                raise ValueError("The file must contain a list of students.")

            students = []
            seen_ids = set()

            for record in data:
                if not isinstance(record, dict):
                    raise ValueError("Invalid student record.")

                student = Student.from_dict(record)
                key = student.student_id.casefold()

                if key in seen_ids:
                    raise ValueError("Duplicate student ID in file.")

                seen_ids.add(key)
                students.append(student)

            return students

        except (OSError, json.JSONDecodeError, ValueError,
                TypeError, KeyError) as error:
            print(f"Error loading records: {error}")
            return []


# ---------- Student Manager Class ----------

class StudentManager:
    def __init__(self, file_manager):
        self.file_manager = file_manager
        self.students = file_manager.load()

    def find_student(self, student_id):
        for student in self.students:
            if student.student_id.casefold() == student_id.casefold():
                return student
        return None

    def add_student(self, student):
        if self.find_student(student.student_id):
            raise ValueError("Student ID already exists.")

        self.students.append(student)

        if not self.file_manager.save(self.students):
            self.students.pop()
            raise OSError("Could not save the new student.")

        print("Student added successfully.")

    def search_student(self, student_id):
        student = self.find_student(student_id)

        if student is None:
            raise LookupError("Student not found.")

        return student

    def update_student(self, student_id, name=None,
                       department=None, marks=None,
                       attendance=None):
        student = self.search_student(student_id)
        old_data = student.to_dict()

        try:
            if name is not None:
                if not name.strip():
                    raise ValueError("Name cannot be empty.")
                student.name = name.strip()

            if department is not None:
                if not department.strip():
                    raise ValueError("Department cannot be empty.")
                student.department = department.strip()

            if marks is not None:
                student.update_marks(marks)

            if attendance is not None:
                student.update_attendance(attendance)

            if not self.file_manager.save(self.students):
                raise OSError("Could not save updated records.")

        except (ValueError, OSError):
            # Restore the original information if updating fails.
            student.name = old_data["name"]
            student.department = old_data["department"]
            student.marks = old_data["marks"]
            student.attendance = old_data["attendance"]
            student.status = old_data["status"]
            raise

        print("Student updated successfully.")

    def delete_student(self, student_id):
        student = self.search_student(student_id)
        index = self.students.index(student)
        self.students.pop(index)

        if not self.file_manager.save(self.students):
            self.students.insert(index, student)
            raise OSError("Could not save deletion.")

        print("Student deleted successfully.")


# ---------- Report Generator Class ----------

class ReportGenerator:
    @staticmethod
    def student_report(student):
        print("\nStudent Report")
        print("-" * 30)
        print(
            f"{student.student_id} | "
            f"{student.name} | {student.department}"
        )
        print(f"Average: {student.average:.1f}%")
        print(f"Attendance: {student.attendance:.1f}%")
        print(f"Status: {student.status}")
        print(f"Performance: {student.performance}")
        print(f"Result: {student.result}")

    @staticmethod
    def class_report(students):
        print("\nClass Performance Report")
        print("-" * 30)
        print(f"Total Students: {len(students)}")

        all_marks = [
            mark for student in students
            for mark in student.marks
        ]

        if not all_marks:
            print("No marks available.")
            return

        print(f"Average Class Mark: {sum(all_marks) / len(all_marks):.1f}")

        top_student = max(students, key=lambda s: s.average)
        print(
            f"Top Performer: {top_student.name} "
            f"({top_student.average:.1f}%)"
        )

        print("\nIndividual Results:")
        for student in students:
            print(
                f"{student.student_id} | {student.name} | "
                f"{student.average:.1f}% | {student.result}"
            )


# ---------- User Interface ----------

def read_marks():
    text = input("Marks (comma-separated): ")
    try:
        marks = [float(item.strip()) for item in text.split(",")]
        if not marks or any(not 0 <= mark <= 100 for mark in marks):
            raise ValueError
        return marks
    except ValueError:
        raise ValueError("Enter valid marks from 0 to 100, e.g. 78,85,72.")


def add_student_ui(manager):
    student = Student(
        input("Student ID: "),
        input("Name: "),
        input("Department: "),
        read_marks(),
        float(input("Attendance (%): "))
    )
    manager.add_student(student)


def update_student_ui(manager):
    student_id = input("Student ID to update: ").strip()
    manager.search_student(student_id)

    name = input("New name (blank to keep): ").strip()
    department = input("New department (blank to keep): ").strip()
    marks_text = input("New marks (blank to keep): ").strip()
    attendance_text = input("New attendance (blank to keep): ").strip()

    marks = None
    attendance = None

    if marks_text:
        marks = [
            float(item.strip())
            for item in marks_text.split(",")
        ]

    if attendance_text:
        attendance = float(attendance_text)

    manager.update_student(
        student_id,
        name=name or None,
        department=department or None,
        marks=marks,
        attendance=attendance
    )


def main():
    file_manager = FileManager()
    manager = StudentManager(file_manager)
    reports = ReportGenerator()

    while True:
        print("""
===== Student Management System =====
1. Add Student
2. View Students
3. Search Student
4. Update Student
5. Delete Student
6. Performance Report
7. Exit
""")

        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                add_student_ui(manager)

            elif choice == "2":
                if not manager.students:
                    print("No student records found.")
                else:
                    for student in manager.students:
                        reports.student_report(student)

            elif choice == "3":
                student_id = input("Enter student ID: ").strip()
                student = manager.search_student(student_id)
                reports.student_report(student)

            elif choice == "4":
                update_student_ui(manager)

            elif choice == "5":
                student_id = input("Student ID to delete: ").strip()
                manager.delete_student(student_id)

            elif choice == "6":
                reports.class_report(manager.students)

            elif choice == "7":
                print("Exiting Student Management System.")
                break

            else:
                print("Invalid option. Choose from 1 to 7.")

        except (ValueError, LookupError, OSError) as error:
            print(f"Operation failed: {error}")
        except (TypeError, IndexError) as error:
            print(f"Invalid input or operation: {error}")


if __name__ == "__main__":
    main()
