from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QMenu, QAction, \
    QGridLayout
from PyQt5.QtCore import Qt, QSize, QTime, QDate
from PyQt5.QtGui import QMouseEvent, QContextMenuEvent, QIcon, QPixmap
import datetime

from util.Folder import Folder

from style_sheets.folder_style_sheet import style_sheet

class FolderWidget(Folder, QWidget):
    def __init__(self, name, path, time, fav, parent = None):
        super(FolderWidget, self).__init__(name, path, time, fav)
        QWidget.__init__(self, parent)
        self.parent = parent

        # create the folder name text , create date and time and icon
        self.name_label = QLabel(self.name)
        self.name_label.setObjectName("name-label")

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(QSize(130, 100))
        icon = QPixmap("img/sys/folder (1).png").scaled(self.icon_label.size() , Qt.KeepAspectRatio, Qt.FastTransformation)
        self.icon_label.setPixmap(icon)

        self.time_label = QLabel(self.formatTime(f"{self.time}"))
        self.time_label.setObjectName("time-label")

        self.favorite_button = QPushButton()
        self.favorite_button.setObjectName("fav-button")
        self.favorite_button.setIcon(QIcon("img/sys/star.png"))

        # create the grid
        self.grid = QGridLayout()
        self.grid.setVerticalSpacing(0)
        # self.changeView(0)

        # create the base widget
        self.baseWidget = QWidget()
        self.baseWidget.setContentsMargins(0, 0, 0, 0)
        self.baseWidget.setObjectName("folder-base")
        self.baseWidget.setLayout(self.grid)

        self.setContentsMargins(0, 0, 0, 0)
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hbox)
        self.layout().addWidget(self.baseWidget)
        self.setStyleSheet(style_sheet)

    def changeView(self, index):

        # first remove the widget from grid
        for w in [self.name_label, self.time_label, self.icon_label, self.favorite_button]:
            self.grid.removeWidget(w)

        if index == 0:
            self.name_label.setWordWrap(False)
            self.grid.addWidget(self.favorite_button, 0, 2)
            self.grid.addWidget(self.icon_label, 0, 0, 3, 1)
            self.grid.addWidget(self.name_label, 1, 1)
            self.grid.addWidget(self.time_label, 2, 2)

            # adjust the size of the widget
            self.setFixedHeight(230)
            self.setMaximumWidth(2000)

        elif index == 1:
            self.name_label.setWordWrap(True)
            self.grid.addWidget(self.favorite_button, 0, 0)
            self.grid.addWidget(self.icon_label, 1, 0, 1, 1)
            self.grid.addWidget(self.name_label, 2, 0, 1, 1)
            # adjust th size of the  widget
            self.setFixedSize(QSize(250, 240))
        else:
            pass

    def contextMenuEvent(self, event : QContextMenuEvent) -> None:

        # create the context menu for folder
        folderMenu = QMenu(self)
        folderMenu.setTitle("Folder Actions")

        # create the folder actions here
        open_action = QAction(QIcon("img/sys/open-folder (1).png"),"Open", self)
        open_action.triggered.connect(lambda e : self.parent.openFolder(self.path))
        folderMenu.addAction(open_action)

        rename_action = QAction(QIcon("img/sys/rename.png"), "Rename", self)
        folderMenu.addAction(rename_action)

        lock_action = QAction(QIcon("img/sys/lock.png"), "Lock", self)
        folderMenu.addAction(lock_action)

        fav_action = QAction(QIcon("img/sys/star.png") , "Set Favorite", self)
        folderMenu.addAction(fav_action)

        delete_action = QAction(QIcon("img/sys/delete.png"),"Delete", self)
        folderMenu.addAction(delete_action)


        folderMenu.exec_(self.mapToGlobal(event.pos()))

    def mousePressEvent(self, event : QMouseEvent) -> None:

        self.parent.selected(self)
        event.accept()


    def mouseDoubleClickEvent(self,event : QMouseEvent) -> None:

        self.parent.openFolder(self.path)
        # stop propagate the signal
        event.accept()

    def selected(self):

        self.baseWidget.setObjectName("selected-folder-base")
        self.setStyleSheet(style_sheet)

    def unselected(self):

        self.baseWidget.setObjectName("folder-base")
        self.setStyleSheet(style_sheet)

    def formatTime(self, text : str):

        date, time = text.split(" ")
        time_ , date_ = QTime.fromString(time.split(".")[0], "hh:mm:ss") , QDate.fromString(date, "yyyy-MM-dd")

        formatted_date, formatted_time = date_.toString("yyyy MMM dd"), time_.toString("hh:mm A")

        return f"created on {formatted_date} {formatted_time}"

if __name__ == "__main__":
    app = QApplication([])
    w = FolderWidget("shavin", ".0", "2022.12.12", False)
    w.show()
    print()
    app.exec_()