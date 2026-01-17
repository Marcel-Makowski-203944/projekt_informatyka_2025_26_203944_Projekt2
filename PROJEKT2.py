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
            
class Zbiornik :
    def __init__ ( self , x , y , width =100 , height =140 , nazwa ="") :
        self . x = x ; self.y = y
        self . width = width ; self.height = height
        self . nazwa = nazwa
        self . pojemnosc = 100.0
        self . aktualna_ilosc = 0.0
        self . poziom = 0.0
    def dodaj_ciecz ( self , ilosc ) :
        wolne = self . pojemnosc - self . aktualna_ilosc
        dodano = min( ilosc , wolne )
        self . aktualna_ilosc += dodano
        self . aktualizuj_poziom ()
        return dodano
    def usun_ciecz ( self , ilosc ) :
        usunieto = min( ilosc , self.aktualna_ilosc )
        self . aktualna_ilosc -= usunieto
        self . aktualizuj_poziom ()
        return usunieto
    def aktualizuj_poziom ( self ) :
        self . poziom = self . aktualna_ilosc / self . pojemnosc
    def czy_pusty ( self ) :
        return self . aktualna_ilosc <= 0.1
    def czy_pelny ( self ) :
        return self . aktualna_ilosc >= self . pojemnosc - 0.1

    def punkt_gora_srodek(self):
        return (self.x + self.width / 2, self.y)



    def punkt_dol_srodek(self):
        return (self.x + self.width / 2, self.y + self.height)



    def draw(self, painter):
        if self.poziom > 0:
            h_cieczy = self.height * self.poziom
            y_start = self.y + self.height - h_cieczy
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 120, 255, 200))
            painter.drawRect(int(self.x + 3), int(y_start), int(self.width - 6),int(h_cieczy - 2))
        pen = QPen(Qt.white, 4)
        pen.setJoinStyle(Qt.MiterJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))
        painter.setPen(Qt.white)
        painter.drawText(int(self.x), int(self.y - 10), self.nazwa)
