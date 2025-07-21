from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QFrame, QApplication, QTabWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem, QFileDialog, QDialog, QLabel, QCheckBox, QLineEdit, QGridLayout, QGroupBox, QComboBox, QSpinBox, QRadioButton, QButtonGroup, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QSizePolicy, QSplitter, QToolButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QIcon, QPixmap
import os

DARK_BG = "#23234f"
CARD_BG = "#282a36"
ACCENT_PURPLE = "#7c5cff"
ACCENT_BLUE = "#4f8cff"
ACCENT_YELLOW = "#ffe066"
TEXT_COLOR = "#f4f4f4"
BORDER_RADIUS = "12px"

CATEGORIES = {
    "상의": ["티셔츠", "셔츠", "블라우스", "후드티", "맨투맨"],
    "하의": ["청바지", "슬랙스", "치마", "반바지", "레깅스"],
    "아우터": ["재킷", "코트", "패딩", "가디건", "조끼"],
    "신발": ["운동화", "구두", "부츠", "샌들", "슬리퍼"],
    "액세서리": ["모자", "가방", "벨트", "목도리"]
}

class ImageTagDialog(QDialog):
    def __init__(self, image_path, ai_tags=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("이미지 태그 등록")
        self.setModal(True)
        self.resize(500, 400)
        self.image_path = image_path
        # ai_tags는 {카테고리: 하위항목} 형식
        self.ai_tags = ai_tags or {cat: items[0] for cat, items in CATEGORIES.items()}
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(f"background: {CARD_BG}; color: {TEXT_COLOR}; border-radius: {BORDER_RADIUS};")
        layout = QVBoxLayout(self)
        content_layout = QHBoxLayout()

        # 좌측: 이미지 미리보기
        image_label = QLabel()
        pixmap = QPixmap(self.image_path)
        image_label.setPixmap(pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        image_label.setStyleSheet(f'background: {DARK_BG}; border-radius: 8px; border: 1px solid #444;')
        content_layout.addWidget(image_label)

        # 우측: 카테고리별 QComboBox (분류 적용)
        tag_widget = QWidget()
        tag_layout = QGridLayout()
        tag_layout.setColumnStretch(1, 1)
        self.checkboxes = {}
        self.comboboxes = {}
        for i, (category, items) in enumerate(CATEGORIES.items()):
            cb = QCheckBox(category)
            cb.setChecked(True)
            cb.setStyleSheet(f'color: {TEXT_COLOR};')
            combo = QComboBox()
            combo.addItems(items)
            combo.setCurrentText(self.ai_tags.get(category, items[0]))
            combo.setStyleSheet(f'padding: 4px; border-radius: 6px; border: 1px solid #444; background: {DARK_BG}; color: {TEXT_COLOR};')
            self.checkboxes[category] = cb
            self.comboboxes[category] = combo
            tag_layout.addWidget(cb, i, 0)
            tag_layout.addWidget(combo, i, 1)
        tag_widget.setLayout(tag_layout)
        content_layout.addWidget(tag_widget)

        layout.addLayout(content_layout)

        # 하단: 등록 버튼
        self.register_btn = QPushButton('등록')
        self.register_btn.setStyleSheet(f'padding: 10px 32px; background: {ACCENT_PURPLE}; color: white; border-radius: 8px; font-weight: bold;')
        self.register_btn.clicked.connect(self.accept)
        layout.addWidget(self.register_btn, alignment=Qt.AlignRight)

    def get_tags(self):
        # 체크된 항목만 반환, {카테고리: 하위항목}
        return {cat: self.comboboxes[cat].currentText() for cat in CATEGORIES if self.checkboxes[cat].isChecked()}

class DraggableImageList(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.parent_window = parent

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_paths = [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]
            self.parent_window.handle_image_files(file_paths)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3-분할 전체화면 윈도우")
        self.setGeometry(100, 100, 1200, 800)
        self.image_category_map = {}  # {image_path: category}
        self.init_ui()

    def init_ui(self):
        # 전체 배경색 설정
        central_widget = QWidget(self)
        palette = central_widget.palette()
        palette.setColor(QPalette.Window, QColor(DARK_BG))
        central_widget.setAutoFillBackground(True)
        central_widget.setPalette(palette)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        tab_widget = QTabWidget()
        tab_widget.setTabPosition(QTabWidget.North)
        tab_widget.setStyleSheet(f'''
            QTabBar::tab {{ min-width: 120px; min-height: 36px; font-size: 15px; border-radius: 12px 12px 0 0; background: {CARD_BG}; color: {TEXT_COLOR}; margin-right: 2px; }}
            QTabBar::tab:selected {{ background: {ACCENT_PURPLE}; color: white; }}
            QTabWidget::pane {{ border: none; }}
        ''')

        # '코디네이터' 탭
        coordinator_tab = QWidget()
        coordinator_layout = QHBoxLayout()
        coordinator_layout.setContentsMargins(0, 0, 0, 0)
        coordinator_layout.setSpacing(0)

        # 좌측 패널
        left_frame = QFrame()
        left_frame.setFrameShape(QFrame.StyledPanel)
        left_frame.setMinimumWidth(0)
        left_frame.setStyleSheet(f'background: {CARD_BG}; border-radius: {BORDER_RADIUS};')
        left_layout = QHBoxLayout()
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(10)
        # 사이드바(카테고리)
        self.sidebar = QTreeWidget()
        self.sidebar.setHeaderHidden(True)
        self.sidebar.setStyleSheet(f'background: {DARK_BG}; color: {TEXT_COLOR}; border-radius: 8px; font-size: 15px;')
        for cat, items in CATEGORIES.items():
            cat_item = QTreeWidgetItem([cat])
            for sub in items:
                sub_item = QTreeWidgetItem([sub])
                cat_item.addChild(sub_item)
            self.sidebar.addTopLevelItem(cat_item)
        self.sidebar.expandAll()
        self.sidebar.setMaximumWidth(140)
        self.sidebar.setMinimumWidth(0)
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.sidebar.itemClicked.connect(self.filter_images_by_category)
        # 사이드바 토글 버튼
        self.sidebar_toggle_btn = QToolButton()
        self.sidebar_toggle_btn.setText('⮜')
        self.sidebar_toggle_btn.setCheckable(True)
        self.sidebar_toggle_btn.setChecked(False)
        self.sidebar_toggle_btn.setStyleSheet(f'background: {ACCENT_PURPLE}; color: white; border-radius: 8px; font-size: 16px; padding: 4px 10px;')
        self.sidebar_toggle_btn.clicked.connect(self.toggle_sidebar)
        # 이미지 업로드/리스트 영역
        right_vbox = QVBoxLayout()
        right_vbox.setSpacing(10)
        right_vbox.addWidget(self.sidebar_toggle_btn, alignment=Qt.AlignLeft)
        self.upload_button = QPushButton("이미지 업로드")
        self.upload_button.setStyleSheet(f'padding: 12px 0; background: {ACCENT_BLUE}; color: white; border-radius: 8px; font-weight: bold; font-size: 15px;')
        self.upload_button.clicked.connect(self.upload_image)
        right_vbox.addWidget(self.upload_button)
        self.image_list = DraggableImageList(self)
        self.image_list.setViewMode(QListWidget.IconMode)
        self.image_list.setIconSize(QPixmap(100, 100).size())
        self.image_list.setResizeMode(QListWidget.Adjust)
        self.image_list.setSpacing(16)
        self.image_list.setStyleSheet(f'background: {DARK_BG}; border-radius: 10px; border: 1px solid #353570; color: {TEXT_COLOR};')
        right_vbox.addWidget(self.image_list, 1)
        # 좌우 배치(QSplitter로 감싸서 사이드바 열고 닫기)
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.addWidget(self.sidebar)
        sidebar_widget.setLayout(sidebar_layout)
        sidebar_widget.setMaximumWidth(140)
        sidebar_widget.setMinimumWidth(0)
        sidebar_widget.setStyleSheet('background: transparent;')
        right_widget = QWidget()
        right_widget.setLayout(right_vbox)
        self.splitter = QSplitter()
        self.splitter.addWidget(sidebar_widget)
        self.splitter.addWidget(right_widget)
        self.splitter.setSizes([140, 320])
        self.splitter.setCollapsible(0, True)
        self.splitter.setCollapsible(1, False)
        left_layout.addWidget(self.splitter)
        left_frame.setLayout(left_layout)

        # 중간 패널
        center_frame = QFrame()
        center_frame.setFrameShape(QFrame.StyledPanel)
        center_frame.setMinimumWidth(0)
        center_frame.setStyleSheet(f'background: {CARD_BG}; border-radius: {BORDER_RADIUS};')
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignTop)
        center_layout.setContentsMargins(40, 40, 40, 40)
        center_layout.setSpacing(32)
        self.top_label = QLabel()
        self.top_label.setAlignment(Qt.AlignCenter)
        self.top_label.setFixedSize(220, 220)
        self.top_label.setStyleSheet(f'background: {DARK_BG}; border-radius: 16px; border: 2px solid {ACCENT_PURPLE}; font-size: 18px; color: {TEXT_COLOR};')
        center_layout.addWidget(self.top_label)
        self.bottom_label = QLabel()
        self.bottom_label.setAlignment(Qt.AlignCenter)
        self.bottom_label.setFixedSize(220, 220)
        self.bottom_label.setStyleSheet(f'background: {DARK_BG}; border-radius: 16px; border: 2px solid {ACCENT_BLUE}; font-size: 18px; color: {TEXT_COLOR};')
        center_layout.addWidget(self.bottom_label)
        self.shoes_label = QLabel()
        self.shoes_label.setAlignment(Qt.AlignCenter)
        self.shoes_label.setFixedSize(220, 220)
        self.shoes_label.setStyleSheet(f'background: {DARK_BG}; border-radius: 16px; border: 2px solid {ACCENT_YELLOW}; font-size: 18px; color: {TEXT_COLOR};')
        center_layout.addWidget(self.shoes_label)
        center_frame.setLayout(center_layout)

        # 우측 패널
        right_frame = QFrame()
        right_frame.setFrameShape(QFrame.StyledPanel)
        right_frame.setMinimumWidth(0)
        right_frame.setStyleSheet(f'background: {CARD_BG}; border-radius: {BORDER_RADIUS};')
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(22, 22, 22, 22)
        right_layout.setSpacing(22)
        # 상황
        situation_group = QGroupBox('상황')
        situation_group.setStyleSheet(f'QGroupBox {{ color: {ACCENT_PURPLE}; font-weight: bold; border: 1.5px solid {ACCENT_PURPLE}; border-radius: 8px; margin-top: 8px;}}')
        situation_layout = QVBoxLayout()
        self.situation_combo = QComboBox()
        self.situation_combo.addItems(['업무', '데이트', '운동', '일상', '파티'])
        self.situation_combo.setStyleSheet(f'padding: 8px; border-radius: 6px; background: {DARK_BG}; color: {TEXT_COLOR};')
        situation_layout.addWidget(self.situation_combo)
        situation_group.setLayout(situation_layout)
        right_layout.addWidget(situation_group)
        # 날씨
        weather_group = QGroupBox('날씨')
        weather_group.setStyleSheet(f'QGroupBox {{ color: {ACCENT_BLUE}; font-weight: bold; border: 1.5px solid {ACCENT_BLUE}; border-radius: 8px; margin-top: 8px;}}')
        weather_layout = QHBoxLayout()
        self.weather_combo = QComboBox()
        self.weather_combo.addItems(['맑음', '흐림', '비', '눈'])
        self.weather_combo.setStyleSheet(f'padding: 8px; border-radius: 6px; background: {DARK_BG}; color: {TEXT_COLOR};')
        weather_layout.addWidget(self.weather_combo)
        self.temp_spin = QSpinBox()
        self.temp_spin.setRange(-30, 50)
        self.temp_spin.setSuffix('°C')
        self.temp_spin.setValue(20)
        self.temp_spin.setStyleSheet(f'padding: 8px; border-radius: 6px; background: {DARK_BG}; color: {TEXT_COLOR};')
        weather_layout.addWidget(QLabel('온도:'))
        weather_layout.addWidget(self.temp_spin)
        weather_group.setLayout(weather_layout)
        right_layout.addWidget(weather_group)
        # 색상 선호도
        color_group = QGroupBox('색상 선호도')
        color_group.setStyleSheet(f'QGroupBox {{ color: {ACCENT_YELLOW}; font-weight: bold; border: 1.5px solid {ACCENT_YELLOW}; border-radius: 8px; margin-top: 8px;}}')
        color_layout = QGridLayout()
        color_layout.addWidget(QLabel('좋아하는 색:'), 0, 0)
        self.like_color_edit = QLineEdit()
        self.like_color_edit.setStyleSheet(f'padding: 6px; border-radius: 6px; border: 1px solid #444; background: {DARK_BG}; color: {TEXT_COLOR};')
        color_layout.addWidget(self.like_color_edit, 0, 1)
        color_layout.addWidget(QLabel('피하는 색:'), 1, 0)
        self.avoid_color_edit = QLineEdit()
        self.avoid_color_edit.setStyleSheet(f'padding: 6px; border-radius: 6px; border: 1px solid #444; background: {DARK_BG}; color: {TEXT_COLOR};')
        color_layout.addWidget(self.avoid_color_edit, 1, 1)
        color_group.setLayout(color_layout)
        right_layout.addWidget(color_group)
        # 스타일 선택
        style_group = QGroupBox('스타일 선택')
        style_group.setStyleSheet(f'QGroupBox {{ color: {ACCENT_BLUE}; font-weight: bold; border: 1.5px solid {ACCENT_BLUE}; border-radius: 8px; margin-top: 8px;}}')
        style_layout = QVBoxLayout()
        self.style_combo = QComboBox()
        self.style_combo.addItems(['캐주얼', '포멀', '스포티', '빈티지'])
        self.style_combo.setStyleSheet(f'padding: 8px; border-radius: 6px; background: {DARK_BG}; color: {TEXT_COLOR};')
        style_layout.addWidget(self.style_combo)
        style_group.setLayout(style_layout)
        right_layout.addWidget(style_group)
        # 추천 우선순위
        priority_group = QGroupBox('추천 우선순위')
        priority_group.setStyleSheet(f'QGroupBox {{ color: {ACCENT_PURPLE}; font-weight: bold; border: 1.5px solid {ACCENT_PURPLE}; border-radius: 8px; margin-top: 8px;}}')
        priority_layout = QVBoxLayout()
        self.priority_color_radio = QRadioButton('색상 조합')
        self.priority_style_radio = QRadioButton('스타일 일관성')
        self.priority_color_radio.setChecked(True)
        self.priority_group = QButtonGroup()
        self.priority_group.addButton(self.priority_color_radio)
        self.priority_group.addButton(self.priority_style_radio)
        self.priority_color_radio.setStyleSheet(f'color: {TEXT_COLOR};')
        self.priority_style_radio.setStyleSheet(f'color: {TEXT_COLOR};')
        priority_layout.addWidget(self.priority_color_radio)
        priority_layout.addWidget(self.priority_style_radio)
        priority_group.setLayout(priority_layout)
        right_layout.addWidget(priority_group)
        # 하단: 코디 추천 버튼
        self.recommend_btn = QPushButton('코디 추천')
        self.recommend_btn.setStyleSheet(f'padding: 14px 0; background: {ACCENT_PURPLE}; color: white; border-radius: 10px; font-weight: bold; font-size: 17px;')
        right_layout.addWidget(self.recommend_btn)
        right_layout.addStretch(1)
        right_frame.setLayout(right_layout)

        coordinator_layout.addWidget(left_frame, 20)
        coordinator_layout.addWidget(center_frame, 55)
        coordinator_layout.addWidget(right_frame, 25)
        coordinator_tab.setLayout(coordinator_layout)

        style_analysis_tab = QWidget()
        tab_widget.addTab(coordinator_tab, "코디네이터")
        tab_widget.addTab(style_analysis_tab, "스타일 분석")
        main_layout.addWidget(tab_widget)
        central_widget.setLayout(main_layout)

        self.recommend_btn.clicked.connect(self.show_sample_outfit)

    def upload_image(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_dialog.exec():
            file_names = file_dialog.selectedFiles()
            self.handle_image_files(file_names)

    def handle_image_files(self, file_names):
        for file_path in file_names:
            tag_dialog = ImageTagDialog(file_path, parent=self)
            if tag_dialog.exec() == QDialog.Accepted:
                tags = tag_dialog.get_tags()  # {카테고리: 하위항목}
                main_cat = next(iter(tags.keys()), None)
                self.image_category_map[file_path] = main_cat
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    icon = QIcon(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    item = QListWidgetItem(icon, "")
                    item.setToolTip(f"{file_path}\n{tags}")
                    item.setData(Qt.UserRole, main_cat)
                    self.image_list.addItem(item)

    def filter_images_by_category(self, item, column):
        # 카테고리/하위항목 클릭 시 해당 카테고리의 이미지만 표시
        selected_cat = item.text(0)
        # 상위 카테고리 클릭 시 하위까지 모두 포함
        cats = [selected_cat]
        if item.childCount() > 0:
            cats = [item.child(i).text(0) for i in range(item.childCount())]
        self.image_list.clear()
        for path, cat in self.image_category_map.items():
            if cat in cats or selected_cat == cat:
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    icon = QIcon(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    item = QListWidgetItem(icon, "")
                    item.setToolTip(path)
                    self.image_list.addItem(item)

    def show_sample_outfit(self):
        base_dir = os.path.join(os.path.dirname(__file__), '../../images')
        top_img = os.path.abspath(os.path.join(base_dir, 'sample_top.jpg'))
        bottom_img = os.path.abspath(os.path.join(base_dir, 'sample_bottom.jpg'))
        shoes_img = os.path.abspath(os.path.join(base_dir, 'sample_shoes.jpg'))
        if os.path.exists(top_img):
            self.top_label.setPixmap(QPixmap(top_img).scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.top_label.setText('상의')
        if os.path.exists(bottom_img):
            self.bottom_label.setPixmap(QPixmap(bottom_img).scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.bottom_label.setText('하의')
        if os.path.exists(shoes_img):
            self.shoes_label.setPixmap(QPixmap(shoes_img).scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.shoes_label.setText('신발')

    def toggle_sidebar(self):
        sidebar_widget = self.splitter.widget(0)
        if self.sidebar_toggle_btn.isChecked():
            sidebar_widget.hide()
            self.sidebar_toggle_btn.setText('⮞')
        else:
            sidebar_widget.show()
            self.sidebar_toggle_btn.setText('⮜')
        # 사이즈 재조정
        self.splitter.setSizes([0 if self.sidebar_toggle_btn.isChecked() else 140, 320]) 