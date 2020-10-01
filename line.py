# stdlib
import fractions
from typing import Tuple


class Line:
    """Models a line segment on the Hold-That-Line board and supports some basic linear algebraic operations"""

    def __init__(self, start, end):
        # We don't want to model a point
        if start == end:
            raise ValueError(f'Invalid constructors {start}, {end}. Cannot model a zero-dimensional figure.')

        # set some defaults
        self.horizontal = False
        self.vertical = False
        self.start = start
        self.end = end

        # set more values and modify others based on start and end
        self._set_slope()
        self._set_y_intercept()

    def _set_slope(self) -> None:
        """
        Determines if a line segment is horizontal or vertical, and assigns an appropriate slope value regardless

        :return: None
        """
        # Figure out the horizontal and vertical distance between our starting and ending points
        step = (self.end[0] - self.start[0], self.end[1] - self.start[1])

        # if no vertical movement, its horizontal
        if step[0] == 0:
            self.horizontal = True
            self.slope = 0
        # if no horizontal distance, its vertical
        elif step[1] == 0:
            self.vertical = True
            self.slope = float('inf')
        # typical case
        else:
            self.slope = fractions.Fraction(step[0], step[1])  # we're doing rational arithmetic

    def _set_y_intercept(self) -> None:
        """
        Finds and sets the y intercept based on slope and the start and end points.

        :return: None
        """
        # vertical lines have no y intercepts
        if self.vertical:
            y_intercept = None
        # horizontal lines extend outward from their y intercepts
        elif self.horizontal:
            y_intercept = self.start[0]
        # y = mx + b hell yeah
        else:
            y_intercept = self.start[0] - (self.slope * self.start[1])

        self.y_intercept = y_intercept

    def check_intersection(self, other) -> bool:
        """
        Checks if two line segments intersect one another. Accounts for the case where a line in hold-that-line
        intersects with the end point of the segment that it is built off of, and disregards such matches.

        :param other: The Line we're checking for intersection with self
        :return: True if intersection, False if not
        """
        # Check for colinearity and overlap
        # First check if they're parallel
        if self.slope == other.slope:
            check = False
            # vertical lines must be checked before all others due to their lack of y intercepts
            if self.vertical and other.vertical:
                if self.start[1] == other.start[1]:
                    check = True
            # in the typical case, two line segments with the same slope and y intercept are colinear
            elif self.y_intercept == other.y_intercept:
                check = True  # they're colinear!

            if check:
                # check for overlap of colinear lines
                validators = [self.is_on_segment(other.start),
                              self.is_on_segment(other.end) and not self.start == other.end,  # check for shared start+end
                              other.is_on_segment(self.start) and not self.start == other.end,  # same as above
                              other.is_on_segment(self.end)]

                return any(validators)
            else:
                # parallel non-colinear lines cannot ever intersect
                return False

        # they are not parallel
        else:
            # if theres a vertical line between our two segments, we need to calculate our intersect differently
            if self.vertical or other.vertical:
                vert = self if self.vertical else other
                non_vert = self if vert == other else other
                intersect_x = vert.start[1]
                intersect_y = (non_vert.slope * intersect_x) + non_vert.y_intercept
            # otherwise, it goes as you'd expect
            else:
                m = self.slope - other.slope  # m_1 - m_2
                b = other.y_intercept - self.y_intercept  # b_2 - b_1
                intersect_x = b / m
                intersect_y = (self.slope * intersect_x) + self.y_intercept

            coord = (intersect_y, intersect_x)
            if coord == self.start == other.end:  # check for shared start+end
                return False
            else:
                return self.is_on_segment(coord) and other.is_on_segment(coord)

    def is_on_segment(self, coord: Tuple[int, int]) -> bool:
        """
        Determines if a point is within a given line segment.

        ONLY USE IF YOU KNOW THE POINT IS ON THE INFINITE LINE THAT SELF IS A PART OF

        :param coord: The coordinates of the point to check
        :return: True if the point is on the Line, false if otherwise
        """
        #
        lower_x = min(self.start[1], self.end[1])
        upper_x = max(self.start[1], self.end[1])
        lower_y = min(self.start[0], self.end[0])
        upper_y = max(self.start[0], self.end[0])

        return lower_y <= coord[0] <= upper_y and lower_x <= coord[1] <= upper_x


if __name__ == '__main__':
    a = Line((0, 2), (3, 1))
    b = Line((1, 2), (1, 1))
    print(a.check_intersection(b))