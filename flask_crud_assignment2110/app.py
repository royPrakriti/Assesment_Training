from flask import Flask
from flask import jsonify,request



app = Flask(__name__)




students = [
{
"id": 1,
"name": "Rhea Kapoor",
"course": "Python",
"score": 82
},
{
"id": 2,
"name": "Zain Malik",
"course": "SQL",
"score": 76
},
{
"id": 3,
"name": "Devika Rao",
"course": "Cloud",
"score": 91
}
]

@app.route("/students",
methods = ["GET"])
def get_students():
    return jsonify(students)


@app.route("/students/<int:id>",
methods = ["GET"])
def get_student(id):
    for student in students:
        if student["id"] == id:
            return jsonify(student)


    return jsonify({"message": "Student not found"}),404

@app.route("/students",
methods = ["POST"])
def add_student():
    data = request.get_json()
    students.append(data)

    return jsonify({"message": "Student added"},
                   {"student" : data}), 201

@app.route("/students/<int:id>",methods = ["PUT"])
def update_student(id):
    data = request.get_json()
    for student in students:
        if student["id"] == id:
            student.update(data)
            return jsonify({"message": "Student updated"}),200
    return jsonify({"message": "Student not found"}),404

@app.route("/students/delete/<int:id>",
methods = ['DELETE'])
def delete_student(id):
    for student in students:
        if student["id"] == id:
            students.remove(student)

            return jsonify({"message": "Student deleted"})

    return jsonify({"message": "Student not found"}),404

if __name__ == '__main__':
    app.run(debug=True)

