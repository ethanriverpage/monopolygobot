import json

# Read data from "mgb_bot2_game_data.json"
with open("mgb_bot2_game_data.json", "r") as file:
    data = json.load(file)

# Calculate the total cost for each board
total_costs = []
for board in data:
    print(board)
    total_cost = sum(
        sum(building) for building in board.values() if isinstance(building, list)
    )
    total_costs.append(total_cost)

# Calculate the factors between consecutive total costs
factors = []
for i in range(1, len(total_costs)):
    factor = total_costs[i] / total_costs[i - 1]
    factors.append(factor)

# Print the results
for i, board in enumerate(data):
    print(
        f"Board {board['board_number']} ({board['board_name']}): Total Cost = {total_costs[i]:,.2f}"
    )

for i, factor in enumerate(factors):
    print(
        f"Factor between Board {data[i]['board_number']} and Board {data[i+1]['board_number']} = {factor:.2f}"
    )
