


class Console:
    def __init__(self):
        pass

    def stdout(self, message):
        print(message)


    def in_line(self):
        for i in range(10):
            print(f"Progress: {i+1}/10", end='\r')


    
