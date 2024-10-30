import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton
from PyQt6.QtWidgets import QLabel, QLineEdit, QLCDNumber


class RandomString(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 400, 400)
        self.setWindowTitle('ну очень крутой проект')
        self.dob = QPushButton("вставить элемент", self)
        self.dob.move(20, 20)
        self.dob.resize(120, 50)
        self.dob.clicked.connect(self.dobav)
        self.text_dob = QLineEdit(self)
        self.text_dob.move(160, 20)
        self.text_dob.resize(200, 50)
        self.pokaz = QPushButton("вывести элемент", self)
        self.pokaz.move(20, 220)
        self.pokaz.resize(120, 50)
        self.pokaz.clicked.connect(self.el_pokaz)
        self.text_pokaz = QLineEdit(self)
        self.text_pokaz.move(160, 220)
        self.text_pokaz.resize(200, 50)
        self.left = QPushButton('<', self)
        self.left.resize(50, 50)
        self.left.move(100, 100)
        self.left.clicked.connect(self.lev_click)
        self.right = QPushButton('>', self)
        self.right.resize(50, 50)
        self.right.move(225, 100)
        self.right.clicked.connect(self.prav_click)
        self.super_left = QPushButton('<<', self)
        self.super_left.resize(25, 25)
        self.super_left.move(80, 113)
        self.super_left.clicked.connect(self.superlev_click)
        self.super_right = QPushButton('>>', self)
        self.super_right.resize(25, 25)
        self.super_right.move(270, 113)
        self.super_right.clicked.connect(self.superprav_click)
        self.LCD_count = QLCDNumber(self)
        self.LCD_count.resize(75, 60)
        self.LCD_count.move(150, 90)
        self.count = 0

    def lev_click(self):
        if self.count != 0:
            self.count -= 1
        self.LCD_count.display(self.count)

    def prav_click(self):
        if self.count + 1 < 1000:
            self.count += 1
        self.LCD_count.display(self.count)

    def superprav_click(self):
        if self.count + 10 < 1000:
            self.count += 10
        else:
            self.count = 999
        self.LCD_count.display(self.count)

    def superlev_click(self):
        if self.count - 10 >= 0:
            self.count -= 10
        else:
            self.count = 0
        self.LCD_count.display(self.count)

    def dobav(self):
        con = sqlite3.connect("proekt.sqlite")
        cur = con.cursor()
        cur.execute("UPDATE pervaya SET информация = ? WHERE номер = ?", (self.text_dob.text(),self.count))

    def el_pokaz(self):
        con = sqlite3.connect("proekt.sqlite")
        cur = con.cursor()
        cur.execute("SELECT pervaya.информация FROM pervaya")
        results = list(cur.fetchall())



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RandomString()
    ex.show()
    sys.exit(app.exec())
