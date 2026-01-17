import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath

class Rura:
    def __init__(self, punkty, grubosc=12, kolor=Qt.gray):
        self.punkty=[QPointF(float(p[0]),float(p[1]))for p in punkty]
        self.grubosc=grubosc
        self.kolor_rury=kolor
        self.kolor_cieczy=QColor(0,180,255)
        self.czy_plynie=False
        
    def ustaw_przeplyw(self,plynie):
        self.czy_plynie=plynie

    def draw(self,painter):
        if len(self.punkty)<2:
            return
        path=QPainterPath()
        path.moveTo(self.punkty[0])
        for p in self.punkty[1:]:
            path.lineTo(p)

        pen_rura = QPen(self.kolor_rury, self.grubosc, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen_rura)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        if self.czy_plynie:
            pen_ciecz = QPen(self.kolor_cieczy, self.grubosc - 4, Qt.SolidLine,Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen_ciecz)
            painter.drawPath(path)
