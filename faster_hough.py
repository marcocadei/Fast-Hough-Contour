import cv2
import numpy as np
import sys
from os.path import splitext


def crop(image, r, c, height, width):
    return image[r:r+height, c:c+width]


def moore_neighbor_tracing(image, accumulator, maxr):
    color = 100
    original_height, original_width = image.shape
    image = np.pad(image, ((1, 1), (1, 1)), 'constant', constant_values=(255, 255))
    height, width = image.shape
    contour_pixels = []
    p = (0, 0)
    c = (0, 0)
    s = (0, 0)
    previous = (0, 0)
    found = False

    # Find the first point
    for i in range(height):
        for j in range(width):
            if image[i, j] <= color and not (i == 0 and j == 0):
                s = (i, j)
                # contour_pixels.append(s)
                contour_pixels.append((s[0]-1, s[1]-1))
                p = s
                found = True
                break
            if not found:
                previous = (i, j)
        if found:
            break

    # If the pixel is isolated i don't do anything
    isolated = True
    m = moore_neighbor(p)
    for r, c in m:
        if image[r, c] <= color:
            isolated = False

    if not isolated:
        tmp = c
        # Backtrack and next clockwise M(p)
        c = next_neighbor(s, previous)
        previous = tmp
        while c != s:
            if image[c] <= color:
                previous_contour = contour_pixels[len(contour_pixels) - 1]

                # contour_pixels.append(c)
                contour_pixels.append((c[0]-1, c[1]-1))
                p = c
                c = previous

                # HERE is where i have to start checking for lines
                # i get the previous contour pixel
                current_contour = p[0] - 1, p[1] - 1

                # i have to calculate t (between 0 and 179) of the line that connects the two pixel
                t = np.arctan2(previous_contour[1]-current_contour[1], previous_contour[0]-current_contour[0]) * 180 / np.pi
                t = int(np.round(t))
                if t < 0:
                    t += 180
                t %= 180

                # This is the "classic" Hough in which we consider only a subset of all the possible lines
                for t in range(t-30, t+31):
                    if t >= 180:
                        t = 180 - t
                    if t < 0:
                        t = 180 + t
                    rad = np.deg2rad(t)

                    r = current_contour[0] * np.sin(rad) + current_contour[1] * np.cos(rad) + maxr
                    accumulator[int(np.round(r)), t] += 1

            else:
                previous = c
                c = next_neighbor(p, c)

        image = crop(image, 1, 1, original_height, original_width)
    return contour_pixels


def moore_neighbor(pixel):
    row, col = pixel
    return ((row - 1, col - 1), (row - 1, col), (row - 1, col + 1),
            (row, col + 1), (row + 1, col + 1),
            (row + 1, col), (row + 1, col - 1),
            (row, col - 1))


def next_neighbor(central, neighbor):
    neighbors = moore_neighbor(central)
    index = np.where((np.array(neighbors) == neighbor).all(axis=1))[0][0]
    index += 1
    index = index % 8

    # Problem operating like this:
    # if the object of which i want to detect contours starts at the edges of the image there's the possibility
    # of going out of bounds
    return neighbors[index]


# Function that "deletes" an object using the information about its contours
def delete_object(image, contoured, contours):
    # With the edge pixel i also delete its moore neighborhood because otherwise if and edge is 2 pixel thick
    # because i find only the external contour i wouldn't delete the contour completely
    height, width = image.shape
    for x, y in contours:
        image[x, y] = 255
        image[np.clip(x - 1, 0, height - 1), np.clip(y - 1, 0, width - 1)] = 255
        image[np.clip(x - 1, 0, height - 1), y] = 255
        image[np.clip(x - 1, 0, height - 1), np.clip(y + 1, 0, width - 1)] = 255
        image[x, np.clip(y - 1, 0, width - 1)] = 255
        image[x, y] = 255
        image[x, np.clip(y + 1, 0, width - 1)] = 255
        image[np.clip(x + 1, 0, height - 1), np.clip(y - 1, 0, width - 1)] = 255
        image[np.clip(x + 1, 0, height - 1), y] = 255
        image[np.clip(x + 1, 0, height - 1), np.clip(y + 1, 0, width - 1)] = 255

    return image


# INPUT PARAMETER: a binarized image (using Canny edge) in which the contours are black and the background is white
# OUTPUT PARAMETER: an image with black background and white contours for all the objects identified and red lines
#                   where they are found
def main():
    if len(sys.argv) > 1:
        # Used later to save the image
        image_basename = splitext(sys.argv[1])[0]
        img_format = splitext(sys.argv[1])[1]

        # Load the image
        image = cv2.imread(sys.argv[1], 0)
        contour_all = np.zeros(image.shape, np.uint8)

        height, width = image.shape
        # Variables used to perform hough
        maxr = int(np.ceil(np.sqrt(np.power(height, 2) + np.power(width, 2))))
        accumulator = np.zeros((maxr * 2 + 1, 180), np.uint32)

        # I iterate until there are no more edge pixels
        # I keep tracing contours updating the accumulator matrix
        # delete the contour found and repeat
        while np.any(image <= 100):
            contoured = np.zeros(image.shape, np.uint8)
            contours = moore_neighbor_tracing(image, accumulator, maxr)
            for x, y in contours:
                contoured[x, y] = 255
                contour_all[x, y] = 255
            delete_object(image, contoured, contours)

        cv2.imshow("", contour_all)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        cv2.imwrite(image_basename + "_contoured" + img_format, contour_all)

        # Draw the lines i find in the accumulator matrix
        tmp = np.array(contour_all)
        tmp = cv2.merge((tmp, tmp, tmp))
        t = 100
        for i, j in np.argwhere(accumulator > t):
            rad = np.deg2rad(j)
            a = np.cos(rad)
            b = np.sin(rad)
            # This is needed because debugging i saw that a or b could go something like 1e-17 which is 0
            # but if i don't set it manually to 0, due to approximation errors i could get that the two points
            # of an horizontal line have two y that differs by one unit and so the line is not perfectly horizontal
            # (it happened with the sudoku image, for example)
            if 0 < a < 1e-10:
                a = 0
            if 0 < b < 1e-10:
                b = 0
            x0 = a * (i - maxr)
            y0 = b * (i - maxr)
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))
            cv2.line(tmp, (x1, y1), (x2, y2), (0, 0, 255), thickness=1)

        # Post processing: i delete red lines where there is not a white line beneath
        height, width = image.shape
        for i in range(height):
            for j in range(width):
                # if a pixel is red i check if it is correct, otherwise i set it to black
                # to check if it is correct i look if under it there are white pixels in the moor neighborhood
                if tmp[i, j, 2] == 255:
                    mn = moore_neighbor((i, j))
                    mn = np.array(mn)
                    rows = np.clip(mn[:, 0], 0, height-1)
                    columns = np.clip(mn[:, 1], 0, width-1)
                    colored_neighbor = np.any(contour_all[(rows, columns)] >= 200)
                    if contour_all[i, j] <= 100 and not colored_neighbor:
                        tmp[i, j, 2] = 0

        cv2.imshow("", tmp)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        cv2.imwrite(image_basename + "_houghed2" + img_format, tmp)

    else:
        print("Not enough input arguments")


if __name__ == "__main__":
    main()
