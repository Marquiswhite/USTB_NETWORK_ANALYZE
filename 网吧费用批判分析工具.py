import sys
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QFormLayout, QTextEdit,
    QComboBox, QGroupBox, QGridLayout, QTabWidget,
)


class CriticalAnalysisApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 输入组件
        self.x_input = QLineEdit("1000")
        self.y_input = QLineEdit("1")
        self.z_input = QLineEdit("5000")

        # 绘图参数控件
        self.var_selector = QComboBox()
        self.var_selector.addItems(["x (网吧单价)", "y (网速)", "z (数据量)"])
        self.range_start = QLineEdit("500")
        self.range_end = QLineEdit("2000")
        self.plot_btn = QPushButton("生成曲线")
        self.plot_btn.clicked.connect(self.update_plot)

        # Matplotlib 画布
        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvas(self.figure)

        # 创建选项卡容器
        self.tabs = QTabWidget()
        self.analysis_tab = QWidget()
        self.critique_tab = QWidget()
        self.tabs.addTab(self.analysis_tab, "费用分析")

        # 构建分析选项卡
        self.build_analysis_tab()

        # 主布局
        main_layout = QGridLayout()
        main_layout.addWidget(self.tabs, 0, 0, 1, 2)
        self.setLayout(main_layout)

        self.setWindowTitle("网络费用分析工具")
        self.setGeometry(300, 300, 1200, 800)
        self.show_initial_plot()

    def build_analysis_tab(self):
        """构建分析选项卡内容"""
        tab_layout = QGridLayout()

        # 输入面板
        input_group = QGroupBox("参数输入")
        form_layout = QFormLayout()
        form_layout.addRow("网吧单价 x（元/小时）:", self.x_input)
        form_layout.addRow("网速 y（G/秒）:", self.y_input)
        form_layout.addRow("下载量 z（GB）:", self.z_input)
        input_group.setLayout(form_layout)

        # 绘图控制
        plot_controls = QGridLayout()
        plot_controls.addWidget(QLabel("分析变量:"), 0, 0)
        plot_controls.addWidget(self.var_selector, 0, 1)
        plot_controls.addWidget(QLabel("变化范围:"), 1, 0)
        plot_controls.addWidget(self.range_start, 1, 1)
        plot_controls.addWidget(QLabel("到"), 1, 2)
        plot_controls.addWidget(self.range_end, 1, 3)
        plot_controls.addWidget(self.plot_btn, 2, 0, 1, 4)

        # 结果区域
        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)

        # 布局组合
        tab_layout.addWidget(input_group, 0, 0, 1, 2)
        tab_layout.addWidget(self.canvas, 1, 0, 2, 1)
        tab_layout.addLayout(plot_controls, 1, 1)
        tab_layout.addWidget(self.result_area, 2, 1)

        self.analysis_tab.setLayout(tab_layout)

    def validate_input(self, check_plot=False):
        try:
            # 基础验证
            x = float(self.x_input.text())
            y = float(self.y_input.text())
            z = float(self.z_input.text())
            start = float(self.range_start.text())
            end = float(self.range_end.text())

            if any(v <= 0 for v in [x, y, z, start, end]) or start >= end:
                raise ValueError
            return (x, y, z, start, end)
        except:
            self.result_area.setText("⚠️ 请输入有效的数值范围！")
            return None

    def school_cost(self, z):
        return 0.6 * z

    def bar_cost(self, x, y, z):
        t = z / (y * 3600)
        return x * math.ceil(t)

    def update_plot(self):
        inputs = self.validate_input()
        if not inputs:
            return

        x, y, z, start, end = inputs
        var_index = self.var_selector.currentIndex()

        # 生成数据
        var_labels = ["x (元/小时)", "y (G/秒)", "z (GB)"]
        values = np.linspace(start, end, 100)

        self.ax.clear()

        if var_index == 0:  # x变化
            school = [self.school_cost(z)] * len(values)
            bar = [self.bar_cost(v, y, z) for v in values]
            self.ax.plot(values, school, label="校园网", lw=2)
            self.ax.plot(values, bar, label="网吧", linestyle="--")
            self.ax.set_xlabel(var_labels[0])
        elif var_index == 1:  # y变化
            school = [self.school_cost(z)] * len(values)
            bar = [self.bar_cost(x, v, z) for v in values]
            self.ax.plot(values, school, label="校园网", lw=2)
            self.ax.plot(values, bar, label="网吧", linestyle="--")
            self.ax.set_xlabel(var_labels[1])
        else:  # z变化
            school = [self.school_cost(v) for v in values]
            bar = [self.bar_cost(x, y, v) for v in values]
            self.ax.plot(values, school, label="校园网", lw=2)
            self.ax.plot(values, bar, label="网吧", linestyle="--")
            self.ax.set_xlabel(var_labels[2])

        self.ax.set_ylabel("费用（元）")
        self.ax.legend()
        self.ax.grid(True)
        self.canvas.draw()

        # 显示当前参数计算结果
        self.show_current_result(x, y, z)

    def show_initial_plot(self):
        """初始化示例图"""
        x = np.linspace(500, 2000, 100)
        y_val = 1
        z_val = 5000
        school = [self.school_cost(z_val)] * len(x)
        bar = [self.bar_cost(v, y_val, z_val) for v in x]

        self.ax.plot(x, school, label="校园网", lw=2)
        self.ax.plot(x, bar, label="网吧", linestyle="--")
        self.ax.set_xlabel("x (元/小时)")
        self.ax.set_ylabel("费用（元）")
        self.ax.legend()
        self.ax.grid(True)
        self.canvas.draw()

    def show_current_result(self, x, y, z):
        """显示当前参数计算结果"""
        school = self.school_cost(z)
        bar = self.bar_cost(x, y, z)
        t = math.ceil(z / (y * 3600))

        result = [
            "当前参数计算结果：",
            f"校园网费用: {school:.2f} 元",
            f"网吧费用: {bar:.2f} 元 (需时 {t} 小时)",
            f"推荐选择：{'网吧' if bar < school else '校园网'}",
            f"节省金额：{abs(bar-school):.2f} 元"
        ]

        self.result_area.setText("\n".join(result))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CriticalAnalysisApp()
    ex.show()
    sys.exit(app.exec_())
