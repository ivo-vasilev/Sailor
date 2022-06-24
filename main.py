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

import resources_rc


class AddressBar(QLineEdit):
    def __init__(self):
        super().__init__()

    def mousePressEvent(self, e):
        self.selectAll()


class App(QFrame):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sailor")
        self.setWindowIcon(QIcon(':/icons/sailor-logo-trans.png'))
        self.setMinimumSize(1200, 600)
        self.layout = None
        self.tabbar = None
        self.shortcutNewTab = None
        self.shortcutReload = None
        self.tabs = None
        self.tabCount = None
        self.Toolbar = None
        self.ToolbarLayout = None
        self.addressbar = None
        self.BackButton = None
        self.ForwardButton = None
        self.ReloadButton = None
        self.AddTabButton = None
        self.container = None
        self.create_app()

    def create_app(self):
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Create Tabs
        self.tabbar = QTabBar(movable=True, tabsClosable=True)
        self.tabbar.tabCloseRequested.connect(self.close_tab)
        self.tabbar.tabBarClicked.connect(self.switch_tab)
        self.tabbar.setCurrentIndex(0)
        self.tabbar.setDrawBase(False)
        self.tabbar.setLayoutDirection(Qt.LeftToRight)

        self.shortcutNewTab = QShortcut(QKeySequence("Ctrl+T"), self)
        self.shortcutNewTab.activated.connect(self.add_tab)

        self.shortcutReload = QShortcut(QKeySequence("Ctrl+R"), self)
        self.shortcutReload.activated.connect(self.reload_page)

        # Keep track of tabs
        self.tabCount = 0
        self.tabs = []

        # Create Address Bar
        self.Toolbar = QWidget()
        self.ToolbarLayout = QHBoxLayout()
        self.addressbar = AddressBar()
        self.addressbar.returnPressed.connect(self.browse_to)

        # Add toolbar buttons
        self.BackButton = QPushButton(QIcon(':/icons/back.png'), "")
        self.BackButton.clicked.connect(self.go_back)

        self.ForwardButton = QPushButton(QIcon(':/icons/forward.png'), "")
        self.ForwardButton.clicked.connect(self.go_forward)

        self.ReloadButton = QPushButton(QIcon(':/icons/reload.png'), "")
        self.ReloadButton.clicked.connect(self.reload_page)

        # Create the toolbar
        self.Toolbar.setLayout(self.ToolbarLayout)
        self.Toolbar.setObjectName("Toolbar")
        self.ToolbarLayout.addWidget(self.BackButton)
        self.ToolbarLayout.addWidget(self.ForwardButton)
        self.ToolbarLayout.addWidget(self.ReloadButton)
        self.ToolbarLayout.addWidget(self.addressbar)

        # New Tab button
        self.AddTabButton = QPushButton("+")
        self.AddTabButton.clicked.connect(self.add_tab)
        self.ToolbarLayout.addWidget(self.AddTabButton)

        # Set main view
        self.container = QWidget()
        self.container.layout = QStackedLayout()
        self.container.setLayout(self.container.layout)

        self.layout.addWidget(self.tabbar)
        self.layout.addWidget(self.Toolbar)
        self.layout.addWidget(self.container)

        self.setLayout(self.layout)

        self.add_tab()

        self.show()

    def close_tab(self, i):
        self.tabbar.removeTab(i)
        del self.tabs[i]

        # Find a way to display the content of the remaining tab!

    def add_tab(self):
        i = self.tabCount

        self.tabs.append(QWidget())
        self.tabs[i].layout = QVBoxLayout()
        self.tabs[i].layout.setContentsMargins(0, 0, 0, 0)

        # For tab switching
        self.tabs[i].setObjectName("tab" + str(i))

        # Open webview
        self.tabs[i].content = QWebEngineView()
        self.tabs[i].content.load(QUrl.fromUserInput("https://www.wikipedia.org/"))

        self.tabs[i].content.titleChanged.connect(lambda: self.set_tab_content(i, "title"))
        self.tabs[i].content.iconChanged.connect(lambda: self.set_tab_content(i, "icon"))
        self.tabs[i].content.urlChanged.connect(lambda: self.set_tab_content(i, "url"))

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

    def switch_tab(self, i):
        if self.tabbar.tabData(i):
            tab_data = self.tabbar.tabData(i)["object"]
            tab_content = self.findChild(QWidget, tab_data)
            self.container.layout.setCurrentWidget(tab_content)
            new_url = tab_content.content.url().toString()
            self.addressbar.setText(new_url)

    def browse_to(self):
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

    def set_tab_content(self, i, type):
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
                    new_title = self.findChild(QWidget, tab_name).content.title()
                    self.tabbar.setTabText(count, new_title)
                elif type == "icon":
                    new_icon = self.findChild(QWidget, tab_name).content.icon()
                    self.tabbar.setTabIcon(count, new_icon)

                running = False
            else:
                count += 1

    def go_back(self):
        active_index = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(active_index)["object"]
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.back()

    def go_forward(self):
        active_index = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(active_index)["object"]
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.forward()

    def reload_page(self):
        active_index = self.tabbar.currentIndex()
        tab_name = self.tabbar.tabData(active_index)["object"]
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.reload()


app = QApplication(sys.argv)
window = App()

with open("slr_style.css", "r") as style:
    app.setStyleSheet(style.read())

sys.exit(app.exec_())
