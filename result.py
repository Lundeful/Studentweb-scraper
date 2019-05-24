class Result:

    def __init__(self, semester, name, code, grade):
        self.semester = semester
        self.name = name
        self.code = code
        self.grade = grade

    def __str__(self):
        return self.name + "\n" + self.code + "\n" + self.semester + "\n" + self.grade
