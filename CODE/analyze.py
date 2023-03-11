import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate

# Open the file from the data folder and read the data
def read_data(filename):
    data = np.loadtxt(filename, delimiter=",", skiprows=1)
    return data


fig = plt.figure()
ax = fig.add_subplot(projection="3d")

data = read_data("data/Platform_Test_1_002.csv")

results = np.empty((3,4))

output = np.empty((3, 7), dtype=object)
# Fill the output matrix with the max, min, and diff values
output[:, 0] = ["Max", "Min", "Diff"]

for i in range(0, 6):
    output[0, i+1] = np.max(data[:, i+2])
    output[1, i+1] = np.min(data[:, i+2])
    output[2, i+1] = np.max(data[:, i+2]) - np.min(data[:, i+2])

print(tabulate(output, headers=["Roll", "Pitch", "Yaw", "X", "Y", "Z"], tablefmt="fancy_grid"))

# Plot the data

ax.scatter(data[:, 5], data[:, 6], data[:, 7], marker="o", color="red")

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")

plt.show()

# Plot the roll data as a function of time
plt.plot(data[:, 0], abs(data[:, 2] - np.max(data[:,2])), color="red")
plt.xlabel("Time (ms)")
plt.ylabel("Roll (deg)")
plt.savefig("data/roll.png")

# Plot the pitch data as a function of time
plt.plot(data[:, 0], abs(data[:, 3] - np.max(data[:,3])), color="green")
plt.xlabel("Time (ms)")
plt.ylabel("Pitch (deg)")
plt.savefig("data/pitch.png")

# Plot the yaw data as a function of time
plt.plot(data[:, 0], abs(data[:, 4] - np.max(data[:,4])), color="blue")
plt.xlabel("Time (ms)")
plt.ylabel("Yaw (deg)")
plt.savefig("data/yaw.png")

