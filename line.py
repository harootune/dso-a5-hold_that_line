from typing import Tuple, Union, List
import decimal
from decimal import Decimal


class Line:

    decimal.getcontext().prec = 7

    def __init__(self, start, end):
        if start == end:
            raise ValueError(f'Invalid constructors {start}, {end}. Cannot model a zero-dimensional figure.')

        self.horizontal = False
        self.vertical = False
        self.start = start
        self.end = end

        self._set_slope()
        self._set_y_intercept()

    def _set_slope(self):
        step = (Decimal(self.end[0] - self.start[0]), Decimal(self.end[1] - self.start[1]))

        if step[0] == 0:
            self.horizontal = True
            self.slope = 0
        elif step[1] == 0:
            self.vertical = True
            self.slope = float('inf')
        else:
            self.slope = step[0] / step[1]

    def _set_y_intercept(self):
        if self.vertical:
            y_intercept = None
        elif self.horizontal:
            y_intercept = self.start[0]
        else:
            y_intercept = self.start[0] - (self.slope * self.start[1])

        self.y_intercept = y_intercept

    def check_intersection(self, other) -> bool:
        if self.slope == other.slope:
            check = False
            if self.vertical and other.vertical:
                if self.start[1] == other.start[1]:
                    check = True
            elif self.y_intercept == other.y_intercept:
                check = True

            if check:
                validators = [self.is_on_segment(other.start),
                              self.is_on_segment(other.end) and not self.start == other.end,
                              other.is_on_segment(self.start) and not self.start == other.end,
                              other.is_on_segment(self.end)]

                return any(validators)
            else:
                return False

        else:
            if self.vertical or other.vertical:
                vert = self if self.vertical else other
                non_vert = self if vert == other else other
                intersect_x = vert.start[1]
                intersect_y = (non_vert.slope * intersect_x) + non_vert.y_intercept
            else:
                m = self.slope - other.slope
                b = other.y_intercept - self.y_intercept
                intersect_x = b / m
                intersect_y = (self.slope * intersect_x) + self.y_intercept

            coord = (intersect_y, intersect_x)
            if coord == self.start == other.end:
                return False
            else:
                return self.is_on_segment(coord) and other.is_on_segment(coord)

    def is_on_segment(self, coord):
        lower_x = min(self.start[1], self.end[1])
        upper_x = max(self.start[1], self.end[1])
        lower_y = min(self.start[0], self.end[0])
        upper_y = max(self.start[0], self.end[0])

        return lower_y <= coord[0] <= upper_y and lower_x <= coord[1] <= upper_x


if __name__ == '__main__':
    a = Line((0, 0), (0, 2))
    b = Line((0, 2), (0, 0))
    print(b.check_intersection(a))