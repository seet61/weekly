# -*- coding:utf8 -*-

from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtGui import QCloseEvent
import time, sqlite3

import sys
#sys.setdefaultencoding('utf-8')

class MainWindow(QtGui.QWidget):
    def __init__(self):
        """инициализация окна"""
        self.con, self.cur = self.connect_db()
        # Написать авторизацию!!!!!!!!!!
        self.main_window = uic.loadUi("weekly_tabs.ui")
        self.main_window.setCurrentIndex(0)
        self.day = time.strftime('%d.%m.%Y')
        self.main_window.label.setText(self.day)
        self.load_day()
        self.main_window.tableWidget.setColumnWidth(1, 50)
        self.main_window.tableWidget.setColumnWidth(2, 150)
        self.main_window.tableWidget.setColumnWidth(3, 170)
        self.main_window.dateEdit.setDate(QtCore.QDate(time.localtime()[0], time.localtime()[1], time.localtime()[2]))
        self.connect(self.main_window.calendarWidget, QtCore.SIGNAL("selectionChanged()"), self.load_day)
        self.connect(self.main_window.btn_load_week, QtCore.SIGNAL("clicked()"), self.load_week)
        self.connect(self.main_window.btn_delete, QtCore.SIGNAL("clicked()"), self.delete_entry)
        self.connect(self.main_window.btn_save, QtCore.SIGNAL("clicked()"), self.save_entry)
        #self.connect(self.main_window.tableWidget, QtCore.SIGNAL("cellClicked()"), self.full)
        self.connect(self.main_window.btn_full, QtCore.SIGNAL("clicked()"), self.full)

    def connect_db(self):
        con = sqlite3.connect('/home/seet/PycharmProjects/weekly/weekly.db')
        cur = con.cursor()
        return con, cur

    def full(self):
        item = self.main_window.tableWidget.currentItem()
        print unicode(item.text())
        self.main_window.textBrowser.setText(unicode(item.text()))


    def load_day(self):
        """ загружаем день """
        self.main_window.tableWidget.clear()
        self.day = self.main_window.calendarWidget.selectedDate()
        self.day = self.day.toString("dd.MM.yyyy")
        self.main_window.label.setText(self.day)
        res = []
        self.cur.execute("select * from records where date=?;", (str(self.day),))
        res = self.cur.fetchall()
        self.main_window.tableWidget.setRowCount(len(res))
        for row in xrange(len(res)):
            for col in xrange(len(res[row])):
                #print row, col, res[row][col]
                qitem = QtGui.QTableWidgetItem(res[row][col])
                self.main_window.tableWidget.setItem(row,col, qitem)


    def load_week(self):
        """ Загружаем неделю """
        day_format = time.strptime(self.day, '%d.%m.%Y')
        self.week = str(int(time.strftime('%U', day_format)) + 1)
        self.main_window.label.setText(self.week)
        self.cur.execute("select * from records where week=? order by date", (str(self.week),))
        res = self.cur.fetchall()
        self.main_window.tableWidget.setRowCount(len(res))
        for row in xrange(len(res)):
            for col in xrange(len(res[row])):

                #print row, col, res[row][col]
                qitem = QtGui.QTableWidgetItem(res[row][col])
                self.main_window.tableWidget.setItem(row,col, qitem)

    def save_entry(self):
        """Данные для сохранения"""
        date = self.main_window.dateEdit.date()
        date = date.toString("dd.MM.yyyy")
        #print date
        day_format = time.strptime(date, '%d.%m.%Y')
        week = str(int(time.strftime('%U', day_format)) + 1)
        #print week
        short = self.main_window.short_description.text()
        #print u'%s' % short
        full = self.main_window.full_description.toPlainText()
        #print u'%s' % full
        if (len(short) > 3) and (len(full) > 10):
            #print u'Записываем данные'
            self.cur.execute("insert into records(date, week, short_description, more_description) values (?, ?, ?, ?)",\
                             (str(date), week, unicode(short), unicode(full)))
            self.con.commit()
            self.main_window.short_description.clear()
            self.main_window.full_description.clear()
            self.main_window.error.setText(u'Сохранено.')
        else:
            self.main_window.error.setText(u'Ввведено короткое описание!')

    def delete_entry(self):
        """Удаление записи"""
        #row = self.main_window.tableWidget.currentRow()
        item = self.main_window.tableWidget.currentItem()
        self.cur.execute("delete from records where short_description=?",\
                             (unicode(item.text()),))
        self.con.commit()

    def closeEvent(self):
        """Закрытие окна"""
        self.cur.close()
        self.con.close()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.main_window.show()
    sys.exit(app.exec_())