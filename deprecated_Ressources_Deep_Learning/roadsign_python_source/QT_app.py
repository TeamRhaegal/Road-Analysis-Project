# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QPixmap
import sys
import numpy as np

class Ui_MainWindow(object):
    
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.MainWindow = QtWidgets.QMainWindow()
        self.setupUi(self.MainWindow)
        self.MainWindow.show()
        sys.exit(self.app.exec_())
        pass
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 720)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setEnabled(True)
        self.pushButton.setGeometry(QtCore.QRect(20, 10, 83, 25))
        self.pushButton.setCheckable(False)
        self.pushButton.setObjectName("pushButton")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(180, 370, 261, 20))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(820, 370, 301, 20))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(830, 40, 271, 17))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(190, 40, 271, 17))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(10, 70, 601, 281))
        self.label_5.setScaledContents(True)
        self.label_5.setObjectName("camera_image")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(670, 70, 601, 281))
        self.label_6.setScaledContents(True)
        self.label_6.setObjectName("location_image")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(100, 390, 121, 131))
        self.label_7.setScaledContents(True)
        self.label_7.setObjectName("cropped_image_1")
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(100, 540, 121, 131))
        self.label_9.setScaledContents(True)
        self.label_9.setObjectName("cropped_image_4")
        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setGeometry(QtCore.QRect(250, 540, 121, 131))
        self.label_10.setScaledContents(True)
        self.label_10.setObjectName("cropped_image_5")
        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        self.label_11.setGeometry(QtCore.QRect(250, 390, 121, 131))
        self.label_11.setScaledContents(True)
        self.label_11.setObjectName("cropped_image_2")
        self.label_12 = QtWidgets.QLabel(self.centralwidget)
        self.label_12.setGeometry(QtCore.QRect(400, 390, 121, 131))
        self.label_12.setScaledContents(True)
        self.label_12.setObjectName("cropped_image_3")
        self.label_13 = QtWidgets.QLabel(self.centralwidget)
        self.label_13.setGeometry(QtCore.QRect(400, 540, 121, 131))
        self.label_13.setScaledContents(True)
        self.label_13.setObjectName("cropped_image_6")
        self.label_14 = QtWidgets.QLabel(self.centralwidget)
        self.label_14.setGeometry(QtCore.QRect(1060, 390, 121, 131))
        self.label_14.setScaledContents(True)
        self.label_14.setObjectName("roadsign_representation_3")
        self.label_15 = QtWidgets.QLabel(self.centralwidget)
        self.label_15.setGeometry(QtCore.QRect(1060, 540, 121, 131))
        self.label_15.setScaledContents(True)
        self.label_15.setObjectName("roadsign_representation_6")
        self.label_16 = QtWidgets.QLabel(self.centralwidget)
        self.label_16.setGeometry(QtCore.QRect(910, 390, 121, 131))
        self.label_16.setScaledContents(True)
        self.label_16.setObjectName("roadsign_representation_2")
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(760, 390, 121, 131))
        self.label_8.setScaledContents(True)
        self.label_8.setObjectName("roadsign_representation_1")
        self.label_17 = QtWidgets.QLabel(self.centralwidget)
        self.label_17.setGeometry(QtCore.QRect(760, 540, 121, 131))
        self.label_17.setScaledContents(True)
        self.label_17.setObjectName("roadsign_representation_4")
        self.label_18 = QtWidgets.QLabel(self.centralwidget)
        self.label_18.setGeometry(QtCore.QRect(910, 540, 121, 131))
        self.label_18.setScaledContents(True)
        self.label_18.setObjectName("roadsign_representation_5")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1280, 22))
        self.menubar.setObjectName("menubar")
        self.menuRoadsign_detector = QtWidgets.QMenu(self.menubar)
        self.menuRoadsign_detector.setObjectName("menuRoadsign_detector")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuRoadsign_detector.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Exit"))
        self.label.setText(_translate("MainWindow", "Cropped image (s) (up to six roadsigns)"))
        self.label_2.setText(_translate("MainWindow", "Representation of recognized road sign (s)"))
        self.label_3.setText(_translate("MainWindow", "Representation of recognized road sign"))
        self.label_4.setText(_translate("MainWindow", "Representation of recognized road sign"))
        self.label_5.setText(_translate("MainWindow", "TextLabel"))
        self.label_6.setText(_translate("MainWindow", "TextLabel"))
        self.label_7.setText(_translate("MainWindow", "TextLabel"))
        self.label_9.setText(_translate("MainWindow", "TextLabel"))
        self.label_10.setText(_translate("MainWindow", "TextLabel"))
        self.label_11.setText(_translate("MainWindow", "TextLabel"))
        self.label_12.setText(_translate("MainWindow", "TextLabel"))
        self.label_13.setText(_translate("MainWindow", "TextLabel"))
        self.label_14.setText(_translate("MainWindow", "TextLabel"))
        self.label_15.setText(_translate("MainWindow", "TextLabel"))
        self.label_16.setText(_translate("MainWindow", "TextLabel"))
        self.label_8.setText(_translate("MainWindow", "TextLabel"))
        self.label_17.setText(_translate("MainWindow", "TextLabel"))
        self.label_18.setText(_translate("MainWindow", "TextLabel"))
        self.menuRoadsign_detector.setTitle(_translate("MainWindow", "Roadsign_detector"))
    
    # take images path or numpy arrays containing multiple image paths (cropped_images, representation_images) to update images on QT window
    def update_images(self, camera_image, location_image, cropped_images, representation_images):
        
         # add camera + location images 
        self.label_5.setPixmap(QPixmap(camera_image))
        self.label_6.setPixmap(QPixmap(location_image))
        
        # add other multiple images
        cropped_labels = np.array([self.label_7, self.label_11, self.label_12, self.label_9, self.label_10, self.label_13])
        representation_labels = np.array([self.label_8, self.label_16, self.label_14, self.label_17, self.label_18, self.label_15])
        
        for i in range(cropped_images.shape[0]):
            cropped_labels[i].setPixmap(QPixmap(cropped_images[i]))
        
        for i in range(represerntation_images.shape[0]):
            representation_labels[i].setPixmap(QPixmap(representation_images[i]))

        # show labels
        self.label5.show()
        self.label6.show()

        for i in range(cropped_images.shape[0]):
            cropped_labels[i].show()
            
        for i in range(represerntation_images.shape[0]):
            representation_labels[i].show()

