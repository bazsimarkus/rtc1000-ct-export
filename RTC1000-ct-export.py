"""
RTC1000-ct-export
Script to analyze & export vectorized component tester output curves from Rohde & Schwarz RTC1000 oscilloscopes
"""

import numpy as np
import cv2
from skimage.measure import approximate_polygon, find_contours

original_img = cv2.imread('RTC1000-ct-sample.png')

print(original_img.shape)

# Cropping the image
original_img = original_img[12:466, 12:466]

# Convert the BGR image to HSV colour space
hsv = cv2.cvtColor(original_img, cv2.COLOR_BGR2HSV)

# Set the lower and upper bounds for the green hue
lower = np.array([22, 93, 0])
upper = np.array([45, 255, 255])

# Create a mask for yellow colour using inRange function
mask = cv2.inRange(hsv, lower, upper)

# Perform bitwise and on the original image arrays using the mask
res = cv2.bitwise_and(original_img, original_img, mask=mask)

gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)

th, dst = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY);

# Create the filtered curve
filtered_curve = cv2.bitwise_not(dst)

# Vectorization
contours = find_contours(filtered_curve, 0)

result_contour = np.zeros(filtered_curve.shape + (3,), np.uint8)
result_polygon1 = np.zeros(filtered_curve.shape + (3,), np.uint8)
result_polygon2 = np.zeros(filtered_curve.shape + (3,), np.uint8)

for contour in contours:
    print('Contour shape:', contour.shape)

    # Reduce the number of lines by approximating polygons
    polygon1 = approximate_polygon(contour, tolerance=2.5)
    print('Polygon 1 shape:', polygon1.shape)

    # Increase tolerance to further reduce number of lines
    polygon2 = approximate_polygon(contour, tolerance=15)
    print('Polygon 2 shape:', polygon2.shape)

    contour = contour.astype(np.int).tolist()
    polygon1 = polygon1.astype(np.int).tolist()
    polygon2 = polygon2.astype(np.int).tolist()

    # Draw contour lines
    for idx, coords in enumerate(contour[:-1]):
        y1, x1, y2, x2 = coords + contour[idx + 1]
        result_contour = cv2.line(result_contour, (x1, y1), (x2, y2),
                                  (0, 255, 0), 1)
    # Draw polygon 1 lines
    for idx, coords in enumerate(polygon1[:-1]):
        y1, x1, y2, x2 = coords + polygon1[idx + 1]
        result_polygon1 = cv2.line(result_polygon1, (x1, y1), (x2, y2),
                                   (0, 255, 0), 1)
    # Draw polygon 2 lines
    for idx, coords in enumerate(polygon2[:-1]):
        y1, x1, y2, x2 = coords + polygon2[idx + 1]
        result_polygon2 = cv2.line(result_polygon2, (x1, y1), (x2, y2),
                                   (0, 255, 0), 1)

# Display the images

cv2.namedWindow("filtered_curve", cv2.WINDOW_NORMAL)
cv2.imshow("filtered_curve", filtered_curve)

cv2.namedWindow("result_contour", cv2.WINDOW_NORMAL)
cv2.imshow("result_contour", result_contour)

cv2.namedWindow("result_polygon1", cv2.WINDOW_NORMAL)
cv2.imshow("result_polygon1", result_polygon1)

cv2.namedWindow("result_polygon2", cv2.WINDOW_NORMAL)
cv2.imshow("result_polygon2", result_polygon2)

if cv2.waitKey(0):
    cv2.destroyAllWindows()
