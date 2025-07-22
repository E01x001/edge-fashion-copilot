from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import os

class OutfitResultWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("OutfitResultWidget")
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.layout.setSpacing(18)

        # 제목 라벨
        self.title_label = QLabel("추천 코디")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: white; margin-bottom: 12px;")
        self.layout.addWidget(self.title_label)

        # 이미지 라벨 리스트
        self.image_labels = []

    def show_outfit_result(self, top_path, bottom_path, outer_path=None, shoes_path=None, accessory_path=None):
        # 필수 이미지 없으면 표시하지 않음
        if not (top_path and bottom_path):
            return

        # 이전 이미지 제거
        for lbl in self.image_labels:
            self.layout.removeWidget(lbl)
            lbl.deleteLater()
        self.image_labels.clear()

        # 이미지 경로 리스트 (순서대로)
        image_paths = [
            top_path,
            bottom_path,
            outer_path,
            shoes_path,
            accessory_path
        ]

        for path in image_paths:
            if path and os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    img_label = QLabel()
                    img_label.setAlignment(Qt.AlignCenter)
                    img_label.setPixmap(pixmap.scaledToWidth(200, Qt.SmoothTransformation))
                    img_label.setStyleSheet("margin-bottom: 8px;")
                    self.layout.addWidget(img_label)
                    self.image_labels.append(img_label)