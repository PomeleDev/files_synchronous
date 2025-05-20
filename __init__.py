import sys
import os
import traceback
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog,
    QLabel, QMenu, QAction, QMessageBox, QLineEdit, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QFont, QIcon


# Windows 任务栏图标支持防止多次点击关闭
if os.name == 'nt':
    import ctypes
    app_id = u"Pomelo.SyncTool.1.0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)


class CustomListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditTriggers(QListWidget.DoubleClicked)
        self.placeholder_text = "双击这里快速输入分目录路径"

    def mouseDoubleClickEvent(self, event):
        if self.count() >= 10:
            QMessageBox.warning(None, "提示", "单次最多只能添加10个分路径。")
            return

        index = self.indexAt(event.pos())
        if not index.isValid():
            item = QListWidgetItem("")
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.addItem(item)
            self.editItem(item)
        else:
            super().mouseDoubleClickEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        all_empty = all(self.item(i).text().strip() == "" for i in range(self.count()))

        if all_empty:
            painter = QPainter(self.viewport())
            painter.setPen(QColor(128, 128, 128))
            font = QFont()
            font.setItalic(True)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignCenter, self.placeholder_text)


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = '文件同步工具 v0.1'
        self.main_folder = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, 400, 500)
        self.setFixedSize(400, 500)

        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.label = QLabel("请选择主目录和分目录，然后进行同步。", self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        btn_select_main = QPushButton('选择主目录')
        btn_select_main.setFixedHeight(32)
        layout.addWidget(btn_select_main)

        self.main_folder_line_edit = QLineEdit(self)
        self.main_folder_line_edit.setReadOnly(True)
        self.main_folder_line_edit.setPlaceholderText("未选择主目录")
        self.main_folder_line_edit.setFixedHeight(30)
        layout.addWidget(self.main_folder_line_edit)

        self.subdirectory_list = CustomListWidget(self)
        self.subdirectory_list.setFixedHeight(230)
        self.subdirectory_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.subdirectory_list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.subdirectory_list)

        btn_add_sub = QPushButton('添加分目录')
        btn_add_sub.setFixedHeight(32)
        layout.addWidget(btn_add_sub)

        btn_sync = QPushButton('同步文件夹')
        btn_sync.setFixedHeight(36)
        layout.addWidget(btn_sync)

        self.setLayout(layout)

        # 绑定事件
        btn_select_main.clicked.connect(self.select_main_folder)
        btn_add_sub.clicked.connect(self.add_subdirectory)
        btn_sync.clicked.connect(self.sync_folders)

        # 样式
        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9fa;
                font-family: "Microsoft YaHei", sans-serif;
                font-size: 14px;
            }
            QLabel {
                color: #333;
                font-size: 14px;
            }
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #ccc;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #dcdcdc;
            }
            QPushButton:pressed {
                background-color: #cfcfcf;
            }
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
                background-color: #fff;
            }
            QLineEdit {
                font-size: 14px;
                border: 1px solid #ccc;
            }
            QListWidget::item:selected {
                background-color: #e0e0ff;
                color: #000;
            }
            QMenu {
                background-color: #fff;
                border: 1px solid #ccc;
                padding: 4px 0px;
            }
            QMenu::item:selected {
                background-color: #000;
                color: #fff;
            }
        """)

    def select_main_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择主目录")
        if folder:
            self.main_folder = folder
            self.main_folder_line_edit.setText(folder)
            self.main_folder_line_edit.setToolTip(folder)

    def add_subdirectory(self):
        if self.subdirectory_list.count() >= 10:
            QMessageBox.warning(self, "提示", "最多只能添加 10 个分目录路径。")
            return

        sub_folder = QFileDialog.getExistingDirectory(self, "选择分目录")
        if sub_folder:
            if os.path.abspath(sub_folder) == os.path.abspath(self.main_folder):
                QMessageBox.warning(self, "警告", "分目录不能是主目录本身！")
                return

            item = QListWidgetItem(sub_folder)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.subdirectory_list.addItem(item)

    def show_context_menu(self, pos):
        context_menu = QMenu(self)
        delete_action = QAction('删除', self)
        delete_action.triggered.connect(self.delete_subdirectory)
        context_menu.addAction(delete_action)
        context_menu.exec_(self.subdirectory_list.mapToGlobal(pos))

    def delete_subdirectory(self):
        list_items = self.subdirectory_list.selectedItems()
        if not list_items:
            return
        for item in list_items:
            self.subdirectory_list.takeItem(self.subdirectory_list.row(item))

    def sync_folders(self):
        if not self.main_folder:
            QMessageBox.warning(self, '警告', '请先选择主目录。')
            return

        if self.subdirectory_list.count() == 0:
            QMessageBox.warning(self, '警告', '请至少添加一个分目录。')
            return

        self.label.setText("正在同步...")

        try:
            for i in range(self.subdirectory_list.count()):
                full_path = self.subdirectory_list.item(i).text().strip()
                full_path = os.path.normpath(full_path)

                if not full_path or not os.path.basename(full_path):
                    continue

                # 防止同步自身
                if os.path.abspath(full_path) == os.path.abspath(self.main_folder):
                    QMessageBox.warning(self, "跳过", f"已跳过与主目录相同的路径：\n{full_path}")
                    continue

                if os.path.exists(full_path):
                    if os.path.islink(full_path):
                        os.unlink(full_path)
                    else:
                        import shutil
                        shutil.rmtree(full_path)

                parent_dir = os.path.dirname(full_path)
                link_name = os.path.basename(full_path)
                link_path = os.path.join(parent_dir, link_name)

                os.symlink(self.main_folder, link_path)

            QMessageBox.information(self, '成功', '同步完成！')
            self.label.setText("同步完成。")

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, '错误', f'同步失败:\n{e}')
            self.label.setText("同步失败。")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()

    # 设置图标（容错处理）
    if os.path.exists("favicon.ico"):
        ex.setWindowIcon(QIcon("favicon.ico"))

    # 窗口居中
    screen_rect = app.desktop().screenGeometry()
    window_rect = ex.frameGeometry()
    center_point = screen_rect.center()
    window_rect.moveCenter(center_point)
    ex.move(window_rect.topLeft())

    # 欢迎提示
    QMessageBox.information(ex, "使用说明", """\
欢迎使用 文件同步工具 v0.1

本工具已开源在 Github，完全免费。
请勿上当受骗购买“高级版”或“授权”。

【功能简介】：
- 支持主目录与多个分目录之间的同步；
- 通过创建符号链接实现映射；
- 路径可编辑、双击新增、右键删除；
- 最多添加 10 个分目录；
- 需要管理员权限运行。

【使用方法】：
1. 点击“选择主目录”选择源目录；
2. 添加或输入分目录；
3. 点击“同步文件夹”即可开始。
""")

    ex.show()
    sys.exit(app.exec_())
