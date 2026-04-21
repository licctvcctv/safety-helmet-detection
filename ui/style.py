DARK_STYLE = """
QWidget#central {
    background-color: #09111d;
}

QLabel, QPushButton, QComboBox, QDoubleSpinBox, QListWidget {
    font-family: "Microsoft YaHei UI", "PingFang SC", "Segoe UI", sans-serif;
}

/* ---- 标题栏 ---- */
QFrame#titleBar {
    background-color: #0c1523;
    border-bottom: 1px solid #1a2940;
}

QLabel#logoBadge {
    background-color: #14304e;
    border: 1px solid #28507a;
    border-radius: 12px;
}

QLabel#titleLabel {
    font-size: 17pt;
    font-weight: 700;
    color: #eff5ff;
}

QLabel#titleSub {
    font-size: 9pt;
    color: #7c8ca6;
    letter-spacing: 0.4px;
}

QFrame#statusPill, QFrame#timePill {
    background-color: #101b2b;
    border: 1px solid #20314a;
    border-radius: 14px;
}

QLabel#statusDot {
    font-size: 10pt;
}

QLabel#statusText {
    font-size: 9pt;
    font-weight: 600;
    color: #dce6f7;
}

QLabel#timeLabel {
    font-size: 9pt;
    font-weight: 600;
    color: #9fb0ca;
    font-family: "Consolas", "SF Mono", "Menlo", monospace;
}

/* ---- 左侧面板 ---- */
QFrame#sidebar {
    background-color: #0e1727;
    border-right: 1px solid #1a2940;
}

QFrame#sideSection {
    background-color: #111d2e;
    border: 1px solid #1f314d;
    border-radius: 16px;
}

QLabel#sectionIcon {
    background-color: #15263d;
    border: 1px solid #2c4568;
    border-radius: 10px;
}

QLabel#sideHeader {
    font-size: 11pt;
    font-weight: 700;
    color: #ecf3ff;
}

QLabel#paramLabel {
    font-size: 9pt;
    color: #8c9cb6;
    padding-left: 2px;
    font-weight: 500;
}

/* ---- 操作按钮 ---- */
QPushButton#folder, QPushButton#importbtn, QPushButton#exporter {
    background-color: #132135;
    color: #e6eefb;
    border: 1px solid #243955;
    border-radius: 12px;
    padding: 10px 14px;
    font-size: 10pt;
    font-weight: 600;
    text-align: left;
}

QPushButton#folder:hover, QPushButton#importbtn:hover,
QPushButton#exporter:hover {
    background-color: #172840;
    border-color: #31517a;
}

QPushButton#playbtn {
    background-color: #2f7df6;
    color: #f9fbff;
    border: 1px solid #4a92ff;
    border-radius: 14px;
    padding: 12px 16px;
    font-size: 11pt;
    font-weight: 700;
    text-align: left;
}

QPushButton#playbtn:hover {
    background-color: #3d89ff;
}

QPushButton#playbtn:checked {
    background-color: #17624e;
    border-color: #2c8c71;
}

QPushButton#stopbtn {
    background-color: #161f2c;
    color: #d7e3f7;
    border: 1px solid #29394f;
    border-radius: 12px;
    padding: 10px 14px;
    font-size: 10pt;
    font-weight: 600;
    text-align: left;
}

QPushButton#stopbtn:hover {
    background-color: #1c2737;
    border-color: #3a4d67;
}

QPushButton:disabled {
    background-color: #111826;
    color: #5d6a7f;
    border-color: #1c2738;
}

/* ---- 下拉框 / 数值框 ---- */
QComboBox {
    background-color: #0e1827;
    color: #d9e6f7;
    border: 1px solid #243955;
    border-radius: 10px;
    padding: 7px 10px;
    font-size: 10pt;
}

QComboBox:hover {
    border-color: #3867a4;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #88a2c7;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #0f1827;
    color: #dce8f8;
    selection-background-color: #19304b;
    border: 1px solid #223652;
    outline: none;
}

QDoubleSpinBox {
    background-color: #0e1827;
    color: #d9e6f7;
    border: 1px solid #243955;
    border-radius: 10px;
    padding: 4px 8px;
    font-size: 10pt;
}

QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background: transparent;
    border: none;
    width: 14px;
}

/* ---- 滑块 ---- */
QSlider::groove:horizontal {
    height: 4px;
    background: #243349;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #5ea0ff;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
    border: 2px solid #dbe8ff;
}

QSlider::handle:horizontal:hover {
    background: #7ab0ff;
}

QSlider::sub-page:horizontal {
    background: #2f7df6;
    border-radius: 2px;
}

QSlider::add-page:horizontal {
    background: #243349;
    border-radius: 2px;
}

/* ---- 主视图 ---- */
QFrame#viewPanel {
    background-color: #09111d;
}

QFrame#viewCard {
    background-color: #0f1929;
    border: 1px solid #1d2d45;
    border-radius: 18px;
}

QLabel#viewIconBadge {
    background-color: #13263d;
    border: 1px solid #294563;
    border-radius: 10px;
}

QLabel#viewTitle {
    font-size: 11pt;
    font-weight: 700;
    color: #eef4ff;
}

QLabel#viewMeta {
    font-size: 8.8pt;
    color: #7f8ea8;
}

QLabel#input, QLabel#output {
    background-color: #0a1321;
    border: 1px solid #1b2b42;
    border-radius: 14px;
    color: #60728f;
    font-size: 11pt;
    font-weight: 500;
    padding: 20px;
}

QLabel#input:hover, QLabel#output:hover {
    border-color: #35577f;
    background-color: #0c1626;
}

/* ---- 进度卡片 ---- */
QFrame#progressFrame {
    background-color: #0f1929;
    border: 1px solid #1d2d45;
    border-radius: 16px;
}

QLabel#progressTitle {
    font-size: 9.5pt;
    font-weight: 600;
    color: #dce8f8;
}

QLabel#progressValue {
    font-size: 9pt;
    font-weight: 700;
    color: #8fb6ff;
}

QProgressBar {
    background-color: #172437;
    border: none;
    border-radius: 6px;
    color: transparent;
    min-height: 12px;
    max-height: 12px;
}

QProgressBar::chunk {
    background-color: #3384ff;
    border-radius: 6px;
}

/* ---- 结果统计 ---- */
QListWidget#resultlist {
    background-color: transparent;
    color: #dde7f7;
    border: none;
    font-size: 10.5pt;
    outline: none;
}

QListWidget::item {
    padding: 7px 10px;
    border-radius: 10px;
}

QListWidget::item:hover {
    background-color: #162437;
}

/* ---- 底部状态栏 ---- */
QFrame#statusBar {
    background-color: #0b1422;
    border-top: 1px solid #16253b;
}

QLabel#outputbox {
    color: #92a4c2;
    font-size: 9pt;
}

QLabel#footerRight {
    color: #54657e;
    font-size: 8pt;
    letter-spacing: 0.3px;
}
"""
