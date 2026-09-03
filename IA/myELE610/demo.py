

class person():
    def __init__(self, age , height, name):
        self.age = age
        self.height = height
        self.name = name

    def introduce(self):
        print(f"{self.name} is {self.age} years old")

viljar  = person(24, 140, "Viljar Normann")


class child(person):
    def __init__(self, age, height, name):
        super().__init__(age, height,name)
    
    def of_age(self):
        if self.age > 18:
            print(True)
        else:
            print(False)



viljar.introduce()

print(viljar.height)


hakon = child(14, 150, "Hakon Hauge")
hakon.of_age()
hakon.introduce()

