import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel,
                             QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QScrollArea, QTimeEdit, QLineEdit,
                             QCheckBox)
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5 import uic, QtWidgets
import mysql.connector


print("connecting to db...")
cnx = mysql.connector.connect(user='root',password='...',host='127.0.0.1',database='alarm')
print("connected to db")
cursor = cnx.cursor()


class NewWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi('setAlarm.ui', self)
        self.setWindowTitle("Set Alarm")

        self.saveButton = self.findChild(QPushButton, 'pushButton')
        self.time = self.findChild(QTimeEdit, 'timeEdit')
        self.label = self.findChild(QLineEdit, 'lineEdit')


        self.saveButton.clicked.connect(self.saveAlarm)
        self.time.setDisplayFormat("HH:mm")
        self.show()

    def saveAlarm(self):

        try:

            cursor.execute('INSERT INTO alarm.alarm (label, time, enabled) VALUES (%s, %s, %s);', (self.label.text(), self.time.text(), 1))
            cnx.commit()

            window.addAlarmWidget(self.time.text() + self.label.text(),cursor.lastrowid, 1)

            self.label.clear()
        except mysql.connector.Error as err:
            print(err)

class AlarmClock(QMainWindow):
    def __init__(self):
        super().__init__()


        uic.loadUi('alarmClock.ui', self)
        self.setWindowTitle("Alarm Clock")


        self.scroll_layout = self.findChild(QWidget, "scrollAreaWidgetContents").layout()
        self.addButton = self.findChild(QPushButton, "pushButton")
        self.addButton.clicked.connect(self.openWindow)

        self.alarm_timer = QTimer()
        self.alarm_timer.timeout.connect(self.check_alarms)
        self.alarm_timer.start(1000) 

        self.addAlarmLabels()
        self.show()





    def addAlarmLabels(self):
        cursor.execute("SELECT DATE_FORMAT (time, '%H:%i'), id, label, enabled AS alarm_simple FROM alarm;")

        for i in cursor.fetchall():
            self.addAlarmWidget(i[0] + (f'  {i[2]}' if i[2]!= None else ''), i[1], i[3])

    def addAlarmWidget(self, alarm_text, index, enabled):

        alarm_widget = QWidget()
        alarm_layout = QHBoxLayout(alarm_widget)


        alarm_label = QLabel(alarm_text)
        alarm_label.setStyleSheet("""
            QLabel { 
    color: #7B1FA2; 
    background: rgba(186, 104, 200, 0.1); 
    border-radius: 8px; 
    padding: 10px; 
}
        """)


        delete_btn = QPushButton("Delete")
        delete_btn.setMaximumWidth(100)
        delete_btn.clicked.connect(lambda: self.deleteAlarm(alarm_widget, index))

        delete_btn.setStyleSheet(
            """
            QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #F44336, stop:1 #D32F2F);
    color: white;
    font-weight: bold;
    border: none;
    border-radius: 20px;
    padding: 12px 25px;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #E57373, stop:1 #F44336);
    border: 2px solid #FFCDD2;
}
QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #D32F2F, stop:1 #C62828);
    transform: scale(0.95);
}
            """
        )


        checkbox = QCheckBox()
        checkbox.setStyleSheet("""
        QCheckBox::indicator {
            width: 25px;
            height: 25px;
            border-radius: 12px;
            border: 3px solid #BDBDBD;
            background: #F5F5F5;
        }
        QCheckBox::indicator:checked {
            background: #4CAF50;
            border-color: #388E3C;
        }
        QCheckBox::indicator:hover {
            border-color: #757575;
        }
        """)
        checkbox.setMaximumWidth(50)
        checkbox.setChecked(True if enabled == 1 else False)
        checkbox.stateChanged.connect(lambda :self.set_enabled(index, enabled))


        alarm_layout.addWidget(alarm_label)
        alarm_layout.addWidget(checkbox)
        alarm_layout.addWidget(delete_btn)


        if self.scroll_layout.count() > 0:
            # check for last item is spacer or not
            last_item = self.scroll_layout.itemAt(self.scroll_layout.count() - 1)
            if last_item.spacerItem():
                self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, alarm_widget)
            else:
                self.scroll_layout.addWidget(alarm_widget)
        else:
            self.scroll_layout.addWidget(alarm_widget)




    def deleteAlarm(self, alarm_widget, index):
        try:

            cursor.execute('DELETE FROM alarm.alarm WHERE id = %s;', (index,))
            cnx.commit()
        except mysql.connector.Error as err:
            print(err)

        self.scroll_layout.removeWidget(alarm_widget)
        alarm_widget.deleteLater()





    def set_enabled(self, id, enabled):

        try:

            cursor.execute("UPDATE alarm.alarm SET enabled = %s WHERE id = %s;",
                       (0 if enabled == 1 else 1, id))
            cnx.commit()

        except mysql.connector.Error as err:
            print(err)


    def openWindow(self):
        self.new_window = NewWindow()
        self.new_window.show()


    def check_alarms(self):
        current_time = QTime.currentTime().toString("HH:mm")

        try:

            cursor.execute("SELECT DATE_FORMAT(time, '%H:%i'), label, id FROM alarm WHERE enabled = 1")
            alarms = cursor.fetchall()

            for alarm in alarms:
                alarm_time = alarm[0]
                alarm_label = alarm[1] if alarm[1] else "Alarm"
                alarm_id = alarm[2]

                if current_time == alarm_time:
                    

                    self.show_alarm_message(alarm_label, alarm_time)


                    cursor.execute("UPDATE alarm SET enabled = 0 WHERE id = %s", (alarm_id,))
                    cnx.commit()

        except mysql.connector.Error as err:
            print(err)




    def show_alarm_message(self, label, time):

        from PyQt5.QtWidgets import QMessageBox

        msg = QMessageBox()
        msg.setWindowTitle("Alarm!")
        msg.setText(f'{label}\n{time})')
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

app = QApplication(sys.argv)
window = AlarmClock()
app.exec_()