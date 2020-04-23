import requests
from bs4 import BeautifulSoup
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice, QLegend
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QPainter
from PyQt5.QtCore import Qt, QTranslator, QLocale, QLibraryInfo, pyqtSlot
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout,
                             QLabel, QComboBox, QSizePolicy, QCheckBox)


def request(country=""):
    if country == "":
        url = "https://www.worldometers.info/coronavirus/"
    else:
        url = "https://www.worldometers.info/coronavirus/country/" + country

    print(url)
    response = requests.get(url)
    html_content = response.content
    soup = BeautifulSoup(html_content, "html.parser")
    worldCases = []
    for i in soup.find_all("div", {"class": "maincounter-number"}):
        worldCases.append(i.text)
    return worldCases


class CircularGraphic(QWidget):
    def __init__(self, parent=None):
        super(CircularGraphic, self).__init__(parent)

        self.initUI()

    def initUI(self):
        self.m_themaComboBox = self.addThemaItem()
        self.m_labelComboBox = self.addLabelItem()
        self.m_indicatorMarkerComboBox = self.addIndicatorItem()
        self.m_countryComboBox = self.addCountryItem()
        self.m_showLabelCheckBox = QCheckBox("Show Label")

        chartView = QChartView(self.createGraphicCircular())
        chartView.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        chartView.setRenderHint(QPainter.Antialiasing, True)

        self.m_chartView = chartView

        designConfiguracion = QVBoxLayout()
        designConfiguracion.addWidget(QLabel("Thema:"))
        designConfiguracion.addWidget(self.m_themaComboBox)
        designConfiguracion.addWidget(QLabel("Label:"))
        designConfiguracion.addWidget(self.m_labelComboBox)
        designConfiguracion.addWidget(QLabel("Indicator Marker:"))
        designConfiguracion.addWidget(self.m_indicatorMarkerComboBox)
        designConfiguracion.addWidget(QLabel("Country:"))
        designConfiguracion.addWidget(self.m_countryComboBox)
        designConfiguracion.addWidget(self.m_showLabelCheckBox)
        designConfiguracion.addStretch()

        baseDesign = QGridLayout()
        baseDesign.addLayout(designConfiguracion, 0, 0, 0, 1)
        baseDesign.addWidget(chartView, 0, 1, 0, 4)

        self.setLayout(baseDesign)

        self.m_themaComboBox.currentIndexChanged.connect(self.updateUI)
        self.m_labelComboBox.currentIndexChanged.connect(self.updateUI)
        self.m_indicatorMarkerComboBox.currentIndexChanged.connect(self.updateUI)
        self.m_countryComboBox.currentIndexChanged.connect(self.createGraphicCircular)
        self.m_showLabelCheckBox.toggled.connect(self.updateUI)
        self.m_showLabelCheckBox.setChecked(True)
        self.updateUI()

    def addCountryItem(self):
        country = QComboBox()
        country.addItem("Turkey")
        country.addItem("Spain")
        return country

    def addThemaItem(self):
        thema = QComboBox()
        thema.addItem("LightTheme", QChart.ChartThemeLight)
        thema.addItem("DarkTheme", QChart.ChartThemeDark)
        return thema

    def addLabelItem(self):
        labelComboBox = QComboBox()
        labelComboBox.addItem("Top", Qt.AlignTop)
        labelComboBox.addItem("Bottom", Qt.AlignBottom)
        labelComboBox.addItem("Left", Qt.AlignLeft)
        labelComboBox.addItem("Right", Qt.AlignRight)
        return labelComboBox

    def addIndicatorItem(self):
        indicatorMarkerComboBox = QComboBox()
        indicatorMarkerComboBox.addItem("Rectangle", QLegend.MarkerShapeRectangle)
        indicatorMarkerComboBox.addItem("Circle", QLegend.MarkerShapeCircle)
        indicatorMarkerComboBox.addItem("Series",
                                        QLegend.MarkerShapeFromSeries)
        return indicatorMarkerComboBox

    def createGraphicCircular(self):
        country = str(self.m_countryComboBox.currentText())
        response = request(country)
        print(response)

        graphic = QChart()
        graphic.setTitle("World Corona Status")
        cases = float(response[0].strip().replace(",", ""))
        deaths = float(response[1].strip().replace(",", ""))
        recovered = float(response[2].strip().replace(",", ""))

        data_list = [("Cases:" + response[0], cases),
                     ("Deaths:" + response[1], deaths),
                     ("Recovered:" + response[2], recovered)]

        series = QPieSeries(graphic)
        for tag, valor in data_list:
            slice = series.append(tag, valor)

        graphic.addSeries(series)
        graphic.createDefaultAxes()

        return graphic

    @pyqtSlot()
    def updateUI(self):

        thema = self.m_themaComboBox.itemData(self.m_themaComboBox.currentIndex())

        if self.m_chartView.chart().theme() != thema:
            self.m_chartView.chart().setTheme(thema)

            pal = self.window().palette()

            if thema == QChart.ChartThemeLight:
                pal.setColor(QPalette.Window, QColor(0xf0f0f0))
                pal.setColor(QPalette.WindowText, QColor(0x404044))
            elif thema == QChart.ChartThemeDark:
                pal.setColor(QPalette.Window, QColor(0x121218))
                pal.setColor(QPalette.WindowText, QColor(0xd6d6d6))

            self.window().setPalette(pal)

        options = QChart.AnimationOptions(QChart.AllAnimations)

        if self.m_chartView.chart().animationOptions() != options:
            self.m_chartView.chart().setAnimationOptions(options)

        label = self.m_chartView.chart().legend()

        labelPosition = self.m_labelComboBox.itemData(self.m_labelComboBox.currentIndex())

        if labelPosition == 0:
            label.hide()
        else:
            label.setAlignment(Qt.Alignment(labelPosition))
            label.show()

        indicatorMarker = self.m_indicatorMarkerComboBox.itemData(
            self.m_indicatorMarkerComboBox.currentIndex())

        if label != indicatorMarker:
            label.setMarkerShape(indicatorMarker)

        showLabel = self.m_showLabelCheckBox.isChecked()
        self.m_chartView.chart().series()[0].setLabelsVisible(showLabel)


# ==================================================================

if __name__ == "__main__":
    import sys

    application = QApplication(sys.argv)
    translator = QTranslator(application)
    locale = QLocale.system().name()
    path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    translator.load("qtbase_%s" % locale, path)
    application.installTranslator(translator)

    font = QFont()
    font.setPointSize(10)
    application.setFont(font)

    window = QMainWindow()
    window.setWindowTitle("Corona App")
    window.setMinimumSize(900, 500)

    widget = CircularGraphic()

    window.setCentralWidget(widget)
    window.show()

    sys.exit(application.exec_())
