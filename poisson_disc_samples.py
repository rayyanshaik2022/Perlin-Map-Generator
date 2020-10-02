from random import random
from math import cos, sin, floor, sqrt, pi, ceil


def euclidean_distance(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return sqrt(dx * dx + dy * dy)


def poisson_disc_samples(width, height, r_max, r_min, k=3, r_array=[], distance=euclidean_distance, random=random):
    tau = 2 * pi
    cellsize = r_max / sqrt(2)

    grid_width = int(ceil(width / cellsize))
    grid_height = int(ceil(height / cellsize))
    grid = [None] * (grid_width * grid_height)

    def grid_coords(p):
        return int(floor(p[0] / cellsize)), int(floor(p[1] / cellsize))

    def fits(p, gx, gy, r):
        yrange = list(range(max(gy - 2, 0), min(gy + 3, grid_height)))
        for x in range(max(gx - 2, 0), min(gx + 3, grid_width)):
            for y in yrange:
                g = grid[x + y * grid_width]
                if g is None:
                    continue

                r = r_array[int(floor(g[0]))][int(floor(g[1]))]
                if distance(p, g) <= r:  # too close
                    return False
        return True

    p = width * random(), height * random()
    queue = [p]
    grid_x, grid_y = grid_coords(p)
    grid[grid_x + grid_y * grid_width] = p

    z_max = width * height * 8
    z = 0

    while queue:
        qindex = int(random() * len(queue))  # select random point from queue
        qx, qy = queue.pop(qindex)
        r = r_array[int(floor(qx))][int(floor(qy))]
        # print('min_dist:', r)

        z += 1
        if z > z_max:
            print('max iteration exceeded')
            break

        for _ in range(k):
            alpha = tau * random()
            d = r * sqrt(3 * random() + 1)
            px = qx + d * cos(alpha)
            py = qy + d * sin(alpha)

            if not (0 <= px < width and 0 <= py < height):
                continue

            p = (px, py)
            grid_x, grid_y = grid_coords(p)
            if not fits(p, grid_x, grid_y, r):
                continue
            queue.append(p)
            grid[grid_x + grid_y * grid_width] = p
    return [p for p in grid if p is not None]