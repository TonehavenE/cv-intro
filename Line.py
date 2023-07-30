from numpy import power

# CONSTANTS
VERTICAL_SLOPE = power(10, 10)
HORIZONTAL_SLOPE = 0.00000000000001
NO_X_INTERCEPT = power(10, 10)

class Line:
    img_height = int(1080/2)

    def __init__(self, x1: int, y1: int, x2: int, y2: int):
        self.x1 = int(x1)
        self.y1 = int(y1)
        self.x2 = int(x2)
        self.y2 = int(y2)
        self.slope = self.calculate_slope()
        self.x_intercept = self.calculate_x_intercept()
        # self.x_of = np.vectorize(self.x)
        # self.y_of = np.vectorize(self.y)
        self.y_intercept = self.y(0)
        self.paired = False

    def calculate_slope(self) -> float:
        if self.x1 == self.x2:
            return VERTICAL_SLOPE
        elif self.y1 == self.y2:
            return HORIZONTAL_SLOPE
        else:
            return (self.y2 - self.y1) / (self.x2 - self.x1)

    def calculate_x_intercept(self) -> int:
        if self.y1 == self.y2:
            return NO_X_INTERCEPT
        else:
            # return ((self.slope * self.x1) - self.y1) / self.slope
            return round(((self.img_height - self.y1) / self.slope) + self.x1, 0)

    def get_points(self) -> list[int, int, int, int]:
        return [self.x1, self.y1, self.x2, self.y2]
    
    def y(self, x: float) -> float:
        # y - y1 = m(x - x1)
        # y = m(x - x1) + y1
        return self.slope * (x - self.x1) + self.y1
    
    def x(self, y: float) -> float:
        # y - y1 = mx - mx1
        # mx = y - y1 + mx1
        # x = ((y - y1) / m) + x1
        return ((y - self.y1) / self.slope) + self.x1

    def is_paired(self) -> bool:
        return self.paired

    def __str__(self) -> str:
        return f"p1: ({self.x1}, {self.y1}), p2: ({self.x2}, {self.y2}), slope: {self.slope:.2f}, x-intercept: {self.x_intercept}, y-intercept: {self.y_intercept}"