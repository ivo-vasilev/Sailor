#!/usr/bin/python3

import sys
import os
import json

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QTabBar, QFrame, QStackedLayout, QShortcut,
                             QSplitter)
from PyQt5.QtGui import QIcon, QWindow, QImage, QKeySequence
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *


class AddressBar(QLineEdit):
    def __init__(self):
        super().__init__()

    def mousePressEvent(self, e):
        self.selectAll()


class App(QFrame):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sailor")
        self.setWindowIcon(QIcon('icons/surf-logo-trans.png'))
        self.setMinimumSize(1200, 600)
        self.CreateApp()

    def CreateApp(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Create Tabs
        self.tabbar = QTabBar(movable=True, tabsClosable=True)
        self.tabbar.tabCloseRequested.connect(self.CloseTab)
        self.tabbar.tabBarClicked.connect(self.SwitchTab)
        self.tabbar.setCurrentIndex(0)
        self.tabbar.setDrawBase(False)
        self.tabbar.setLayoutDirection(Qt.LeftToRight)

        self.shortcutNewTab = QShortcut(QKeySequence("Ctrl+T"), self)
        self.shortcutNewTab.activated.connect(self.AddTab)

        self.shortcutReload = QShortcut(QKeySequence("Ctrl+R"), self)
        self.shortcutReload.activated.connect(self.ReloadPage)

        # Keep track of tabs
        self.tabCount = 0
        self.tabs = []

        # Create Address Bar
        self.Toolbar = QWidget()
        self.ToolbarLayout = QHBoxLayout()
        self.addressbar = AddressBar()
        self.addressbar.returnPressed.connect(self.BrowseTo)

        # Add toolbar buttons
        self.BackButton = QPushButton(QIcon('icons/back.png'), "")
        self.BackButton.clicked.connect(self.GoBack)

        self.ForwardButton = QPushButton(QIcon('icons/forward.png'), "")
        self.ForwardButton.clicked.connect(self.GoForward)

        self.ReloadButton = QPushButton(QIcon('icons/reload.png'), "")
        self.ReloadButton.clicked.connect(self.ReloadPage)

        # Create the toolbar
        self.Toolbar.setLayout(self.ToolbarLayout)
        self.Toolbar.setObjectName("Toolbar")
        self.ToolbarLayout.addWidget(self.BackButton)
        self.ToolbarLayout.addWidget(self.ForwardButton)
        self.ToolbarLayout.addWidget(self.ReloadButton)
        self.ToolbarLayout.addWidget(self.addressbar)

        # New Tab button
        self.AddTabButton = QPushButton("+")
        self.AddTabButton.clicked.connect(self.AddTab)
        self.ToolbarLayout.addWidget(self.AddTabButton)

        # Set main view
        self.container = QWidget()
        self.container.layout = QStackedLayout()
        self.container.setLayout(self.container.layout)

        self.layout.addWidget(self.tabbar)
        self.layout.addWidget(self.Toolbar)
        self.layout.addWidget(self.container)

        self.setLayout(self.layout)

        self.AddTab()

        self.show()

    def CloseTab(self, i):
        self.tabbar.removeTab(i)
        del self.tabs[i]

    def AddTab(self):
        i = self.tabCount

        self.tabs.append(QWidget())
        self.tabs[i].layout = QVBoxLayout()
        self.tabs[i].layout.setContentsMargins(0, 0, 0, 0)

        # For tab switching
        self.tabs[i].setObjectName("tab" + str(i))

        # Open webview
        self.tabs[i].content = QWebEngineView()
        self.tabs[i].content.load(QUrl.fromUserInput("https://www.wikipedia.org/"))

        self.tabs[i].content.titleChanged.connect(lambda: self.SetTabContent(i, "title"))
        self.tabs[i].content.iconChanged.connect(lambda: self.SetTabContent(i, "icon"))
        self.tabs[i].content.urlChanged.connect(lambda: self.SetTabContent(i, "url"))

        # Add webview to tabs layout
        self.tabs[i].splitview = QSplitter()
        self.tabs[i].layout.addWidget(self.tabs[i].splitview)

        self.tabs[i].splitview.addWidget(self.tabs[i].content)

        # Set top level tab from [] to layout
        self.tabs[i].setLayout(self.tabs[i].layout)

        # Add tab to top level stacked widget
        self.container.layout.addWidget(self.tabs[i])
        self.container.layout.setCurrentWidget(self.tabs[i])

        # Create tab on tabbar, representing this tab
        # Set tabData to tab<#> so it knows what self.tabs[#] it needs to control
        self.tabbar.addTab("New Tab")
        self.tabbar.setTabData(i, {"object": "tab" + str(i), "initial": i})

        self.tabbar.setCurrentIndex(i)

        self.tabCount += 1

    def SwitchTab(self, i):
        if self.tabbar.tabData(i):
            tab_data = self.tabbar.tabData(i)["object"]
            tab_content = self.findChild(QWidget, tab_data)
            self.container.layout.setCurrentWidget(tab_content)
            new_url = tab_content.content.url().toString()
            self.addressbar.setText(new_url)

    def BrowseTo(self):
        text = self.addressbar.text()

        i = self.tabbar.currentIndex()
        tab = self.tabbar.tabData(i)["object"]
        webview = self.findChild(QWidget, tab).content

        if "http" not in text:
            if "." not in text:
                url = "https://en.wikipedia.org/w/index.php?search=" + text
            else:
                url = "http://" + text
        else:
            url = text

        webview.load(QUrl.fromUserInput(url))

    def SetTabContent(self, i, type):
        tab_name = self.tabs[i].objectName()

        count = 0
        running = True

        current_tab = self.tabbar.tabData(self.tabbar.currentIndex())["object"]

        if current_tab == tab_name and type == "url":
            new_url = self.findChild(QWidget, tab_name).content.url().toString()
            self.addressbar.setText(new_url)
            return False

        while running:
            tab_data_name = self.tabbar.tabData(count)

            if count >= 99:
                running = False

            if tab_name == tab_data_name["object"]:
                if type == "title":
                    newTitle = self.findChild(QWidget, tab_name).content.title()
                    self.tabbar.setTabText(count, newTitle)
                elif type == "icon":
                    newIcon = self.findChild(QWidget, tab_name).content.icon()
                    self.tabbar.setTabIcon(count, newIcon)

                running = False
            else:
                count += 1

    def GoBack(self):
        activeIndex = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(activeIndex)["object"]
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.back()

    def GoForward(self):
        activeIndex = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(activeIndex)["object"]
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.forward()

    def ReloadPage(self):
        activeIndex = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(activeIndex)["object"]
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.reload()


app = QApplication(sys.argv)
window = App()

with open("slr_style.css", "r") as style:
    app.setStyleSheet(style.read())

sys.exit(app.exec_())
