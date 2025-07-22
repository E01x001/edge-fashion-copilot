from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QFrame, QApplication, QTabWidget, QVBoxLayout, QPushButton, QListWidget, QListWidgetItem, QFileDialog, QDialog, QLabel, QCheckBox, QLineEdit, QGridLayout, QGroupBox, QComboBox, QSpinBox, QRadioButton, QButtonGroup, QTreeWidget, QTreeWidgetItem, QSizePolicy, QSplitter, QToolButton, QColorDialog, QSlider
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QIcon, QPixmap
import os
from src.ui.outfit_result_widget import OutfitResultWidget

# === 테마 색상 정의 ===
# 다크모드(현재)
DARK_THEME = {
    'DARK_BG': '#23243A',         # 전체 배경
    'CARD_BG': '#282A36',         # 카드/프레임/그룹박스 배경
    'ACCENT_PURPLE': '#6C63FF',   # 강조(테두리/버튼)
    'ACCENT_BLUE': '#4F8CFF',     # 버튼/포커스
    'ACCENT_YELLOW': '#FFE066',   # 포인트
    'TEXT_COLOR': '#E0E0E0',      # 메인 텍스트
    'BORDER_RADIUS': '12px',
    'SIDEBAR_BG': '#23243A',      # 사이드바/입력창 배경
    'SIDEBAR_TEXT': '#E0E0E0',    # 사이드바/라벨 텍스트
    'SIDEBAR_BTN_BG': '#353570',  # 버튼 배경
    'SIDEBAR_BTN_TEXT': '#E0E0E0',# 버튼 텍스트
    'ITEM_BG': '#282A36',         # 아이템/리스트 배경
    'INPUT_BG': '#2C2D3C',        # 입력창 배경
    'INPUT_TEXT': '#E0E0E0',      # 입력창 텍스트
    'INPUT_PLACEHOLDER': '#B0B0B0', # 입력창 placeholder
    'INPUT_BORDER': '#6C63FF',    # 입력창 테두리
}

# 기본(라이트) 모드: 이미지 참고
LIGHT_THEME = {
    'DARK_BG': '#E3F3FC',      # 전체 배경 (가장 밝은 하늘색)
    'CARD_BG': '#C7E4F5',      # 패널/박스 배경 (밝은 하늘색)
    'ACCENT_PURPLE': '#0077B6',
    'ACCENT_BLUE': '#0099CC',
    'ACCENT_YELLOW': '#FFD600',
    'TEXT_COLOR': '#222',
    'BORDER_RADIUS': '12px',
    'SIDEBAR_BG': '#B3DDF2',   # 사이드바/입력창 배경
    'SIDEBAR_TEXT': '#003344',
    'SIDEBAR_BTN_BG': '#0099CC',
    'SIDEBAR_BTN_TEXT': '#FFF',
    'ITEM_BG': '#E3F3FC',
    'INPUT_BG': '#FFFFFF',
    'INPUT_TEXT': '#222',
    'INPUT_PLACEHOLDER': '#888',
    'INPUT_BORDER': '#0099CC',
}

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
        self.setStyleSheet(f"background: {self.parent().theme['CARD_BG']}; color: {self.parent().theme['TEXT_COLOR']}; border-radius: {self.parent().theme['BORDER_RADIUS']};")
        layout = QVBoxLayout(self)
        content_layout = QHBoxLayout()

        # 좌측: 이미지 미리보기
        image_label = QLabel()
        pixmap = QPixmap(self.image_path)
        image_label.setPixmap(pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        image_label.setStyleSheet(f'background: {self.parent().theme["DARK_BG"]}; border-radius: 8px; border: 1px solid #444;')
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
            cb.setStyleSheet(f'color: {self.parent().theme["TEXT_COLOR"]};')
            combo = QComboBox()
            combo.addItems(items)
            combo.setCurrentText(self.ai_tags.get(category, items[0]))
            combo.setStyleSheet(f'padding: 4px; border-radius: 6px; border: 1px solid #444; background: {self.parent().theme["DARK_BG"]}; color: {self.parent().theme["TEXT_COLOR"]};')
            self.checkboxes[category] = cb
            self.comboboxes[category] = combo
            tag_layout.addWidget(cb, i, 0)
            tag_layout.addWidget(combo, i, 1)
        tag_widget.setLayout(tag_layout)
        content_layout.addWidget(tag_widget)

        layout.addLayout(content_layout)

        # 하단: 등록 버튼
        self.register_btn = QPushButton('등록')
        self.register_btn.setStyleSheet(f'padding: 10px 32px; background: {self.parent().theme["ACCENT_PURPLE"]}; color: white; border-radius: 8px; font-weight: bold;')
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

class TemperatureGauge(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(80)
        self.setFixedWidth(180)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.temp_label = QLabel("20°C")
        self.temp_label.setAlignment(Qt.AlignCenter)
        self.temp_label.setStyleSheet(
            f"""
            font-size: 28px;
            font-weight: bold;
            color: {parent.theme['ACCENT_BLUE'] if parent else '#4F8CFF'};
            """
        )
        layout.addWidget(self.temp_label)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(-30, 50)
        self.slider.setValue(20)
        self.slider.setTickInterval(10)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setStyleSheet(
            f"""
            QSlider::groove:horizontal {{
                border-radius: 8px;
                height: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {parent.theme['ACCENT_PURPLE'] if parent else '#6C63FF'},
                    stop:1 {parent.theme['ACCENT_BLUE'] if parent else '#4F8CFF'});
            }}
            QSlider::handle:horizontal {{
                background: {parent.theme['ACCENT_YELLOW'] if parent else '#FFE066'};
                border: 2px solid #fff;
                width: 18px;
                margin: -4px 0;
                border-radius: 9px;
            }}
            """
        )
        self.slider.valueChanged.connect(self.update_temp)
        layout.addWidget(self.slider)

    def update_temp(self, value):
        self.temp_label.setText(f"{value}°C")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.theme_mode = 'dark'
        self.theme = DARK_THEME.copy()
        self.setWindowTitle("3-분할 전체화면 윈도우")
        self.setGeometry(100, 100, 1200, 800)
        self.image_category_map = {}
        self.init_ui()

    def apply_theme(self):
        t = self.theme
        # 전체 배경
        palette = self.centralWidget().palette()
        palette.setColor(QPalette.Window, QColor(t['DARK_BG']))
        self.centralWidget().setAutoFillBackground(True)
        self.centralWidget().setPalette(palette)

        # 중앙 배경 프레임 색상 적용 (중앙/우측 패널 모두 밝은 하늘색으로 통일)
        self.center_bg_frame.setStyleSheet(f'background: {t["DARK_BG"]};')
        self.center_frame.setStyleSheet(f'background: {t["CARD_BG"]}; border-radius: {t["BORDER_RADIUS"]};')
        self.result_frame.setStyleSheet(f'background: {t["CARD_BG"]}; border-radius: {t["BORDER_RADIUS"]};')
        self.right_frame.setStyleSheet(f'background: {t["CARD_BG"]}; border-radius: {t["BORDER_RADIUS"]};')

        # 좌측 패널
        self.left_frame.setStyleSheet(f'background: {t["CARD_BG"]}; border-radius: {t["BORDER_RADIUS"]};')
        self.sidebar.setStyleSheet(f'background: {t["SIDEBAR_BG"]}; color: {t["SIDEBAR_TEXT"]}; border-radius: 8px; font-size: 15px; border: 2px solid {t["ACCENT_PURPLE"]};')
        self.sidebar_search.setStyleSheet(
            f'''
            QLineEdit {{
                padding: 6px 10px;
                border-radius: 8px;
                background: {t["INPUT_BG"]};
                color: {t["INPUT_TEXT"]};
                border: 2px solid {t["INPUT_BORDER"]};
                font-size: 15px;
            }}
            QLineEdit:placeholder {{
                color: {t["INPUT_PLACEHOLDER"]};
            }}
            '''
        )
        self.sidebar_toggle_btn.setStyleSheet(f'background: {t["SIDEBAR_BTN_BG"]}; color: {t["SIDEBAR_BTN_TEXT"]}; border-radius: 8px; font-size: 16px; padding: 4px 10px; font-weight: bold;')
        self.upload_button.setStyleSheet(f'padding: 12px 0; background: {t["ACCENT_BLUE"]}; color: #fff; border-radius: 8px; font-weight: bold; font-size: 15px; border: none;')
        self.image_list.setStyleSheet(f'background: {t["ITEM_BG"]}; border-radius: 10px; border: 2px solid {t["ACCENT_PURPLE"]}; color: {t["SIDEBAR_TEXT"]};')

        # "나의 옷장" 라벨
        self.closet_tab_label.setStyleSheet(
            f"""
            background: {t['CARD_BG']};
            color: {t['ACCENT_PURPLE']};
            border: 2px solid {t['ACCENT_PURPLE']};
            border-radius: 8px;
            font-size: 15px;
            padding: 4px 14px;
            margin-left: 8px;
            margin-top: 2px;
            font-weight: bold;
            """
        )

        # 우측 패널 그룹박스/폼 스타일
        for gb in self.right_frame.findChildren(QGroupBox):
            if '색상' in gb.title():
                gb.setStyleSheet(
                    f"""
                    QGroupBox {{
                        margin: 10px 0 0 0;
                        padding: 10px 16px 10px 16px;
                        border-radius: 10px;
                        border: 2px solid {t['ACCENT_YELLOW']};
                        background: {t['CARD_BG']};
                        color: #B8860B;
                        font-size: 16px;
                        font-weight: bold;
                    }}
                    QGroupBox:title {{
                        subcontrol-origin: margin;
                        subcontrol-position: top left;
                        left: 12px;
                        top: 6px;
                        padding: 0 4px;
                    }}
                    """
                )
            elif '상황' in gb.title():
                gb.setStyleSheet(
                    f"""
                    QGroupBox {{
                        margin: 10px 0 0 0;
                        padding: 10px 16px 10px 16px;
                        border-radius: 10px;
                        border: 2px solid {t['ACCENT_PURPLE']};
                        background: {t['CARD_BG']};
                        color: {t['ACCENT_PURPLE']};
                        font-size: 16px;
                        font-weight: bold;
                    }}
                    QGroupBox:title {{
                        subcontrol-origin: margin;
                        subcontrol-position: top left;
                        left: 12px;
                        top: 6px;
                        padding: 0 4px;
                    }}
                    """
                )
            elif '날씨' in gb.title():
                gb.setStyleSheet(
                    f"""
                    QGroupBox {{
                        margin: 10px 0 0 0;
                        padding: 10px 16px 10px 16px;
                        border-radius: 10px;
                        border: 2px solid {t['ACCENT_BLUE']};
                        background: {t['CARD_BG']};
                        color: {t['ACCENT_BLUE']};
                        font-size: 16px;
                        font-weight: bold;
                    }}
                    QGroupBox:title {{
                        subcontrol-origin: margin;
                        subcontrol-position: top left;
                        left: 12px;
                        top: 6px;
                        padding: 0 4px;
                    }}
                    """
                )
            elif '스타일' in gb.title():
                gb.setStyleSheet(
                    f"""
                    QGroupBox {{
                        margin: 10px 0 0 0;
                        padding: 10px 16px 10px 16px;
                        border-radius: 10px;
                        border: 2px solid {t['ACCENT_BLUE']};
                        background: {t['CARD_BG']};
                        color: {t['ACCENT_BLUE']};
                        font-size: 16px;
                        font-weight: bold;
                    }}
                    QGroupBox:title {{
                        subcontrol-origin: margin;
                        subcontrol-position: top left;
                        left: 12px;
                        top: 6px;
                        padding: 0 4px;
                    }}
                    """
                )
            else:
                gb.setStyleSheet(
                    f"""
                    QGroupBox {{
                        margin: 10px 0 0 0;
                        padding: 10px 16px 10px 16px;
                        border-radius: 10px;
                        border: 2px solid {t['ACCENT_PURPLE']};
                        background: {t['CARD_BG']};
                        color: {t['ACCENT_PURPLE']};
                        font-size: 16px;
                        font-weight: bold;
                    }}
                    QGroupBox:title {{
                        subcontrol-origin: margin;
                        subcontrol-position: top left;
                        left: 12px;
                        top: 6px;
                        padding: 0 4px;
                    }}
                    """
                )

        # 색상 선호도 관련 라벨/버튼
        label_widgets = self.right_frame.findChildren(QLabel)
        button_widgets = self.right_frame.findChildren(QPushButton)
        for widget in label_widgets + button_widgets:
            widget.setStyleSheet(
                f"""
                color: {t['TEXT_COLOR']};
                font-size: 15px;
                font-weight: bold;
                background: {t['CARD_BG']};
                border: none;
                """
            )

        # 콤보박스, 스핀박스, 라디오버튼 등
        for cb in self.right_frame.findChildren(QComboBox):
            cb.setStyleSheet(
                f'''
                QComboBox {{
                    padding: 8px;
                    border-radius: 6px;
                    background: {t["INPUT_BG"]};
                    color: {t["INPUT_TEXT"]};
                    border: 2px solid {t["INPUT_BORDER"]};
                    font-size: 15px;
                }}
                QComboBox QAbstractItemView {{
                    background: {t["CARD_BG"]};
                    color: {t["INPUT_TEXT"]};
                    selection-background-color: {t["ACCENT_PURPLE"]};
                }}
                '''
            )
        for sp in self.right_frame.findChildren(QSpinBox):
            sp.setStyleSheet(
                f'''
                QSpinBox {{
                    padding: 8px;
                    border-radius: 6px;
                    background: {t["INPUT_BG"]};
                    color: {t["INPUT_TEXT"]};
                    border: 2px solid {t["INPUT_BORDER"]};
                    font-size: 15px;
                }}
                '''
            )
        for rb in self.right_frame.findChildren(QRadioButton):
            rb.setStyleSheet(f'color: {t["TEXT_COLOR"]}; font-size: 15px; background: {t["CARD_BG"]};')

        # 우측 패널 하단 마진 추가
        self.right_frame.layout().setContentsMargins(22, 22, 22, 32)
        self.right_frame.layout().setSpacing(12)

    def init_ui(self):
        # 전체 배경색 설정
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 탭 위젯 선언
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)

        # 중앙 배경 프레임 추가
        self.center_bg_frame = QFrame()
        self.center_bg_frame.setObjectName("center_bg_frame")
        center_layout = QHBoxLayout(self.center_bg_frame)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        # 좌측 패널
        self.left_frame = QFrame()
        self.left_frame.setFrameShape(QFrame.StyledPanel)
        self.left_frame.setMinimumWidth(0)
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        # 사이드바 및 이미지 리스트 패널
        self.sidebar_search = QLineEdit()
        self.sidebar_search.setPlaceholderText('카테고리 검색...')
        self.sidebar_search.textChanged.connect(self.filter_sidebar)
        self.sidebar = QTreeWidget()
        self.sidebar.setHeaderHidden(True)
        self.populate_sidebar()
        self.sidebar.expandAll()
        self.sidebar.setMaximumWidth(180)
        self.sidebar.setMinimumWidth(0)
        self.sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.sidebar.itemClicked.connect(self.filter_images_by_category)

        # 토글버튼과 "나의 옷장" 라벨을 한 줄에 배치
        toggle_row = QHBoxLayout()
        self.sidebar_toggle_btn = QToolButton()
        self.sidebar_toggle_btn.setText('⮜')
        self.sidebar_toggle_btn.setCheckable(True)
        self.sidebar_toggle_btn.setChecked(False)
        self.sidebar_toggle_btn.clicked.connect(self.toggle_sidebar)
        toggle_row.addWidget(self.sidebar_toggle_btn, alignment=Qt.AlignLeft)

        self.closet_tab_label = QLabel("나의 옷장")
        self.closet_tab_label.setAlignment(Qt.AlignVCenter)
        toggle_row.addWidget(self.closet_tab_label, alignment=Qt.AlignLeft)
        toggle_row.addStretch(1)

        right_vbox = QVBoxLayout()
        right_vbox.setSpacing(10)
        right_vbox.addLayout(toggle_row)

        self.image_list = DraggableImageList(self)
        self.image_list.setViewMode(QListWidget.IconMode)
        self.image_list.setIconSize(QPixmap(100, 100).size())
        self.image_list.setResizeMode(QListWidget.Adjust)
        self.image_list.setSpacing(16)
        right_vbox.addWidget(self.image_list, 1)

        self.upload_button = QPushButton("이미지 업로드")
        self.upload_button.clicked.connect(self.upload_image)
        right_vbox.addWidget(self.upload_button, alignment=Qt.AlignBottom)

        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(6)
        sidebar_layout.addWidget(self.sidebar_search)
        sidebar_layout.addWidget(self.sidebar)
        sidebar_widget.setLayout(sidebar_layout)
        sidebar_widget.setMaximumWidth(180)
        sidebar_widget.setMinimumWidth(0)
        sidebar_widget.setStyleSheet('background: transparent;')
        right_widget = QWidget()
        right_widget.setLayout(right_vbox)
        self.splitter = QSplitter()
        self.splitter.addWidget(sidebar_widget)
        self.splitter.addWidget(right_widget)
        self.splitter.setSizes([180, 280])
        self.splitter.setCollapsible(0, True)
        self.splitter.setCollapsible(1, False)
        left_layout.addWidget(self.splitter)
        self.left_frame.setLayout(left_layout)

        # 중간 패널: OutfitResultWidget으로 교체
        self.center_frame = QFrame()
        self.center_frame.setFrameShape(QFrame.StyledPanel)
        self.center_frame.setMinimumWidth(0)
        center_layout2 = QVBoxLayout()
        center_layout2.setAlignment(Qt.AlignTop)
        center_layout2.setContentsMargins(40, 40, 40, 40)
        center_layout2.setSpacing(32)

        # OutfitResultWidget 생성 및 배치
        self.outfit_result_widget = OutfitResultWidget(self.center_frame)
        center_layout2.addWidget(self.outfit_result_widget)
        self.center_frame.setLayout(center_layout2)

        # 중앙 결과 프레임 (배경만)
        self.result_frame = QFrame()
        self.result_frame.setFrameShape(QFrame.StyledPanel)
        self.result_frame.setMinimumWidth(0)
        self.result_frame.setStyleSheet('border: none;')
        # 필요시 self.result_frame에 위젯 추가 가능

        # 우측 패널
        self.right_frame = QFrame()
        self.right_frame.setFrameShape(QFrame.StyledPanel)
        self.right_frame.setMinimumWidth(0)
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(22, 22, 22, 22)
        right_layout.setSpacing(22)
        # 상황
        situation_group = QGroupBox('상황')
        situation_group.setStyleSheet(f'QGroupBox {{ color: {self.theme["ACCENT_PURPLE"]}; font-weight: bold; border: 1.5px solid {self.theme["ACCENT_PURPLE"]}; border-radius: 8px; margin-top: 8px;}}')
        situation_layout = QVBoxLayout()
        self.situation_combo = QComboBox()
        self.situation_combo.addItems(['업무', '데이트', '운동', '일상', '파티'])
        self.situation_combo.setStyleSheet(f'padding: 8px; border-radius: 6px; background: {self.theme["SIDEBAR_BG"]}; color: {self.theme["SIDEBAR_TEXT"]};')
        situation_layout.addWidget(self.situation_combo)
        situation_group.setLayout(situation_layout)
        right_layout.addWidget(situation_group)
        # 날씨
        weather_group = QGroupBox('날씨')
        weather_group.setStyleSheet(f'QGroupBox {{ color: {self.theme["ACCENT_BLUE"]}; font-weight: bold; border: 1.5px solid {self.theme["ACCENT_BLUE"]}; border-radius: 8px; margin-top: 8px;}}')
        weather_layout = QVBoxLayout()
        self.weather_combo = QComboBox()
        self.weather_combo.addItems(['맑음', '흐림', '비', '눈'])
        self.weather_combo.setStyleSheet(f'padding: 8px; border-radius: 6px; background: {self.theme["SIDEBAR_BG"]}; color: {self.theme["SIDEBAR_TEXT"]};')
        weather_layout.addWidget(self.weather_combo)

        # 온도 게이지 추가
        self.temp_gauge = TemperatureGauge(self)
        weather_layout.addWidget(self.temp_gauge)

        weather_group.setLayout(weather_layout)
        right_layout.addWidget(weather_group)
        # 색상 선호도
        color_group = QGroupBox('색상 선호도')
        color_group.setStyleSheet(f'QGroupBox {{ color: {self.theme["ACCENT_YELLOW"]}; font-weight: bold; border: 1.5px solid {self.theme["ACCENT_YELLOW"]}; border-radius: 8px; margin-top: 8px;}}')
        color_layout = QGridLayout()
        # 좋아하는 색
        color_layout.addWidget(QLabel('좋아하는 색:'), 0, 0)
        self.like_colors = []
        self.like_color_box = QHBoxLayout()
        self.like_color_box.setSpacing(6)
        self.like_color_widget = QWidget()
        self.like_color_widget.setLayout(self.like_color_box)
        color_layout.addWidget(self.like_color_widget, 0, 1)
        self.like_color_add_btn = QPushButton('+')
        self.like_color_add_btn.setFixedWidth(28)
        self.like_color_add_btn.setStyleSheet(f'background: {self.theme["ACCENT_YELLOW"]}; color: {self.theme["SIDEBAR_BG"]}; border-radius: 8px; font-weight: bold;')
        self.like_color_add_btn.clicked.connect(lambda: self.add_color('like'))
        color_layout.addWidget(self.like_color_add_btn, 0, 2)
        # 피하는 색
        color_layout.addWidget(QLabel('피하는 색:'), 1, 0)
        self.avoid_colors = []
        self.avoid_color_box = QHBoxLayout()
        self.avoid_color_box.setSpacing(6)
        self.avoid_color_widget = QWidget()
        self.avoid_color_widget.setLayout(self.avoid_color_box)
        color_layout.addWidget(self.avoid_color_widget, 1, 1)
        self.avoid_color_add_btn = QPushButton('+')
        self.avoid_color_add_btn.setFixedWidth(28)
        self.avoid_color_add_btn.setStyleSheet(f'background: {self.theme["ACCENT_PURPLE"]}; color: white; border-radius: 8px; font-weight: bold;')
        self.avoid_color_add_btn.clicked.connect(lambda: self.add_color('avoid'))
        color_layout.addWidget(self.avoid_color_add_btn, 1, 2)
        color_group.setLayout(color_layout)
        right_layout.addWidget(color_group)
        # 스타일 선택
        style_group = QGroupBox('스타일 선택')
        style_group.setStyleSheet(f'QGroupBox {{ color: {self.theme["ACCENT_BLUE"]}; font-weight: bold; border: 1.5px solid {self.theme["ACCENT_BLUE"]}; border-radius: 8px; margin-top: 8px;}}')
        style_layout = QVBoxLayout()
        self.style_combo = QComboBox()
        self.style_combo.addItems(['캐주얼', '포멀', '스포티', '빈티지'])
        self.style_combo.setStyleSheet(f'padding: 8px; border-radius: 6px; background: {self.theme["SIDEBAR_BG"]}; color: {self.theme["SIDEBAR_TEXT"]};')
        style_layout.addWidget(self.style_combo)
        style_group.setLayout(style_layout)
        right_layout.addWidget(style_group)
        # 추천 우선순위
        priority_group = QGroupBox('추천 우선순위')
        priority_group.setStyleSheet(f'QGroupBox {{ color: {self.theme["ACCENT_PURPLE"]}; font-weight: bold; border: 1.5px solid {self.theme["ACCENT_PURPLE"]}; border-radius: 8px; margin-top: 8px;}}')
        priority_layout = QVBoxLayout()
        self.priority_color_radio = QRadioButton('색상 조합')
        self.priority_style_radio = QRadioButton('스타일 일관성')
        self.priority_color_radio.setChecked(True)
        self.priority_group = QButtonGroup()
        self.priority_group.addButton(self.priority_color_radio)
        self.priority_group.addButton(self.priority_style_radio)
        self.priority_color_radio.setStyleSheet(f'color: {self.theme["SIDEBAR_TEXT"]};')
        self.priority_style_radio.setStyleSheet(f'color: {self.theme["SIDEBAR_TEXT"]};')
        priority_layout.addWidget(self.priority_color_radio)
        priority_layout.addWidget(self.priority_style_radio)
        priority_group.setLayout(priority_layout)
        right_layout.addWidget(priority_group)
        # 하단: 코디 추천 버튼
        self.recommend_btn = QPushButton('코디 추천')
        self.recommend_btn.setStyleSheet(f'padding: 14px 0; background: {self.theme["ACCENT_PURPLE"]}; color: white; border-radius: 10px; font-weight: bold; font-size: 17px;')
        right_layout.addWidget(self.recommend_btn)
        right_layout.addStretch(1)
        self.right_frame.setLayout(right_layout)

        # 코디네이터 탭 레이아웃 선언 및 패널 배치
        coordinator_tab = QWidget()
        coordinator_layout = QHBoxLayout(coordinator_tab)
        coordinator_layout.setContentsMargins(0, 0, 0, 0)
        coordinator_layout.setSpacing(0)
        coordinator_layout.addWidget(self.left_frame, 20)
        coordinator_layout.addWidget(self.center_frame, 55)
        coordinator_layout.addWidget(self.right_frame, 25)
        coordinator_tab.setLayout(coordinator_layout)

        # 탭 추가
        style_analysis_tab = QWidget()
        self.tab_widget.addTab(coordinator_tab, "코디네이터")
        self.tab_widget.addTab(style_analysis_tab, "스타일 분석")
        # 설정 탭 추가
        settings_tab = QWidget()
        vbox = QVBoxLayout(settings_tab)
        vbox.addStretch(1)
        theme_label = QLabel('테마 선택:')
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['기본 모드', '다크 모드'])
        self.theme_combo.setCurrentIndex(1 if self.theme_mode == 'dark' else 0)
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        vbox.addWidget(theme_label)
        vbox.addWidget(self.theme_combo)
        vbox.addStretch(10)
        self.tab_widget.addTab(settings_tab, '설정')
        main_layout.addWidget(self.tab_widget)
        self.centralWidget().setLayout(main_layout)
        self.apply_theme()

    def on_theme_changed(self, idx):
        if idx == 0:
            self.theme_mode = 'light'
            self.theme = LIGHT_THEME.copy()
        else:
            self.theme_mode = 'dark'
            self.theme = DARK_THEME.copy()
        self.apply_theme()

    def upload_image(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_dialog.exec():
            file_names = file_dialog.selectedFiles()
            self.handle_image_files(file_names)
            # 업로드 후에도 현재 선택된 카테고리 필터 유지
            current_item = self.sidebar.currentItem()
            if current_item:
                self.filter_images_by_category(current_item, 0)

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
        selected_cat = item.text(0)
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

    def add_color(self, mode):
        color = QColorDialog.getColor()
        if color.isValid():
            hex_color = color.name()
            if mode == 'like' and hex_color not in self.like_colors:
                self.like_colors.append(hex_color)
                self.update_color_preview('like')
            elif mode == 'avoid' and hex_color not in self.avoid_colors:
                self.avoid_colors.append(hex_color)
                self.update_color_preview('avoid')

    def update_color_preview(self, mode):
        if mode == 'like':
            # 기존 위젯 제거
            for i in reversed(range(self.like_color_box.count())):
                self.like_color_box.itemAt(i).widget().deleteLater()
            # 새로 추가
            for c in self.like_colors:
                lbl = QLabel()
                lbl.setFixedSize(24, 24)
                lbl.setStyleSheet(f'background: {c}; border-radius: 12px; border: 2px solid #fff;')
                lbl.setToolTip(c)
                lbl.mousePressEvent = lambda e, color=c: self.remove_color('like', color)
                self.like_color_box.addWidget(lbl)
        elif mode == 'avoid':
            for i in reversed(range(self.avoid_color_box.count())):
                self.avoid_color_box.itemAt(i).widget().deleteLater()
            for c in self.avoid_colors:
                lbl = QLabel()
                lbl.setFixedSize(24, 24)
                lbl.setStyleSheet(f'background: {c}; border-radius: 12px; border: 2px solid #fff;')
                lbl.setToolTip(c)
                lbl.mousePressEvent = lambda e, color=c: self.remove_color('avoid', color)
                self.avoid_color_box.addWidget(lbl)

    def remove_color(self, mode, color):
        if mode == 'like':
            self.like_colors = [c for c in self.like_colors if c != color]
            self.update_color_preview('like')
        elif mode == 'avoid':
            self.avoid_colors = [c for c in self.avoid_colors if c != color]
            self.update_color_preview('avoid') 

    def populate_sidebar(self, filter_text=""):
        self.sidebar.clear()
        filter_text = filter_text.lower()
        for cat, items in CATEGORIES.items():
            if filter_text and filter_text not in cat.lower() and not any(filter_text in sub.lower() for sub in items):
                continue
            cat_item = QTreeWidgetItem([cat])
            for sub in items:
                if filter_text and filter_text not in sub.lower() and filter_text not in cat.lower():
                    continue
                sub_item = QTreeWidgetItem([sub])
                cat_item.addChild(sub_item)
            self.sidebar.addTopLevelItem(cat_item)

    def filter_sidebar(self, text):
        self.populate_sidebar(text)
        self.sidebar.expandAll()

    def change_temperature(self, delta):
        self.temp_spin.setValue(self.temp_spin.value() + delta)

    def on_recommend_clicked(self):
        # 예시: 이미지 경로를 실제 추천 결과에 맞게 전달
        # 실제 구현에서는 추천 알고리즘 결과를 받아서 경로를 전달해야 함
        top_path = "./images/top.png"
        bottom_path = "./images/bottom.png"
        outer_path = "./images/outer.png"
        shoes_path = "./images/shoes.png"
        accessory_path = "./images/belt.png"
        # 필수 이미지가 없으면 표시하지 않음
        if not (os.path.exists(top_path) and os.path.exists(bottom_path)):
            return
        self.outfit_result_widget.show_outfit_result(
            top_path, bottom_path, outer_path, shoes_path, accessory_path
        )