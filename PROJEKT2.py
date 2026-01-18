import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QInputDialog
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath

class Rura:
    def __init__(self, punkty, grubosc=10, kolor=Qt.yellow):
        self.punkty = [QPointF(float(p[0]), float(p[1])) for p in punkty]
        self.grubosc = grubosc
        self.kolor_rury = kolor
        self.czy_plynie = False
        
    def ustaw_przeplyw(self, plynie):
        self.czy_plynie = plynie

    def draw(self, painter):
        if len(self.punkty) < 2: return
        path = QPainterPath()
        path.moveTo(self.punkty[0])
        for p in self.punkty[1:]:
            path.lineTo(p)
        # Rura stale żółta - brak wizualizacji przepływu
        pen_rura = QPen(self.kolor_rury, self.grubosc, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen_rura)
        painter.drawPath(path)

class Zbiornik:
    def __init__(self, x, y, width=100, height=140, nazwa=""):
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.nazwa = nazwa
        # Z6 ma większą pojemność ze względu na rozmiar 200x200
        self.pojemnosc = 400.0 if width == 200 else 100.0 
        self.aktualna_ilosc = 0.0
        self.poziom = 0.0
        self.temperatura = 20.0

    def dodaj_ciecz(self, ilosc, temp_wlotowa=None):
        wolne = self.pojemnosc - self.aktualna_ilosc
        dodano = min(ilosc, wolne)
        if temp_wlotowa is not None and (self.aktualna_ilosc + dodano) > 0:
            self.temperatura = ((self.aktualna_ilosc * self.temperatura) + (dodano * temp_wlotowa)) / (self.aktualna_ilosc + dodano)
        elif self.aktualna_ilosc == 0 and temp_wlotowa is not None:
            self.temperatura = temp_wlotowa
        self.aktualna_ilosc += dodano
        self.poziom = self.aktualna_ilosc / self.pojemnosc
        return dodano

    def usun_ciecz(self, ilosc):
        usunieto = min(ilosc, self.aktualna_ilosc)
        self.aktualna_ilosc -= usunieto
        self.poziom = self.aktualna_ilosc / self.pojemnosc
        return usunieto

    def punkt_gora_srodek(self): return (self.x + self.width / 2, self.y)
    def punkt_dol_srodek(self): return (self.x + self.width / 2, self.y + self.height)
    def punkt_lewa_bok_45proc(self): return (self.x, self.y + self.height * (1 - 0.45))
    def punkt_prawa_30proc(self): return (self.x + self.width, self.y + self.height * (1 - 0.3))
    def punkt_lewa_srodek(self): return (self.x, self.y + self.height / 2)

    def draw(self, painter):
        if self.aktualna_ilosc > 0:
            h_cieczy = int((self.height - 4) * self.poziom)
            r = min(255, int(self.temperatura * 2))
            g = max(0, 120 - int(self.temperatura))
            b = max(50, 255 - int(self.temperatura))
            painter.setBrush(QColor(r, g, b, 200))
            painter.setPen(Qt.NoPen)
            painter.drawRect(int(self.x + 2), int(self.y + self.height - h_cieczy - 2), int(self.width - 4), h_cieczy)

        painter.setPen(QPen(Qt.green, 4))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(int(self.x), int(self.y), int(self.width), int(self.height))
        
        painter.setPen(Qt.darkGreen)
        if any(char in self.nazwa for char in "3456"):
            painter.drawText(int(self.x), int(self.y + self.height + 25), self.nazwa)
        else:
            painter.drawText(int(self.x), int(self.y - 15), self.nazwa)
        
        painter.setPen(Qt.black)
        text_temp = f"{self.temperatura:.1f}°C" if self.aktualna_ilosc > 0.1 else "-- °C"
        painter.drawText(int(self.x + self.width + 10), int(self.y + self.height / 2), text_temp)

class SymulacjaKaskady(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Symulator kaskady - Z6 Control")
        self.setFixedSize(1200, 950)
        
        start_temp, ok = QInputDialog.getInt(self, "Parametry", "Temp. Z1 (°C):", 20, 0, 100, 1)
        self.temp_startowa = float(start_temp) if ok else 20.0

        # Zbiorniki
        self.z1 = Zbiornik(100, 50, nazwa="Zbiornik 1")
        self.z1.aktualna_ilosc = 30.0; self.z1.poziom = 0.3; self.z1.temperatura = self.temp_startowa
        
        self.z2 = Zbiornik(450, 200, nazwa="Zbiornik 2")
        self.z3 = Zbiornik(750, 500, nazwa="Zbiornik 3")
        self.z4 = Zbiornik(100, 650, nazwa="Zbiornik 4")
        self.z5 = Zbiornik(450, 700, nazwa="Zbiornik 5")
        
        # Zbiornik 6 (200x200)
        self.z6 = Zbiornik(850, 80, width=200, height=200, nazwa="Zbiornik 6")
        
        self.zbiorniki = [self.z1, self.z2, self.z3, self.z4, self.z5, self.z6]

        # Definicje rur
        p1s, p1k = self.z1.punkt_dol_srodek(), self.z2.punkt_gora_srodek()
        self.rura1 = Rura([p1s, (p1s[0], 125), (p1k[0], 125), p1k])
        
        p2s, p2k = self.z2.punkt_dol_srodek(), self.z3.punkt_gora_srodek()
        self.rura2 = Rura([p2s, (p2s[0], 480), (p2k[0], 480), p2k])
        
        p3s, p3k = self.z2.punkt_lewa_bok_45proc(), self.z4.punkt_gora_srodek()
        self.rura3 = Rura([p3s, (300, p3s[1]), (150, 600), p3k])

        self.rura_z2_do_z5 = Rura([self.z2.punkt_dol_srodek(), self.z5.punkt_gora_srodek()])

        # Rura do Z6 (odchodzi na 30% wysokości Z2)
        p2_30 = self.z2.punkt_prawa_30proc()
        p6_in = self.z6.punkt_lewa_srodek()
        self.rura_z2_do_z6 = Rura([p2_30, (p2_30[0] + 150, p2_30[1]), (p2_30[0] + 150, p6_in[1]), p6_in])

        self.rury = [self.rura1, self.rura2, self.rura3, self.rura_z2_do_z5, self.rura_z2_do_z6]
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.logika)
        self.running = False
        self.init_ui()

    def init_ui(self):
        self.btn_start = QPushButton("Start / Stop", self)
        self.btn_start.setGeometry(30, 880, 100, 40)
        self.btn_start.clicked.connect(self.start_stop)

        # Zaktualizowana lista przycisków
        labels = [
            ("Z1 Max", self.pelen_z1), ("Z1 Pusto", self.pusty_z1),
            ("Z2 Max", self.pelen_z2), ("Z2 Pusto", self.pusty_z2),
            ("Z3 Max", self.pelen_z3), ("Z3 Pusto", self.pusty_z3),
            ("Z4 Max", self.pelen_z4), ("Z4 Pusto", self.pusty_z4),
            ("Z5 Max", self.pelen_z5), ("Z5 Pusto", self.pusty_z5),
            ("Z6 Max", self.pelen_z6), ("Z6 Pusto", self.pusty_z6)
        ]
        
        x_pos = 150
        for text, func in labels:
            btn = QPushButton(text, self)
            btn.setGeometry(x_pos, 885, 80, 30)
            btn.setStyleSheet("background-color: #444; color: white; font-size: 10px;")
            btn.clicked.connect(func)
            x_pos += 85

    # Metody sterowania zbiornikami
    def pelen_z1(self): self.z1.dodaj_ciecz(100.0); self.z1.temperatura = self.temp_startowa; self.update()
    def pusty_z1(self): self.z1.usun_ciecz(100.0); self.update()
    def pelen_z2(self): self.z2.dodaj_ciecz(100.0); self.update()
    def pusty_z2(self): self.z2.usun_ciecz(100.0); self.update()
    def pelen_z3(self): self.z3.dodaj_ciecz(100.0); self.update()
    def pusty_z3(self): self.z3.usun_ciecz(100.0); self.update()
    def pelen_z4(self): self.z4.dodaj_ciecz(100.0); self.update()
    def pusty_z4(self): self.z4.usun_ciecz(100.0); self.update()
    def pelen_z5(self): self.z5.dodaj_ciecz(100.0); self.update()
    def pusty_z5(self): self.z5.usun_ciecz(100.0); self.update()
    def pelen_z6(self): self.z6.dodaj_ciecz(400.0); self.update()
    def pusty_z6(self): self.z6.usun_ciecz(400.0); self.update()

    def start_stop(self):
        if self.running: self.timer.stop()
        else: self.timer.start(30)
        self.running = not self.running

    def rysuj_pompe(self, painter, rura, index_punktu):
        center = rura.punkty[index_punktu]
        painter.setBrush(Qt.yellow)
        painter.setPen(QPen(Qt.black, 2))
        painter.drawEllipse(center, 18, 18)

    def logika(self):
        # Z1 -> Z2
        if self.z1.poziom > 0.05 and self.z2.aktualna_ilosc < self.z2.pojemnosc:
            self.z2.dodaj_ciecz(self.z1.usun_ciecz(0.6), self.z1.temperatura)

        # Grzanie Z2
        if self.z2.aktualna_ilosc > 0 and self.z2.temperatura < self.temp_startowa + 25:
            self.z2.temperatura += 0.05

        # Pompa Z2 -> Z6 (Wylot na 30% wysokości)
        if self.z2.poziom > 0.3 and self.z6.aktualna_ilosc < self.z6.pojemnosc:
            self.z6.dodaj_ciecz(self.z2.usun_ciecz(0.8), self.z2.temperatura)

        # Grawitacyjny odpływ z dna Z2
        if self.z2.poziom > 0.15:
            if self.z3.aktualna_ilosc < self.z3.pojemnosc:
                self.z3.dodaj_ciecz(self.z2.usun_ciecz(0.3), self.z2.temperatura)
            if self.z5.aktualna_ilosc < self.z5.pojemnosc:
                self.z5.dodaj_ciecz(self.z2.usun_ciecz(0.2), self.z2.temperatura)

        # Wylot boczny Z2 -> Z4 (na 45% wysokości)
        if self.z2.poziom > 0.45 and self.z4.aktualna_ilosc < self.z4.pojemnosc:
            self.z4.dodaj_ciecz(self.z2.usun_ciecz(0.3), self.z2.temperatura)
            
        self.update()

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        for r in self.rury: r.draw(p)
        
        # Popy (identyczne dla Z1 i Z2->Z6)
        self.rysuj_pompe(p, self.rura1, 1) 
        self.rysuj_pompe(p, self.rura_z2_do_z6, 1) 
        
        for z in self.zbiorniki: z.draw(p)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SymulacjaKaskady(); ex.show()
    sys.exit(app.exec_())
