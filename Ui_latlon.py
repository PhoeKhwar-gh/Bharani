# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1200, 900)
        font = QtGui.QFont()
        font.setFamily("Pyidaungsu")
        font.setPointSize(10)
        Dialog.setFont(font)
        
        # Set window icon
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("res/search.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        
        # Window flags - Remove maximize/minimize buttons, make it a dialog
        Dialog.setWindowFlags(QtCore.Qt.Dialog | 
                             QtCore.Qt.WindowTitleHint | 
                             QtCore.Qt.WindowCloseButtonHint |
                             QtCore.Qt.WindowSystemMenuHint)
        Dialog.setFixedSize(1200, 900)  # Fixed size to prevent resizing
        
        self.horizontalLayout = QtWidgets.QHBoxLayout(Dialog)
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        # ================== LEFT PANEL ==================
        self.leftFrame = QtWidgets.QFrame(Dialog)
        self.leftFrame.setFixedWidth(400)
        self.leftFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.leftFrame.setObjectName("leftFrame")
        self.leftLayout = QtWidgets.QVBoxLayout(self.leftFrame)
        self.leftLayout.setObjectName("leftLayout")

        # Title
        self.labelTitle = QtWidgets.QLabel(self.leftFrame)
        self.labelTitle.setText("နေရာဒေသ အသစ် ဖြည့်ရန်")
        self.labelTitle.setFont(QtGui.QFont("Pyidaungsu", 12, QtGui.QFont.Bold))
        self.leftLayout.addWidget(self.labelTitle)

        # Country
        self.countryLayout = QtWidgets.QHBoxLayout()
        self.labelCountry = QtWidgets.QLabel("နိုင်ငံ")
        self.labelCountry.setMinimumWidth(120)
        self.txtCountry = QtWidgets.QLineEdit()
        self.countryLayout.addWidget(self.labelCountry)
        self.countryLayout.addWidget(self.txtCountry)
        self.leftLayout.addLayout(self.countryLayout)
        
        # State
        self.stateLayout = QtWidgets.QHBoxLayout()
        self.labelState = QtWidgets.QLabel("တိုင်း/ပြည်နယ်")
        self.labelState.setMinimumWidth(120)
        self.txtState = QtWidgets.QLineEdit()
        self.stateLayout.addWidget(self.labelState)
        self.stateLayout.addWidget(self.txtState)
        self.leftLayout.addLayout(self.stateLayout)
        
        # City
        self.cityLayout = QtWidgets.QHBoxLayout()
        self.labelCity = QtWidgets.QLabel("မြို့/ကျေးရွာ")
        self.labelCity.setMinimumWidth(120)
        self.txtCity = QtWidgets.QLineEdit()
        self.cityLayout.addWidget(self.labelCity)
        self.cityLayout.addWidget(self.txtCity)
        self.leftLayout.addLayout(self.cityLayout)

        # Latitude
        self.latLayout = QtWidgets.QHBoxLayout()
        self.labelLat = QtWidgets.QLabel("လတ္တီကျု (၀.၀၀၀၀)")
        self.labelLat.setMinimumWidth(120)
        self.txtLat = QtWidgets.QLineEdit()
        self.latLayout.addWidget(self.labelLat)
        self.latLayout.addWidget(self.txtLat)
        self.leftLayout.addLayout(self.latLayout)

        # Longitude
        self.lonLayout = QtWidgets.QHBoxLayout()
        self.labelLon = QtWidgets.QLabel("လောင်ဂျီတွဒ် (၀.၀၀၀၀)")
        self.labelLon.setMinimumWidth(120)
        self.txtLon = QtWidgets.QLineEdit()
        self.lonLayout.addWidget(self.labelLon)
        self.lonLayout.addWidget(self.txtLon)
        self.leftLayout.addLayout(self.lonLayout)

        # Time Zone
        self.tzLayout = QtWidgets.QHBoxLayout()
        self.labelTZ = QtWidgets.QLabel("Time Zone")
        self.labelTZ.setMinimumWidth(120)
        self.txtTimezone = QtWidgets.QLineEdit()
        self.tzLayout.addWidget(self.labelTZ)
        self.tzLayout.addWidget(self.txtTimezone)
        self.leftLayout.addLayout(self.tzLayout)

        # Cache Label
        self.lblCache = QtWidgets.QLabel("🌍 ရှာဖွေသည့် နေရာဒေသကို ရွေးပါက မြေပုံတွင် ပြသပါမည် → လတ္တီကျု၊ လောင်ဂျီကျု ပေါ်လာပါမည်")
        self.lblCache.setWordWrap(True)
        self.lblCache.setStyleSheet("background-color:#e6f7ff; border:1px solid #91d5ff; padding:5px;")
        self.leftLayout.addWidget(self.lblCache)

        # Search area
        self.searchLayout = QtWidgets.QHBoxLayout()
        self.btnSearch = QtWidgets.QPushButton("ရှာပါ")
        self.txtSearch = QtWidgets.QLineEdit()
        self.txtSearch.setPlaceholderText("🔍 မြို့/ကျေးရွာအမည် ရှာရန်...")
        self.searchLayout.addWidget(self.btnSearch)
        self.searchLayout.addWidget(self.txtSearch)
        self.leftLayout.addLayout(self.searchLayout)

        # Search Results List
        self.listResults = QtWidgets.QListWidget()
        self.listResults.setVisible(False)
        self.leftLayout.addWidget(self.listResults)

        # Spacer
        spacer = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.leftLayout.addItem(spacer)

        # Save button
        self.btnSave = QtWidgets.QPushButton("Save Lat, Lon")
        self.btnSave.setMinimumHeight(40)
        self.leftLayout.addWidget(self.btnSave)

        self.horizontalLayout.addWidget(self.leftFrame)

        # ================== RIGHT PANEL (MAP) ==================
        self.rightFrame = QtWidgets.QFrame(Dialog)
        self.rightFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.rightFrame.setObjectName("rightFrame")
        self.rightLayout = QtWidgets.QVBoxLayout(self.rightFrame)
        self.rightLayout.setContentsMargins(0, 0, 0, 0)
        self.frmWeb = QtWidgets.QFrame(self.rightFrame)
        self.frmWeb.setMinimumSize(QtCore.QSize(700, 600))
        self.frmWeb.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.rightLayout.addWidget(self.frmWeb)
        self.horizontalLayout.addWidget(self.rightFrame)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "နေရာဒေသအသစ် ရှာဖွေရေးကိရိယာ"))