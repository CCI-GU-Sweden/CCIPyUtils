
class RoiGeometry:
    
    def __init__(self, text: str = ""):
        self.text = text


class RoiPoint(RoiGeometry):
    def __init__(self, x: float, y: float, text: str = ""):
        super().__init__(text)
        self.x = x
        self.y = y
    
class RoiRectangle(RoiGeometry):
    
    def __init__(self, x: float, y: float, width: float, height: float, text: str = ""):
        super().__init__(text)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        
class RoiEllipse(RoiGeometry):
    
    def __init__(self, x: float, y: float, width: float, height: float, text: str = ""):
        super().__init__(text)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        

class RoiPolygon(RoiGeometry):
    
    def __init__(self, points: list[RoiPoint], text: str = ""):
        super().__init__(text)
        self.points = points


