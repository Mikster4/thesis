import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate

# Open the file from the data folder and read the data
def read_data(filename):
    data = np.loadtxt(filename, delimiter=",", skiprows=1)
    return data


fig = plt.figure()
ax = fig.add_subplot(projection="3d")

data = read_data("data/Test_Max_Roll.csv")

results = np.empty((3,4))

output = np.empty((3, 7), dtype=object)
# Fill the output matrix with the max, min, and diff values
output[:, 0] = ["Max", "Min", "Diff"]

for i in range(0, 6):
    output[0, i+1] = np.max(data[:, i+2])
    output[1, i+1] = np.min(data[:, i+2])
    output[2, i+1] = np.max(data[:, i+2]) - np.min(data[:, i+2])

print(tabulate(output, headers=["Roll", "Pitch", "Yaw", "X", "Y", "Z"], tablefmt="github"))

# Plot the data

ax.scatter(data[:, 5], data[:, 6], abs(data[:, 7]), marker="o", color="red")

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")

plt.show()

# Plot the roll data as a function of time
plt.plot(data[:, 1], data[:, 2], color="red")

# Plot the pitch data as a function of time
plt.plot(data[:, 1], data[:, 3], color="green")

# Plot the yaw data as a function of time
plt.plot(data[:, 1], data[:, 4], color="blue")

plt.xlabel("Time (ms)")
plt.ylabel("Rotation (deg)")
plt.savefig("data/combined_rotation.png")
plt.legend(["Roll", "Pitch", "Yaw"])
plt.show()
plt.clf()

# Plot the relative roll data as a function of time
plt.plot(data[:, 1], abs(data[:, 2] - np.mean(data[0:100, 2])), color="red")
plt.plot(data[:, 1], abs(data[:, 3] - np.mean(data[0:100, 3])), color="green")
plt.plot(data[:, 1], abs(data[:, 4] - np.mean(data[0:100, 4])), color="blue")
plt.legend(["Roll", "Pitch", "Yaw"])
plt.xlabel("Time (ms)")
plt.ylabel("Rotation (deg)")
#plt.savefig("data/combined_rotation_relative.png")
plt.show()



# plt.plot(data[:, 0], abs(data[:, 2] - np.max(data[:,2])), color="red")