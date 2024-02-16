import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow
from UI import Ui_MainWindow
from request import generate_image, geosearch_controller


class Geo(QMainWindow, Ui_MainWindow):
    Scale = 17
    MAP_TYPE = {
        'Scheme': 'map',
        'Sputnik': 'sat',
        'Hybrid': 'sat,skl'
    }

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Яндекс.Карты')
        self.scheme.nextCheckState()

        self.map_type = Geo.MAP_TYPE['Scheme']
        self.org_name = None
        self.center_point = None
        self.scale = Geo.Scale

        self.buttonGroup.buttonClicked.connect(self.change_type_map)
        self.search.clicked.connect(self._search_btn_clicked)
        self.clear_btn.clicked.connect(self._clean_btn_clicked)

    def _search_btn_clicked(self):
        self.scale = Geo.Scale
        self.org_name = self.search_bar.text()
        self.org_point = geosearch_controller.get_ll_by_address(
            address=self.org_name
        )
        self.center_point = self.org_point
        self.take_picture()

    def _clean_btn_clicked(self):
        self.scale = Geo.Scale
        self.org_name = None
        self.search_bar.setText('')
        self.address.setText('')
        self.map.clear()

    def take_picture(self):
        try:
            generate_image(
                center_point=self.center_point,
                org_point=self.org_point,
                map_type=self.map_type,
                scale=self.scale,
            )
            self.pixmap = QPixmap('map.png')
            self.map.setPixmap(self.pixmap)
            self.address.setText(self.get_full_address())
        except Exception as e:
            # Обработка ошибки при загрузке изображения или получении адреса
            print(f"Error: {e}")

    def get_full_address(self):
        return geosearch_controller.get_full_address(
            address=self.org_name
        )

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.scale += 1
            self.scale_checker()
            self.take_picture()
        elif event.key() == Qt.Key_PageDown:
            self.scale -= 1
            self.scale_checker()
            self.take_picture()
        elif event.key() in [Qt.Key_Up, Qt.Key_Down, Qt.Key_Right, Qt.Key_Left]:
            self.update_center_point(event)
            self.scale_checker()
            self.take_picture()

    def update_center_point(self, event):
        longitude, latitude = map(float, self.center_point.split(','))
        move = {
            Qt.Key_Left: (-self.count_longitude(), 0),
            Qt.Key_Right: (self.count_longitude(), 0),
            Qt.Key_Down: (0, -self.count_latitude()),
            Qt.Key_Up: (0, self.count_latitude())
        }

        if event.key() in move:
            delta_longitude, delta_latitude = move[event.key()]
            new_longitude = max(-180, min(180, longitude + delta_longitude))
            new_latitude = max(-90, min(90, latitude + delta_latitude))
            self.center_point = f'{new_longitude},{new_latitude}'

    def scale_checker(self):
        self.scale = min(max(self.scale, 1), 17)

    def count_latitude(self):
        H = 450
        return 180 / (2 ** (self.scale + 8)) * H

    def count_longitude(self):
        W = 600
        return 360 / (2 ** (self.scale + 8)) * W

    def change_type_map(self):
        i = self.buttonGroup.checkedButton().text()
        if i == 'Карта':
            q = 'Scheme'
        elif i == 'Спутник':
            q = 'Sputnik'
        elif i == 'Гибрид':
            q = 'Hybrid'
        self.map_type = Geo.MAP_TYPE[q]
        print(i)
        if self.org_name:
            self.take_picture()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    geofinder = Geo()
    geofinder.show()
    sys.exit(app.exec())
