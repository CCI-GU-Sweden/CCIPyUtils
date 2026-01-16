from math import cos, sin, pi
from ccipy.utils.cci_colors import Colors


class RoiGeometry:
    
    def __init__(self, color: int = Colors.WHITE, text: str = ""):
        self.text = text
        self.color = color
                
    def get_color(self) -> int:
        return self.color
    
    def set_color(self, color: int):
        self.color = color
        
    def get_text(self) -> str:
        return self.text
    
        
class RoiPoint(RoiGeometry):
    def __init__(self, x: float, y: float, color: int = Colors.WHITE, text: str = ""):
        super().__init__(color, text)
        self.x = x
        self.y = y
    
    
class RoiRectangle(RoiGeometry):
    
    def __init__(self, x: float, y: float, width: float, height: float, color: int = Colors.WHITE, text: str = ""):
        super().__init__(color, text)
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @staticmethod
    def from_normalized_xyxy(x1_norm: float, y1_norm: float, x2_norm: float, y2_norm: float, image_width: int, image_height: int, color: int = Colors.WHITE, text: str = "") -> 'RoiRectangle':
        #
        # Create RoiRectangle from normalized (0..1) xyxy coordinates
        #
        x1 = x1_norm * image_width
        y1 = y1_norm * image_height
        x2 = x2_norm * image_width
        y2 = y2_norm * image_height
        width = x2 - x1
        height = y2 - y1
        return RoiRectangle(x1, y1, width, height, color, text)

    @staticmethod
    def from_normalized_xywh(x_norm: float, y_norm: float, width_norm: float, height_norm: float, image_width: int, image_height: int, color: int = Colors.WHITE, text: str = "") -> 'RoiRectangle':
        #
        # Create RoiRectangle from normalized (0..1) xywh coordinates where x and y are top-left corner
        #
        x = x_norm * image_width
        y = y_norm * image_height
        width = width_norm * image_width
        height = height_norm * image_height
        return RoiRectangle(x, y, width, height, color, text)
    
    def get_point_list(self) -> list[RoiPoint]:
        #half_w = self.width / 2
        #half_h = self.height / 2

        return [
            RoiPoint(self.x, self.y),  # top-left
            RoiPoint(self.x + self.width, self.y),  # top-right
            RoiPoint(self.x + self.width, self.y + self.height),  # bottom-right
            RoiPoint(self.x, self.y + self.height),  # bottom-left
        ]
        
        
class RoiEllipse(RoiGeometry):
    
    def __init__(self, x: float, y: float, width: float, height: float, color: int = Colors.WHITE, text: str = ""):
        super().__init__(color, text)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def get_point_list(self, num_points: int = 36) -> list[RoiPoint]:

        # TODO: Double check that the roi from omera is centered!!!
        points = []
        rx = self.width / 2
        ry = self.height / 2
        cx = self.x + rx
        cy = self.y + ry

        for i in range(num_points):
            theta = 2 * pi * i / num_points
            x = cx + rx * cos(theta)
            y = cy + ry * sin(theta)
            points.append(RoiPoint(x, y))

        return points
        

class RoiPolygon(RoiGeometry):
    
    def __init__(self, points: list[RoiPoint], color: int = Colors.WHITE, text: str = ""):
        super().__init__(color, text)
        self.points = points
        
    def get_point_list(self) -> list[RoiPoint]:
        return self.points
