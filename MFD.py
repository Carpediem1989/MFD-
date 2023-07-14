import sys

import matplotlib.pyplot as plt
import numpy as np
from PyQt5 import QtPrintSupport
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter, QFont

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QPushButton,
    QGraphicsView, QGraphicsScene, QVBoxLayout, QHBoxLayout,
    QGroupBox, QGridLayout, QFileDialog, QWidget, QComboBox
)
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QGraphicsOpacityEffect



class ParabolicPlotter(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口标题和大小
        self.setWindowTitle("模场直径曲线")
        self.setGeometry(100, 100, 1000, 800)

        # 输入框
        self.N =41
        self.x_line_edits = []
        self.y_line_edits = []
        self.groups = []

        self.fiber_number_edits = QLineEdit()
        fiber_number_label = QLabel("光纤编号：", self)
        fiber_number_label.setFont(QFont("Arial", 12))

        hbox2 = QHBoxLayout()
        hbox2.addWidget(fiber_number_label)
        hbox2.addWidget(self.fiber_number_edits)
        #self.fiber_number_edits.setFixedSize(500, 30)

        self.name_edits = QLineEdit()
        name_label = QLabel("姓名       ：", self)
        name_label.setFont(QFont("Arial", 12))
        hbox4 = QHBoxLayout()
        hbox4.addWidget(name_label)
        hbox4.addWidget(self.name_edits)

        self.student_id_edits = QLineEdit()
        student_id_label = QLabel("学号       ：", self)
        student_id_label.setFont(QFont("Arial", 12))

        hbox5 = QHBoxLayout()
        hbox5.addWidget(student_id_label)
        hbox5.addWidget(self.student_id_edits)

        self.exp_date_edits = QLineEdit()
        exp_date_label = QLabel("实验日期：", self)
        exp_date_label.setFont(QFont("Arial", 12))
        hbox6 = QHBoxLayout()
        hbox6.addWidget(exp_date_label)
        hbox6.addWidget(self.exp_date_edits)



        layout = QGridLayout()
        row, col = 0, 0

        for i in range(self.N):
            hbox3 = QHBoxLayout()
            label1 = QLabel("角度（deg）")
            label2 = QLabel("功率（dBm）")
            hbox3.addWidget(label1)
            hbox3.addWidget(label2)
            if row == 0 or row == 16 or row == 32:
                layout.addLayout(hbox3, row, col)
            x_line_edit = QLineEdit(str(i - (self.N // 2)))
            y_line_edit = QLineEdit()

            group_box = QGroupBox()
            group_layout = QVBoxLayout()

            hbox = QHBoxLayout()
            hbox.addWidget(x_line_edit)
            hbox.addWidget(y_line_edit)
            group_layout.addLayout(hbox)
            group_box.setLayout(group_layout)

            self.groups.append(group_box)
            self.x_line_edits.append(x_line_edit)
            self.y_line_edits.append(y_line_edit)

            layout.addWidget(self.groups[i], row + 1, col)

            row += 1
            if row == 15:
                col += 1
                row = 0

        input_widget = QWidget()
        input_widget.setObjectName("InputWidget")
        input_widget.setLayout(layout)
        input_widget.setFixedSize(700, 800)

        # 输出窗口
        self.scene = QGraphicsScene(self)
        self.scene.setBackgroundBrush(Qt.white)
        self.graphics_view = QGraphicsView(self.scene, self)
        self.graphics_view.setRenderHint(QPainter.Antialiasing)
        self.graphics_view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        font = QFont()
        font.setPointSize(20)  # 设置字体大小
        font.setBold(True)  # 设置加粗
        text_item = self.scene.addText("建议在1920×1080分辨率下运行，请将所有输入栏填满后绘图。")
        text_item.setFont(font)  # 设置字体
        text_item.setPos(10, 10)  # 设置文本的位置

        # 按钮
        self.plot_button = QPushButton("绘制图像", self)
        self.plot_button.setFixedSize(250, 50)
        self.plot_button.setFont(QFont("Arial", 16))
        self.pdf_button = QPushButton("生成 PDF", self)
        self.pdf_button.setFixedSize(250, 50)
        self.pdf_button.setFont(QFont("Arial", 16))
        self.clear_button = QPushButton("清空", self)
        self.clear_button.setFixedSize(250, 50)
        self.clear_button.setFont(QFont("Arial", 16))
        self.save_button = QPushButton("保存图像", self)
        self.save_button.setFixedSize(250, 50)
        self.save_button.setFont(QFont("Arial", 16))

        self.plot_button.clicked.connect(self.on_plot_clicked)
        self.pdf_button.clicked.connect(self.on_pdf_clicked)
        self.clear_button.clicked.connect(self.on_clear_clicked)
        self.save_button.clicked.connect(self.on_save_clicked)

        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.addWidget(self.plot_button)
        button_layout.addWidget(self.pdf_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.save_button)

        # 添加切换按钮
        self.wl_label = QLabel("波长(\u03BCm)", self)
        self.wl_label.setFont(QFont("Arial", 12))
        self.wl_combo_box = QComboBox(self)#设置大小
        #self.wl_combo_box.setFixedSize(500, 30)
        self.wl_combo_box.addItem("1.31", 1.31)
        self.wl_combo_box.addItem("1.55", 1.55)
        self.wl_combo_box.currentIndexChanged.connect(self.on_wl_changed)
        self.wl_combo_box.setCurrentIndex(1)  # 默认选中1.55

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.wl_label)
        hbox1.addWidget(self.wl_combo_box)

        self.picture = QLabel(self)
        pixmap = QPixmap("C:\\Users\\ASUS\\Desktop\\recent\\material\\BJUTlogo2.png")
        self.picture.setPixmap(pixmap)  # 将 pixmap 设置为 self.picture 的图像
        self.picture.setScaledContents(True)  # 设置内容按比例缩放
        self.picture.setMaximumSize(419, 130)
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(1)
        self.picture.setGraphicsEffect(opacity_effect)

        hbox_sign = QHBoxLayout()
        self.sign = QLabel("作者：22级硕士研究生吴凡", self)
        self.sign.setFont(QFont("Arial", 12))
        hbox_sign.addWidget(self.sign)

        hbox_all = QVBoxLayout()
        hbox_all.addLayout(hbox1)
        hbox_all.addLayout(hbox2)
        hbox_all.addLayout(hbox4)
        hbox_all.addLayout(hbox5)
        hbox_all.addLayout(hbox6)

        hbox_pic_and_all = QHBoxLayout()
        hbox_pic_and_all.addWidget(self.picture)
        hbox_pic_and_all.addLayout(hbox_all)

        main_layout = QGridLayout()
        main_layout.addLayout(hbox_pic_and_all, 0, 0, 6, 2)
        main_layout.addWidget(input_widget, 6, 0, 6, 5)  # 设置 input_widget 占据 6 行 4 列
        main_layout.addWidget(self.graphics_view, 0, 2, 11, 3)
        main_layout.addWidget(button_widget, 11, 2, 14, 3)
        main_layout.addLayout(hbox_sign, 15, 2, 10, 3)#将main_layout.addLayout(hbox_sign, 11, 2, 10, 3)右对齐
        main_layout.setAlignment(hbox_sign, Qt.AlignRight)  # 将 hbox_sign 右对齐



        main_widget = QWidget()
        main_widget.setObjectName("MainWidget")
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # 设置 QMainWindow 的标题和大小
        self.setWindowTitle("光纤模场直径测量")
        self.showMaximized()

    def on_wl_changed(self, index):
        wl = self.wl_combo_box.itemData(index)
        print("wl =", wl)
        # 在这里可以进行后续操作，使用新的波长值 wl
        # 比如更新图表、计算模场直径等
        return wl

    @staticmethod
    def static(x_values, y_values, wl):
        # 将角度转化为弧度
        x_values = np.deg2rad(x_values)

        s3 = 0
        s1 = 0
        for m in range(2, len(x_values)):
            b = (y_values[m] + y_values[m - 1]) / 2  # 强度取1/2
            c = np.abs((x_values[m] + x_values[m - 1])) / 2  # 角度取1/2
            s3 += np.sin(c) ** 3 * b * (x_values[m] - x_values[m - 1])
            s1 += np.sin(c) * b * (x_values[m] - x_values[m - 1])

        mfd = wl / np.pi * np.sqrt(2 * s1 / s3)
        return mfd

    def on_plot_clicked(self):
        try:
            x_values = [float(line_edit.text()) for line_edit in self.x_line_edits]
            Y_values = [float(line_edit.text()) for line_edit in self.y_line_edits]#dbm

            y_values = np.power(10, np.array(Y_values) / 10)  #线性
            print("x_values =", x_values, "deg")
            print("y_values =", Y_values, "dBm")
            wl = self.on_wl_changed(self.wl_combo_box.currentIndex())  # 获取波长
            mfd = self.static(x_values, y_values, wl)
            print("模场直径为 =", mfd, "μm")

            fig = plt.figure(dpi=300)
            canvas = FigureCanvas(fig)
            fig.set_size_inches(8, 6)
            ax = fig.add_subplot(111)

            plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文标签
            plt.rcParams['axes.unicode_minus'] = False  # 这两行需要手动设置

            ax.plot(x_values, Y_values, color='red', linestyle='-', linewidth=3, label='曲线1')
            #轴标签
            ax.set_xlabel("角度(deg)", fontsize=20)
            ax.set_ylabel("功率(dBm)", fontsize=20)

            #刻度范围
            ax.set_xlim(-20, 20)
            max_value = max(Y_values)+5
            min_value = min(Y_values)-5
            ax.set_ylim(min_value, max_value)

            #轴格式
            ax.xaxis.set_major_locator(plt.MultipleLocator(5))
            ax.xaxis.set_minor_locator(plt.MultipleLocator(1))
            ax.yaxis.set_major_locator(plt.MultipleLocator(10))
            ax.yaxis.set_minor_locator(plt.MultipleLocator(2))
            ax.tick_params(axis='x', direction='in',length=6,width=2.5, color='black',labelcolor='black', labelsize=16,pad=8)  # 刻度线与标签之间的距离
            ax.tick_params(axis='x',which='minor', direction='in', length=3, width=2.5, color='black', labelcolor='black', labelsize=16,pad=8)  # 刻度线与标签之间的距离
            ax.tick_params(axis='y', direction='in', length=6, width=2.5, color='black', labelcolor='black', labelsize=16,pad=8)  # 刻度线与标签之间的距离
            ax.tick_params(axis='y', which='minor', direction='in', length=3, width=2.5, color='black',labelcolor='black', labelsize=16,pad=8)  # 刻度线与标签之间的距离
            # 设置边框线的样式和属性
            ax.spines['top'].set_visible(True)  # 显示顶部边框线
            ax.spines['right'].set_visible(True)  # 显示右侧边框线
            ax.spines['bottom'].set_visible(True)  # 显示底部边框线
            ax.spines['left'].set_visible(True)  # 显示左侧边框线

            # 设置边框线的颜色
            ax.spines['top'].set_color('black')
            ax.spines['right'].set_color('black')
            ax.spines['bottom'].set_color('black')
            ax.spines['left'].set_color('black')

            # 设置边框线的粗细
            ax.spines['top'].set_linewidth(2.5)
            ax.spines['right'].set_linewidth(2.5)
            ax.spines['bottom'].set_linewidth(2.5)
            ax.spines['left'].set_linewidth(2.5)


            # 调整文本位置
            xlim = ax.set_xlim()
            ylim = ax.set_ylim()

            # 计算文本的坐标
            text_x = (xlim[0] + xlim[1]) / 2  # 在 x 轴中心位置
            text_y = ylim[1] + 0.05 * (ylim[1] - ylim[0])  # 在 y 轴上方位置

            # 设置文本相对位置并添加到轴对象中
            text = ax.text(text_x+0, text_y+3.5, "模场直径曲线", fontsize=20, fontweight='bold', color='blue',
                           horizontalalignment='center', transform=ax.transData)

            text2 = self.fiber_number_edits.text()
            ax.text(text_x+0, text_y+0.5, "光纤编号："+ text2, fontsize=12, fontweight='bold', color='blue',
                    horizontalalignment='center')

            mfd_str = "{:.3f}".format(mfd)
            ax.text(text_x+0, text_y-2.5, "波长\u03BB = " + str(wl) + "(\u03BCm)" + "   MFD = " + mfd_str + "(\u03BCm)", fontsize=12, fontweight='bold', color='blue',
                    horizontalalignment='center')

            text3 = self.name_edits.text()
            ax.text(text_x+13, text_y+3.5, "姓名：" + text3, fontsize=12, fontweight='bold', color='blue',)
            text4 = self.student_id_edits.text()
            ax.text(text_x+13, text_y+0.5, "学号：" + text4, fontsize=12, fontweight='bold', color='blue', )
            text5 = self.exp_date_edits.text()
            ax.text(text_x+13, text_y-2.5, "实验日期：" + text5, fontsize=12, fontweight='bold', color='blue', )


            fig.canvas.draw()
            #plt.show()
            width, height = fig.canvas.get_width_height()
            buf = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
            buf = buf.reshape((height, width, 3))

            image = QImage(buf.data, width, height, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            #plt.show()
            self.scene.clear()  # 清空场景中的所有内容
            self.scene.addPixmap(pixmap)  # 将图像添加到场景中
            self.graphics_view.setSceneRect(1, 2, width, height)  # 设置场景大小
            self.graphics_view.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)  # 调整图形视图的大小

        except ValueError:
            print("输入错误")

    def on_pdf_clicked(self):
        # 生成 PDF
        pixmap = self.graphics_view.grab()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "保存 PDF 文件", "", "PDF Files (*.pdf);;All Files (*)"
        )
        if file_name:
            printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
            printer.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)
            printer.setOutputFileName(file_name)
            painter = QPainter(printer)
            rect = painter.viewport()
            size = pixmap.size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(pixmap.rect())
            painter.drawPixmap(0, 0, pixmap)
            painter.end()

    def on_clear_clicked(self):
        for line_edit in self.y_line_edits:
            line_edit.setText("")

        self.scene.clear()

    def on_save_clicked(self):
        # 保存图像
        file_name, _ = QFileDialog.getSaveFileName(self, '选择图像保存路径', '', '*.png')
        if file_name:
            pixmap = self.graphics_view.grab()
            pixmap.save(file_name, "PNG", quality=100)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    plotter = ParabolicPlotter()
    plotter.show()
    sys.exit(app.exec_())
