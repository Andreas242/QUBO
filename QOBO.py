import itertools

stations = ['S1', 'S2', 'S3', 'S4', 'S5']
trains = ['T1', 'T2']
tracks = {
    ('S1', 'S2'): 10,
    ('S2', 'S3'): 7,
    ('S3', 'S4'): 9,
    ('S4', 'S5'): 3,

}

# Redefine QUBO
QUBO = {}

train_schedules = {
    'T1': ['S1', 'S2', 'S3', 'S4'],  # Example schedule for train T1
    'T2': ['S2', 'S3', 'S4', 'S5']   # Example schedule for train T2
}
# Correct Binary Variables
binary_vars = {
    (station, next_station, train, t): f'x_{station}_{next_station}_{train}_{t}'
    for train in trains
    for t, station in enumerate(stations)  # include all stations, not just up to the last
    for next_station in stations  # include all possible next stations
    if (station, next_station) in tracks  # only include valid tracks
}


# Objective Function: Minimize total travel time
for key in binary_vars:
    station, next_station, train, t = key
    if (station, next_station) in tracks:
        QUBO[(key, key)] = -tracks[(station, next_station)]  # Minimize travel time with a negative weight
print (QUBO);
for train, schedule in train_schedules.items():
    for t in range(len(schedule) - 1):
        station_from = schedule[t]
        station_to = schedule[t + 1]
        for delay in range(t + 1):  # Apply increasing penalties for delays in start
            key = (station, next_station, train, delay)
            print("key");
            print(key);
            print (binary_vars);
            if key in binary_vars:
                print(key);
                QUBO[(binary_vars[key], binary_vars[key])] += 5 * delay  # Smaller penalty for starting on time
print(QUBO);

# Cross-train synchronization incentives
for time in range(len(stations) - 1):
    for train1 in trains:
        for train2 in trains:
            if train1 != train2:
                for seg1, seg2 in zip(train_schedules[train1], train_schedules[train2]):
                    if (seg1, seg2, time) in tracks and (seg2, seg1, time) in tracks:
                        var1 = f'x_{seg1}_{seg2}_{train1}_{time}'
                        var2 = f'x_{seg2}_{seg1}_{train2}_{time}'
                        if var1 in binary_vars and var2 in binary_vars:
                            # Minor incentive for moving together
                            QUBO[(binary_vars[var1], binary_vars[var2])] -= 2
                            QUBO[(binary_vars[var2], binary_vars[var1])] -= 2
# Adjust penalties for non-compliance with train schedules
for train, schedule in train_schedules.items():
    for t in range(len(schedule) - 1):
        station = schedule[t]
        next_station = schedule[t + 1]
        key = (station, next_station, train, t)
        print(key);
        if key in binary_vars:
            QUBO[(key, key)] = QUBO.get((key, key), 0) - 20  # Increased incentive # Strong incentive to follow the schedule
        # Add penalties for incorrect paths directly here, if needed

# Penalize conflicts between trains at each track segment
for t in range(len(stations) - 1):
    for i in tracks:
        for j1 in trains:
            for j2 in trains:
                if j1 != j2:
                    key1 = (stations[t], stations[t+1], j1, t)
                    key2 = (stations[t], stations[t+1], j2, t)
                    if key1 in binary_vars and key2 in binary_vars:
                        QUBO[(key1, key2)] = 100  # large penalty for train conflicts

# Station visit constraint
for train in trains:
    for t, station in enumerate(train_schedules[train]):
        key = (station, train_schedules[train][t+1] if t+1 < len(train_schedules[train]) else None, train, t)
        if key in binary_vars:
            QUBO[(key, key)] = QUBO.get((key, key), 0) - 10  # incentive to visit each station as per schedule

print(QUBO)

print("QUBO successfully constructed.")




def evaluate_qubo(QUBO, assignment):
    """Calculate the energy of a given assignment for a QUBO."""
    energy = 0
    for (var1, var2), weight in QUBO.items():
        energy += weight * assignment[var1] * assignment[var2]
    return energy

# Assuming binary_vars is a list of your variable names
# binary_vars = [('S1', 'S2', 'T1', 0)]  # Add other variables as needed


# Generate all possible combinations of variable assignments
all_possible_assignments = list(itertools.product([0, 1], repeat=len(binary_vars)))

# Evaluate all possible assignments
best_energy = float('inf')
best_assignment = None

for assignment in all_possible_assignments:
    current_assignment = {var: value for var, value in zip(binary_vars.keys(), assignment)}
    current_energy = evaluate_qubo(QUBO, current_assignment)
    if current_energy < best_energy:
        best_energy = current_energy
        best_assignment = current_assignment

# Output the best solution found
print("Best Energy:", best_energy)
print("Best Assignment:", best_assignment)