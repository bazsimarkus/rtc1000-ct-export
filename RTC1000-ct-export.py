"""
RTC1000-ct-export
Script to analyze & export vectorized component tester output curves from Rohde & Schwarz RTC1000 oscilloscopes

How to use:
$ python3 RTC1000-ct-export.py {screenshot-file}

Example:
$ python3 RTC1000-ct-export.py RTC1000-ct-sample.png
"""

import numpy as np
import cv2
from skimage.morphology import skeletonize, binary_dilation
from matplotlib import pyplot as plt
import csv
import datetime
import sys

from scipy.spatial.distance import pdist, squareform
from matplotlib.collections import LineCollection


# ------------ EXTRACT VOLTAGE-CURRENT VALUES FROM IMAGE ------------

# Read the arguments
input_file = sys.argv[1]
original_img = cv2.imread(input_file)

# Define the upper left corner, and the square area size
upper_left_corner = [12, 12]
square_size = 454

# Cropping the image
original_img = original_img[upper_left_corner[0]:upper_left_corner[0]+square_size, upper_left_corner[1]:upper_left_corner[1]+square_size]

# Convert the BGR image to HSV colour space
hsv = cv2.cvtColor(original_img, cv2.COLOR_BGR2HSV)

# Set the lower and upper bounds for the green hue
lower = np.array([20, 90, 100])
upper = np.array([255, 255, 255])

# Create a mask for yellow colour using inRange function
mask = cv2.inRange(hsv, lower, upper)

# Perform bitwise and on the original image arrays using the mask
res = cv2.bitwise_and(original_img, original_img, mask=mask)
gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
th, dst = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY);
filtered_curve = dst

# Perform morphological operations to get the one-pixel thick curve
curve_skeleton = skeletonize(binary_dilation(filtered_curve))


# ------------ CSV GENERATION ------------

# Datetime object for the distinct result file name
now = datetime.datetime.now()
dt_string = now.strftime("%Y%m%dT%H%M%S")

# Write the header to the CSV file
output_filename = 'RTC1000-ct-measured-values-' + dt_string + '.csv'
with open(output_filename, 'a') as f:
    writer = csv.writer(f)
    writer.writerow(['Voltage [V]', 'Current [mA]'])

# Transpose and flip the image to ensure the increasing order of values in the exported CSV file
flipped_curve = np.flip(np.transpose(curve_skeleton), 1)

# Collect the current-volage value pairs
list_of_current_voltage_pairs = []
for current_count, current_slice in enumerate(flipped_curve):
    for voltage_count, voltage_slice in enumerate(current_slice):
        if voltage_slice == True:
            current_value = (current_count - square_size / 2) * (24 / square_size)
            voltage_value = (voltage_count - square_size / 2) * (24 / square_size)
            list_of_current_voltage_pairs.append([current_value, voltage_value])
            with open(output_filename, 'a') as f:
                writer = csv.writer(f)
                writer.writerow([current_value, voltage_value])


# ------------ PLOT CURVE ------------

# Connect the nearest neighbors of the points with a line
N = len(list_of_current_voltage_pairs)
X = np.array(list_of_current_voltage_pairs)
k = 3

# Matrix of pairwise Euclidean distances
distmat = squareform(pdist(X, 'euclidean'))

# Select the kNN for each datapoint
neighbors = np.sort(np.argsort(distmat, axis=1)[:, 0:k])

# Get edge coordinates
coordinates = np.zeros((N, k, 2, 2))
for i in np.arange(N):
    for j in np.arange(k):
        coordinates[i, j, :, 0] = np.array([X[i,:][0], X[neighbors[i, j], :][0]])
        coordinates[i, j, :, 1] = np.array([X[i,:][1], X[neighbors[i, j], :][1]])

# Create line artists
lines = LineCollection(coordinates.reshape((N*k, 2, 2)), color='black')

# Save plot
fig, ax = plt.subplots(1,1,figsize = (8, 8))
plt.grid()
ax.scatter(X[:,0], X[:,1], c='black', s=0)
ax.add_artist(lines)
plt.xlim([-12, 12])
plt.xlabel("Voltage [V]")
plt.xticks(np.arange(-12, 12, 2))
plt.ylim([-12, 12])
plt.ylabel("Current [mA]")
plt.yticks(np.arange(-12, 12, 2))
plt.savefig('RTC1000-ct-measured-values-' + dt_string + '.png')
