"""安全帽佩戴行为检测系统 —— 程序入口。"""
import sys
from PySide6.QtWidgets import QApplication
from detector import DetectorWindow
from lib import glo


def main():
    app = QApplication(sys.argv)
    glo._init()
    window = DetectorWindow()
    window.center()
    glo.set_value('yolo', window)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
