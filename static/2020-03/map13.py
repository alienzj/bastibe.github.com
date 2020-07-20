import sys
import json
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

class WorldMap(QtWidgets.QGraphicsView):
    currentCountry = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self.setMinimumSize(360, 180)
        self.setMouseTracking(True)
        self.previous_item = None

    def mouseMoveEvent(self, event):
        item = self.itemAt(event.pos())
        if self.previous_item is not None:
            self.previous_item.setBrush(QtGui.QBrush("white", QtCore.Qt.BrushStyle.SolidPattern))
            self.previous_item = None
        if item is not None:
            item.setBrush(QtGui.QBrush("red", QtCore.Qt.BrushStyle.SolidPattern))
            self.previous_item = item
            self.currentCountry.emit(item.country)

    def resizeEvent(self, event):
        scene_size = self.sceneRect()
        dx = (self.width()-4)/scene_size.width()
        dy = (self.height()-4)/scene_size.height()
        self.setTransform(QtGui.QTransform.fromScale(dx, -dy))

    def sizeHint(self):
        return QtCore.QSize(360*2, 180*2)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.status_bar = self.statusBar()

        ocean_brush = QtGui.QBrush("lightblue", QtCore.Qt.BrushStyle.SolidPattern)
        country_pen = QtGui.QPen("grey")
        country_pen.setWidthF(0.5)
        land_brush = QtGui.QBrush("white", QtCore.Qt.BrushStyle.SolidPattern)

        scene = QtWidgets.QGraphicsScene(-180, -90, 360, 180)

        map_data = self.load_map_data()
        for country, polygons in map_data.items():
            for polygon in polygons:
                qpolygon = QtGui.QPolygonF()
                for x, y in polygon:
                    qpolygon.append(QtCore.QPointF(x, y))
                polygon_item = scene.addPolygon(qpolygon, pen=country_pen, brush=land_brush)
                polygon_item.country = country
        scene.setBackgroundBrush(ocean_brush)

        world_map = WorldMap()
        world_map.setScene(scene)
        world_map.setRenderHint(QtGui.QPainter.Antialiasing)
        world_map.currentCountry.connect(self.status_bar.showMessage)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(world_map)

        window_content = QtWidgets.QWidget()
        window_content.setLayout(layout)
        self.setCentralWidget(window_content)

        self.covid_data = pandas.read_csv('data/covid19.csv')

    def load_map_data(self):
        with open('countries_110m.json', 'rt') as f:
            data = json.load(f)

        return data


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())