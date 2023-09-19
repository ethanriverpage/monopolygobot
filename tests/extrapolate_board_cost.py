# Input: Initial value for board16
board16 = float(input("Enter the initial value for board16: "))

# Input: Number of boards to calculate
num_boards = int(input("Enter the number of boards to calculate: "))

result = board16

for n in range(16, 16 + num_boards):
    result *= (n + 1) / n
    print(f"Value for board{n + 1}: {result}")
