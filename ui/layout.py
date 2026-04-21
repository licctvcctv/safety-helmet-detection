"""构建主窗口全部控件和布局。"""
from pathlib import Path

from PySide6.QtCore import QByteArray, QSize, Qt, QTime, QTimer
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
)

from ui.widgets import ClickableLabel


ICON_ROOT = Path(__file__).resolve().parents[1] / "img" / "icons" / "svg"

H_SP = QSizePolicy.Expanding
V_SP = QSizePolicy.Minimum


def _frame(name):
    frame = QFrame()
    frame.setObjectName(name)
    return frame


def _label(name, text=""):
    label = QLabel(text)
    label.setObjectName(name)
    return label


def _load_svg(icon_name, color):
    svg_path = ICON_ROOT / f"{icon_name}.svg"
    svg_data = svg_path.read_text(encoding="utf-8")
    return QByteArray(svg_data.replace("currentColor", color).encode("utf-8"))


def _icon_pixmap(icon_name, size, color):
    renderer = QSvgRenderer(_load_svg(icon_name, color))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap


def _icon_label(name, icon_name, size=18, color="#EAF3FF", badge_size=None):
    badge_size = badge_size or size + 14
    label = _label(name)
    label.setAlignment(Qt.AlignCenter)
    label.setFixedSize(badge_size, badge_size)
    label.setPixmap(_icon_pixmap(icon_name, size, color))
    return label


def _set_button_icon(button, icon_name, size=18, color="#F8FBFF"):
    button.setIcon(QIcon(_icon_pixmap(icon_name, size, color)))
    button.setIconSize(QSize(size, size))
    button.setCursor(Qt.PointingHandCursor)


def _section(parent_lay, icon_name, title, content_fn):
    """创建一个带标题和圆角背景的 section 卡片。"""
    sec = _frame("sideSection")
    inner = QVBoxLayout(sec)
    inner.setContentsMargins(14, 14, 14, 14)
    inner.setSpacing(10)

    header = QHBoxLayout()
    header.setContentsMargins(0, 0, 0, 0)
    header.setSpacing(10)
    header.addWidget(_icon_label("sectionIcon", icon_name, size=14, color="#AFCBFF", badge_size=28))
    header.addWidget(_label("sideHeader", title))
    header.addStretch()
    inner.addLayout(header)

    content_fn(inner)
    parent_lay.addWidget(sec)
    return sec


# ─────────────────────────────────────────
#  标题栏
# ─────────────────────────────────────────
def _build_title_bar(win):
    bar = _frame("titleBar")
    bar.setFixedHeight(76)
    lay = QHBoxLayout(bar)
    lay.setContentsMargins(18, 14, 18, 14)
    lay.setSpacing(12)

    logo = _icon_label("logoBadge", "helmet", size=20, color="#F6FAFF", badge_size=44)
    lay.addWidget(logo)

    title_col = QVBoxLayout()
    title_col.setSpacing(2)
    title_col.setContentsMargins(0, 0, 0, 0)
    win.titleLabel = _label("titleLabel", "安全帽佩戴行为检测系统")
    sub = _label("titleSub", "Safety Helmet Wearing Detection | YOLOv7 + Transformer")
    title_col.addWidget(win.titleLabel)
    title_col.addWidget(sub)
    lay.addLayout(title_col)

    lay.addStretch()

    status_pill = _frame("statusPill")
    status_lay = QHBoxLayout(status_pill)
    status_lay.setContentsMargins(12, 7, 12, 7)
    status_lay.setSpacing(8)
    win._status_dot = _label("statusDot", "\u25cf")
    win._status_dot.setStyleSheet("color: #2aad5c;")
    win._status_label = _label("statusText", "就绪")
    status_lay.addWidget(win._status_dot)
    status_lay.addWidget(win._status_label)
    lay.addWidget(status_pill)

    time_pill = _frame("timePill")
    time_lay = QHBoxLayout(time_pill)
    time_lay.setContentsMargins(12, 7, 12, 7)
    time_lay.setSpacing(0)
    win._time_label = _label("timeLabel", "00:00:00")
    time_lay.addWidget(win._time_label)
    lay.addWidget(time_pill)

    timer = QTimer(win)
    timer.timeout.connect(
        lambda: win._time_label.setText(QTime.currentTime().toString("HH:mm:ss")))
    timer.start(1000)

    return bar


# ─────────────────────────────────────────
#  左侧面板
# ─────────────────────────────────────────
def _build_sidebar(win):
    sidebar = _frame("sidebar")
    sidebar.setFixedWidth(286)
    lay = QVBoxLayout(sidebar)
    lay.setContentsMargins(14, 14, 14, 14)
    lay.setSpacing(12)

    def file_ops(inner):
        win.folder = QPushButton("选择图片 / 视频")
        win.folder.setObjectName("folder")
        _set_button_icon(win.folder, "folder", size=16)

        win.importbtn = QPushButton("导入模型 (.pt)")
        win.importbtn.setObjectName("importbtn")
        _set_button_icon(win.importbtn, "upload", size=16)

        win.exporter = QPushButton("导出识别结果")
        win.exporter.setObjectName("exporter")
        _set_button_icon(win.exporter, "download", size=16)

        for btn in (win.folder, win.importbtn, win.exporter):
            btn.setFixedHeight(40)
            inner.addWidget(btn)

    _section(lay, "folder", "文件操作", file_ops)

    def model_params(inner):
        inner.addWidget(_label("paramLabel", "检测模型"))
        win.comboBox = QComboBox()
        win.comboBox.setObjectName("comboBox")
        win.comboBox.setFixedHeight(34)
        inner.addWidget(win.comboBox)

        inner.addSpacing(2)
        inner.addWidget(_label("paramLabel", "置信度 Confidence"))
        conf_row = QHBoxLayout()
        conf_row.setSpacing(8)
        win.con_num = QDoubleSpinBox()
        win.con_num.setObjectName("con_num")
        win.con_num.setRange(0, 1)
        win.con_num.setSingleStep(0.01)
        win.con_num.setDecimals(2)
        win.con_num.setValue(0.25)
        win.con_num.setFixedSize(68, 30)
        win.con_slider = QSlider(Qt.Horizontal)
        win.con_slider.setObjectName("con_slider")
        win.con_slider.setRange(0, 100)
        win.con_slider.setValue(25)
        conf_row.addWidget(win.con_num)
        conf_row.addWidget(win.con_slider, 1)
        inner.addLayout(conf_row)

        inner.addSpacing(2)
        inner.addWidget(_label("paramLabel", "交并比 IoU"))
        iou_row = QHBoxLayout()
        iou_row.setSpacing(8)
        win.iou_num = QDoubleSpinBox()
        win.iou_num.setObjectName("iou_num")
        win.iou_num.setRange(0, 1)
        win.iou_num.setSingleStep(0.01)
        win.iou_num.setDecimals(2)
        win.iou_num.setValue(0.40)
        win.iou_num.setFixedSize(68, 30)
        win.iou_slider = QSlider(Qt.Horizontal)
        win.iou_slider.setObjectName("iou_slider")
        win.iou_slider.setRange(0, 100)
        win.iou_slider.setValue(40)
        iou_row.addWidget(win.iou_num)
        iou_row.addWidget(win.iou_slider, 1)
        inner.addLayout(iou_row)

    _section(lay, "sliders", "模型参数", model_params)

    win.playbtn = QPushButton("开始检测")
    win.playbtn.setObjectName("playbtn")
    win.playbtn.setCheckable(True)
    win.playbtn.setFixedHeight(46)
    _set_button_icon(win.playbtn, "play", size=18)

    win.stopbtn = QPushButton("停止检测")
    win.stopbtn.setObjectName("stopbtn")
    win.stopbtn.setFixedHeight(40)
    _set_button_icon(win.stopbtn, "stop", size=16, color="#D9E6FB")

    lay.addWidget(win.playbtn)
    lay.addWidget(win.stopbtn)

    def results(inner):
        win.resultlist = QListWidget()
        win.resultlist.setObjectName("resultlist")
        inner.addWidget(win.resultlist)

    sec = _section(lay, "chart", "检测结果", results)
    lay.setStretchFactor(sec, 1)

    return sidebar


# ─────────────────────────────────────────
#  右侧主区域
# ─────────────────────────────────────────
def _view_card(win, obj_name, icon_name, title, meta_text, placeholder):
    card = _frame("viewCard")
    lay = QVBoxLayout(card)
    lay.setContentsMargins(14, 14, 14, 14)
    lay.setSpacing(12)

    header = QHBoxLayout()
    header.setContentsMargins(0, 0, 0, 0)
    header.setSpacing(10)
    header.addWidget(_icon_label("viewIconBadge", icon_name, size=16, color="#EAF3FF", badge_size=30))

    title_col = QVBoxLayout()
    title_col.setSpacing(2)
    title_col.setContentsMargins(0, 0, 0, 0)
    title_col.addWidget(_label("viewTitle", title))
    title_col.addWidget(_label("viewMeta", meta_text))
    header.addLayout(title_col)
    header.addStretch()
    lay.addLayout(header)

    label = ClickableLabel()
    label.setObjectName(obj_name)
    label.setAlignment(Qt.AlignCenter)
    label.setWordWrap(True)
    label.setText(placeholder)
    label.setMinimumSize(340, 240)
    setattr(win, obj_name, label)
    lay.addWidget(label, 1)

    return card


def _build_main_area(win):
    panel = _frame("viewPanel")
    lay = QVBoxLayout(panel)
    lay.setContentsMargins(14, 14, 14, 14)
    lay.setSpacing(12)

    views = QHBoxLayout()
    views.setSpacing(12)
    views.addWidget(_view_card(
        win,
        "input",
        "image",
        "原始画面",
        "支持图片与视频输入",
        "点击左侧“选择图片 / 视频”\n或直接点击此区域载入文件",
    ), 1)
    views.addWidget(_view_card(
        win,
        "output",
        "scan",
        "检测结果",
        "实时显示识别框与目标统计",
        "开始检测后\n识别结果会显示在这里",
    ), 1)
    lay.addLayout(views, 1)

    progress_frame = _frame("progressFrame")
    progress_lay = QVBoxLayout(progress_frame)
    progress_lay.setContentsMargins(14, 12, 14, 12)
    progress_lay.setSpacing(8)

    progress_head = QHBoxLayout()
    progress_head.setContentsMargins(0, 0, 0, 0)
    progress_head.setSpacing(8)
    progress_head.addWidget(_label("progressTitle", "推理进度"))
    progress_head.addStretch()
    win.progressValue = _label("progressValue", "0%")
    progress_head.addWidget(win.progressValue)
    progress_lay.addLayout(progress_head)

    win.progressBar = QProgressBar()
    win.progressBar.setObjectName("progressBar")
    win.progressBar.setMaximum(1000)
    win.progressBar.setValue(0)
    win.progressBar.setTextVisible(False)
    progress_lay.addWidget(win.progressBar)
    lay.addWidget(progress_frame)

    return panel


# ─────────────────────────────────────────
#  组装
# ─────────────────────────────────────────
def setup_ui(win):
    """在 QWidget 上构建全部界面。"""
    central = QFrame(win)
    central.setObjectName("central")
    root = QVBoxLayout(win)
    root.setContentsMargins(0, 0, 0, 0)
    root.setSpacing(0)
    root.addWidget(central)

    main_lay = QVBoxLayout(central)
    main_lay.setContentsMargins(0, 0, 0, 0)
    main_lay.setSpacing(0)

    main_lay.addWidget(_build_title_bar(win))

    body = QHBoxLayout()
    body.setContentsMargins(0, 0, 0, 0)
    body.setSpacing(0)
    body.addWidget(_build_sidebar(win))
    body.addWidget(_build_main_area(win), 1)
    main_lay.addLayout(body, 1)

    status = _frame("statusBar")
    status.setFixedHeight(34)
    status_lay = QHBoxLayout(status)
    status_lay.setContentsMargins(14, 0, 14, 0)
    status_lay.setSpacing(10)
    win.outputbox = _label("outputbox", "就绪")
    status_lay.addWidget(win.outputbox)
    status_lay.addStretch()
    status_lay.addWidget(_label("footerRight", "Safety Helmet Detection v1.1 | SVG UI"))
    main_lay.addWidget(status)
