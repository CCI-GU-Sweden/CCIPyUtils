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
        
    def get_point_list(self) -> list[RoiPoint]:
        half_w = self.width / 2
        half_h = self.height / 2

        return [
            RoiPoint(self.x - half_w, self.y - half_h),  # top-left
            RoiPoint(self.x + half_w, self.y - half_h),  # top-right
            RoiPoint(self.x + half_w, self.y + half_h),  # bottom-right
            RoiPoint(self.x - half_w, self.y + half_h),  # bottom-left
        ]
        
        
class RoiEllipse(RoiGeometry):
    
    def __init__(self, x: float, y: float, width: float, height: float, color: int = Colors.WHITE, text: str = ""):
        super().__init__(color, text)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
    def get_point_list(self, num_points: int = 36) -> list[RoiPoint]:

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
