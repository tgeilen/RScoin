from ecpy.curves import Curve, Point


class eccPoint(Point):

    def __init__(self, x,y, curve):
        Point.__init__(self,x,y, curve)


    def is_on_curve(self):
        return super().is_on_curve

    def mul(self, k):
        result =  super().mul(k)
        return eccPoint(result._x, result._y, result._curve)
    
    def add(self, Q):
        result =  super().add(Q)
        return eccPoint(result._x, result._y, result._curve)
    
    def sub(self, Q):
        result =  super().sub(Q)
        return eccPoint(result._x, result._y, result._curve)

    def __str__(self):
        if self.has_x and self.has_y:
            return str(self._x)+str(self._y)
        else:
            super.__str__(self)