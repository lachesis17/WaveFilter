# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'wavefilter.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFormLayout, QGroupBox, QHBoxLayout, QHeaderView,
    QLabel, QMainWindow, QMenu, QMenuBar,
    QPushButton, QScrollArea, QSizePolicy, QSpinBox,
    QSplitter, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget)

from pyqtgraph import PlotWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1400, 975)
        MainWindow.setMinimumSize(QSize(900, 600))
        self.actionLine_Colors = QAction(MainWindow)
        self.actionLine_Colors.setObjectName(u"actionLine_Colors")
        icon = QIcon()
        icon.addFile(u"ui/colors.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionLine_Colors.setIcon(icon)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_main = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_main.setObjectName(u"horizontalLayout_main")
        self.main_splitter = QSplitter(self.centralwidget)
        self.main_splitter.setObjectName(u"main_splitter")
        self.main_splitter.setOrientation(Qt.Horizontal)
        self.main_splitter.setHandleWidth(10)
        self.main_splitter.setChildrenCollapsible(True)
        self.plot_splitter = QSplitter(self.main_splitter)
        self.plot_splitter.setObjectName(u"plot_splitter")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plot_splitter.sizePolicy().hasHeightForWidth())
        self.plot_splitter.setSizePolicy(sizePolicy)
        self.plot_splitter.setOrientation(Qt.Vertical)
        self.plot_splitter.setHandleWidth(10)
        self.plot_splitter.setChildrenCollapsible(True)
        self.fft_plot = PlotWidget(self.plot_splitter)
        self.fft_plot.setObjectName(u"fft_plot")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(2)
        sizePolicy1.setHeightForWidth(self.fft_plot.sizePolicy().hasHeightForWidth())
        self.fft_plot.setSizePolicy(sizePolicy1)
        self.fft_plot.setMinimumSize(QSize(400, 180))
        self.plot_splitter.addWidget(self.fft_plot)
        self.signal_plot = PlotWidget(self.plot_splitter)
        self.signal_plot.setObjectName(u"signal_plot")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(3)
        sizePolicy2.setHeightForWidth(self.signal_plot.sizePolicy().hasHeightForWidth())
        self.signal_plot.setSizePolicy(sizePolicy2)
        self.signal_plot.setMinimumSize(QSize(400, 260))
        self.plot_splitter.addWidget(self.signal_plot)
        self.main_splitter.addWidget(self.plot_splitter)
        self.control_scroll = QScrollArea(self.main_splitter)
        self.control_scroll.setObjectName(u"control_scroll")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(1)
        sizePolicy3.setHeightForWidth(self.control_scroll.sizePolicy().hasHeightForWidth())
        self.control_scroll.setSizePolicy(sizePolicy3)
        self.control_scroll.setMinimumSize(QSize(360, 0))
        self.control_scroll.setMaximumSize(QSize(16777215, 16777215))
        self.control_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.control_scroll.setWidgetResizable(True)
        self.scroll_contents = QWidget()
        self.scroll_contents.setObjectName(u"scroll_contents")
        self.scroll_contents.setGeometry(QRect(0, 0, 395, 933))
        self.verticalLayout_panel = QVBoxLayout(self.scroll_contents)
        self.verticalLayout_panel.setObjectName(u"verticalLayout_panel")
        self.file_group = QGroupBox(self.scroll_contents)
        self.file_group.setObjectName(u"file_group")
        self.verticalLayout_file = QVBoxLayout(self.file_group)
        self.verticalLayout_file.setObjectName(u"verticalLayout_file")
        self.horizontalLayout_file_buttons = QHBoxLayout()
        self.horizontalLayout_file_buttons.setObjectName(u"horizontalLayout_file_buttons")
        self.open_button = QPushButton(self.file_group)
        self.open_button.setObjectName(u"open_button")

        self.horizontalLayout_file_buttons.addWidget(self.open_button)

        self.generate_button = QPushButton(self.file_group)
        self.generate_button.setObjectName(u"generate_button")

        self.horizontalLayout_file_buttons.addWidget(self.generate_button)


        self.verticalLayout_file.addLayout(self.horizontalLayout_file_buttons)

        self.file_label = QLabel(self.file_group)
        self.file_label.setObjectName(u"file_label")
        self.file_label.setWordWrap(True)

        self.verticalLayout_file.addWidget(self.file_label)

        self.horizontalLayout_playback = QHBoxLayout()
        self.horizontalLayout_playback.setObjectName(u"horizontalLayout_playback")
        self.play_button = QPushButton(self.file_group)
        self.play_button.setObjectName(u"play_button")
        self.play_button.setEnabled(False)

        self.horizontalLayout_playback.addWidget(self.play_button)

        self.stop_button = QPushButton(self.file_group)
        self.stop_button.setObjectName(u"stop_button")
        self.stop_button.setEnabled(False)

        self.horizontalLayout_playback.addWidget(self.stop_button)


        self.verticalLayout_file.addLayout(self.horizontalLayout_playback)


        self.verticalLayout_panel.addWidget(self.file_group)

        self.fft_group = QGroupBox(self.scroll_contents)
        self.fft_group.setObjectName(u"fft_group")
        self.verticalLayout_fft = QVBoxLayout(self.fft_group)
        self.verticalLayout_fft.setSpacing(4)
        self.verticalLayout_fft.setObjectName(u"verticalLayout_fft")
        self.horizontalLayout_fft_checks = QHBoxLayout()
        self.horizontalLayout_fft_checks.setObjectName(u"horizontalLayout_fft_checks")
        self.normalize_check = QCheckBox(self.fft_group)
        self.normalize_check.setObjectName(u"normalize_check")
        self.normalize_check.setChecked(True)

        self.horizontalLayout_fft_checks.addWidget(self.normalize_check)

        self.window_check_fft = QCheckBox(self.fft_group)
        self.window_check_fft.setObjectName(u"window_check_fft")

        self.horizontalLayout_fft_checks.addWidget(self.window_check_fft)


        self.verticalLayout_fft.addLayout(self.horizontalLayout_fft_checks)

        self.formLayout_fft_mode = QFormLayout()
        self.formLayout_fft_mode.setObjectName(u"formLayout_fft_mode")
        self.label_fft_mode = QLabel(self.fft_group)
        self.label_fft_mode.setObjectName(u"label_fft_mode")

        self.formLayout_fft_mode.setWidget(0, QFormLayout.LabelRole, self.label_fft_mode)

        self.fft_mode_combo = QComboBox(self.fft_group)
        self.fft_mode_combo.addItem("")
        self.fft_mode_combo.addItem("")
        self.fft_mode_combo.addItem("")
        self.fft_mode_combo.addItem("")
        self.fft_mode_combo.addItem("")
        self.fft_mode_combo.addItem("")
        self.fft_mode_combo.addItem("")
        self.fft_mode_combo.addItem("")
        self.fft_mode_combo.addItem("")
        self.fft_mode_combo.addItem("")
        self.fft_mode_combo.setObjectName(u"fft_mode_combo")

        self.formLayout_fft_mode.setWidget(0, QFormLayout.FieldRole, self.fft_mode_combo)


        self.verticalLayout_fft.addLayout(self.formLayout_fft_mode)

        self.label_freq_thresh = QLabel(self.fft_group)
        self.label_freq_thresh.setObjectName(u"label_freq_thresh")
        self.label_freq_thresh.setAlignment(Qt.AlignHCenter)

        self.verticalLayout_fft.addWidget(self.label_freq_thresh)

        self.formLayout_fft_thresh = QFormLayout()
        self.formLayout_fft_thresh.setObjectName(u"formLayout_fft_thresh")
        self.label_low_freq = QLabel(self.fft_group)
        self.label_low_freq.setObjectName(u"label_low_freq")

        self.formLayout_fft_thresh.setWidget(0, QFormLayout.LabelRole, self.label_low_freq)

        self.low_peak_freq_spin = QDoubleSpinBox(self.fft_group)
        self.low_peak_freq_spin.setObjectName(u"low_peak_freq_spin")
        self.low_peak_freq_spin.setMinimum(0.000000000000000)
        self.low_peak_freq_spin.setMaximum(999999.000000000000000)
        self.low_peak_freq_spin.setSingleStep(10.000000000000000)
        self.low_peak_freq_spin.setValue(300.000000000000000)

        self.formLayout_fft_thresh.setWidget(0, QFormLayout.FieldRole, self.low_peak_freq_spin)

        self.label_high_freq = QLabel(self.fft_group)
        self.label_high_freq.setObjectName(u"label_high_freq")

        self.formLayout_fft_thresh.setWidget(1, QFormLayout.LabelRole, self.label_high_freq)

        self.high_peak_freq_spin = QDoubleSpinBox(self.fft_group)
        self.high_peak_freq_spin.setObjectName(u"high_peak_freq_spin")
        self.high_peak_freq_spin.setMinimum(0.000000000000000)
        self.high_peak_freq_spin.setMaximum(999999.000000000000000)
        self.high_peak_freq_spin.setSingleStep(10.000000000000000)
        self.high_peak_freq_spin.setValue(310.000000000000000)

        self.formLayout_fft_thresh.setWidget(1, QFormLayout.FieldRole, self.high_peak_freq_spin)

        self.label_min_amp = QLabel(self.fft_group)
        self.label_min_amp.setObjectName(u"label_min_amp")

        self.formLayout_fft_thresh.setWidget(2, QFormLayout.LabelRole, self.label_min_amp)

        self.min_peak_amp_spin = QDoubleSpinBox(self.fft_group)
        self.min_peak_amp_spin.setObjectName(u"min_peak_amp_spin")
        self.min_peak_amp_spin.setDecimals(2)
        self.min_peak_amp_spin.setMinimum(0.000000000000000)
        self.min_peak_amp_spin.setMaximum(1.000000000000000)
        self.min_peak_amp_spin.setSingleStep(0.010000000000000)
        self.min_peak_amp_spin.setValue(0.150000000000000)

        self.formLayout_fft_thresh.setWidget(2, QFormLayout.FieldRole, self.min_peak_amp_spin)


        self.verticalLayout_fft.addLayout(self.formLayout_fft_thresh)

        self.horizontalLayout_kalman = QHBoxLayout()
        self.horizontalLayout_kalman.setObjectName(u"horizontalLayout_kalman")
        self.kalman_check = QCheckBox(self.fft_group)
        self.kalman_check.setObjectName(u"kalman_check")

        self.horizontalLayout_kalman.addWidget(self.kalman_check)

        self.label_kalman_noise = QLabel(self.fft_group)
        self.label_kalman_noise.setObjectName(u"label_kalman_noise")

        self.horizontalLayout_kalman.addWidget(self.label_kalman_noise)

        self.kalman_noise_spin = QDoubleSpinBox(self.fft_group)
        self.kalman_noise_spin.setObjectName(u"kalman_noise_spin")
        self.kalman_noise_spin.setDecimals(2)
        self.kalman_noise_spin.setMinimum(0.100000000000000)
        self.kalman_noise_spin.setMaximum(10.000000000000000)
        self.kalman_noise_spin.setSingleStep(0.100000000000000)
        self.kalman_noise_spin.setValue(0.500000000000000)

        self.horizontalLayout_kalman.addWidget(self.kalman_noise_spin)


        self.verticalLayout_fft.addLayout(self.horizontalLayout_kalman)

        self.apply_fft_button = QPushButton(self.fft_group)
        self.apply_fft_button.setObjectName(u"apply_fft_button")

        self.verticalLayout_fft.addWidget(self.apply_fft_button)


        self.verticalLayout_panel.addWidget(self.fft_group)

        self.plotting_group = QGroupBox(self.scroll_contents)
        self.plotting_group.setObjectName(u"plotting_group")
        self.horizontalLayout_plotting = QHBoxLayout(self.plotting_group)
        self.horizontalLayout_plotting.setObjectName(u"horizontalLayout_plotting")
        self.raw_visible_check = QCheckBox(self.plotting_group)
        self.raw_visible_check.setObjectName(u"raw_visible_check")
        self.raw_visible_check.setChecked(True)

        self.horizontalLayout_plotting.addWidget(self.raw_visible_check)

        self.filtered_visible_check = QCheckBox(self.plotting_group)
        self.filtered_visible_check.setObjectName(u"filtered_visible_check")
        self.filtered_visible_check.setChecked(True)

        self.horizontalLayout_plotting.addWidget(self.filtered_visible_check)


        self.verticalLayout_panel.addWidget(self.plotting_group)

        self.filters_group = QGroupBox(self.scroll_contents)
        self.filters_group.setObjectName(u"filters_group")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.filters_group.sizePolicy().hasHeightForWidth())
        self.filters_group.setSizePolicy(sizePolicy4)
        self.verticalLayout_filters = QVBoxLayout(self.filters_group)
        self.verticalLayout_filters.setSpacing(4)
        self.verticalLayout_filters.setObjectName(u"verticalLayout_filters")
        self.horizontalLayout_filter_top = QHBoxLayout()
        self.horizontalLayout_filter_top.setObjectName(u"horizontalLayout_filter_top")
        self.window_check_filter = QCheckBox(self.filters_group)
        self.window_check_filter.setObjectName(u"window_check_filter")

        self.horizontalLayout_filter_top.addWidget(self.window_check_filter)

        self.filter_combo = QComboBox(self.filters_group)
        self.filter_combo.addItem("")
        self.filter_combo.addItem("")
        self.filter_combo.addItem("")
        self.filter_combo.addItem("")
        self.filter_combo.addItem("")
        self.filter_combo.addItem("")
        self.filter_combo.addItem("")
        self.filter_combo.setObjectName(u"filter_combo")

        self.horizontalLayout_filter_top.addWidget(self.filter_combo)


        self.verticalLayout_filters.addLayout(self.horizontalLayout_filter_top)

        self.formLayout_filter_params = QFormLayout()
        self.formLayout_filter_params.setObjectName(u"formLayout_filter_params")
        self.label_filter_low = QLabel(self.filters_group)
        self.label_filter_low.setObjectName(u"label_filter_low")

        self.formLayout_filter_params.setWidget(0, QFormLayout.LabelRole, self.label_filter_low)

        self.filter_low_spin = QDoubleSpinBox(self.filters_group)
        self.filter_low_spin.setObjectName(u"filter_low_spin")
        self.filter_low_spin.setMinimum(10.000000000000000)
        self.filter_low_spin.setMaximum(10000.000000000000000)
        self.filter_low_spin.setSingleStep(10.000000000000000)
        self.filter_low_spin.setValue(150.000000000000000)

        self.formLayout_filter_params.setWidget(0, QFormLayout.FieldRole, self.filter_low_spin)

        self.label_filter_high = QLabel(self.filters_group)
        self.label_filter_high.setObjectName(u"label_filter_high")

        self.formLayout_filter_params.setWidget(1, QFormLayout.LabelRole, self.label_filter_high)

        self.filter_high_spin = QDoubleSpinBox(self.filters_group)
        self.filter_high_spin.setObjectName(u"filter_high_spin")
        self.filter_high_spin.setMinimum(11.000000000000000)
        self.filter_high_spin.setMaximum(10000.000000000000000)
        self.filter_high_spin.setSingleStep(10.000000000000000)
        self.filter_high_spin.setValue(250.000000000000000)

        self.formLayout_filter_params.setWidget(1, QFormLayout.FieldRole, self.filter_high_spin)

        self.label_filter_order = QLabel(self.filters_group)
        self.label_filter_order.setObjectName(u"label_filter_order")

        self.formLayout_filter_params.setWidget(2, QFormLayout.LabelRole, self.label_filter_order)

        self.filter_order_spin = QSpinBox(self.filters_group)
        self.filter_order_spin.setObjectName(u"filter_order_spin")
        self.filter_order_spin.setMinimum(1)
        self.filter_order_spin.setMaximum(20)
        self.filter_order_spin.setValue(1)

        self.formLayout_filter_params.setWidget(2, QFormLayout.FieldRole, self.filter_order_spin)

        self.label_filter_design = QLabel(self.filters_group)
        self.label_filter_design.setObjectName(u"label_filter_design")

        self.formLayout_filter_params.setWidget(3, QFormLayout.LabelRole, self.label_filter_design)

        self.filter_design_combo = QComboBox(self.filters_group)
        self.filter_design_combo.addItem("")
        self.filter_design_combo.addItem("")
        self.filter_design_combo.addItem("")
        self.filter_design_combo.addItem("")
        self.filter_design_combo.addItem("")
        self.filter_design_combo.setObjectName(u"filter_design_combo")

        self.formLayout_filter_params.setWidget(3, QFormLayout.FieldRole, self.filter_design_combo)

        self.label_ripple = QLabel(self.filters_group)
        self.label_ripple.setObjectName(u"label_ripple")

        self.formLayout_filter_params.setWidget(4, QFormLayout.LabelRole, self.label_ripple)

        self.ripple_spin = QDoubleSpinBox(self.filters_group)
        self.ripple_spin.setObjectName(u"ripple_spin")
        self.ripple_spin.setDecimals(1)
        self.ripple_spin.setMinimum(0.100000000000000)
        self.ripple_spin.setMaximum(120.000000000000000)
        self.ripple_spin.setSingleStep(0.100000000000000)
        self.ripple_spin.setValue(3.000000000000000)

        self.formLayout_filter_params.setWidget(4, QFormLayout.FieldRole, self.ripple_spin)

        self.label_attenuation = QLabel(self.filters_group)
        self.label_attenuation.setObjectName(u"label_attenuation")

        self.formLayout_filter_params.setWidget(5, QFormLayout.LabelRole, self.label_attenuation)

        self.attenuation_spin = QDoubleSpinBox(self.filters_group)
        self.attenuation_spin.setObjectName(u"attenuation_spin")
        self.attenuation_spin.setDecimals(1)
        self.attenuation_spin.setMinimum(0.100000000000000)
        self.attenuation_spin.setMaximum(120.000000000000000)
        self.attenuation_spin.setSingleStep(0.100000000000000)
        self.attenuation_spin.setValue(20.000000000000000)

        self.formLayout_filter_params.setWidget(5, QFormLayout.FieldRole, self.attenuation_spin)


        self.verticalLayout_filters.addLayout(self.formLayout_filter_params)

        self.filter_tree = QTreeWidget(self.filters_group)
        self.filter_tree.setObjectName(u"filter_tree")
        sizePolicy4.setHeightForWidth(self.filter_tree.sizePolicy().hasHeightForWidth())
        self.filter_tree.setSizePolicy(sizePolicy4)
        self.filter_tree.setAlternatingRowColors(True)
        self.filter_tree.setIndentation(0)
        self.filter_tree.header().setMinimumSectionSize(40)

        self.verticalLayout_filters.addWidget(self.filter_tree)

        self.horizontalLayout_filter_actions = QHBoxLayout()
        self.horizontalLayout_filter_actions.setObjectName(u"horizontalLayout_filter_actions")
        self.preview_check = QCheckBox(self.filters_group)
        self.preview_check.setObjectName(u"preview_check")

        self.horizontalLayout_filter_actions.addWidget(self.preview_check)

        self.clear_button = QPushButton(self.filters_group)
        self.clear_button.setObjectName(u"clear_button")

        self.horizontalLayout_filter_actions.addWidget(self.clear_button)

        self.apply_filter_button = QPushButton(self.filters_group)
        self.apply_filter_button.setObjectName(u"apply_filter_button")

        self.horizontalLayout_filter_actions.addWidget(self.apply_filter_button)


        self.verticalLayout_filters.addLayout(self.horizontalLayout_filter_actions)


        self.verticalLayout_panel.addWidget(self.filters_group)

        self.info_label = QLabel(self.scroll_contents)
        self.info_label.setObjectName(u"info_label")
        self.info_label.setWordWrap(True)

        self.verticalLayout_panel.addWidget(self.info_label)

        self.control_scroll.setWidget(self.scroll_contents)
        self.main_splitter.addWidget(self.control_scroll)

        self.horizontalLayout_main.addWidget(self.main_splitter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 1400, 22))
        self.menuSettings = QMenu(self.menuBar)
        self.menuSettings.setObjectName(u"menuSettings")
        MainWindow.setMenuBar(self.menuBar)

        self.menuBar.addAction(self.menuSettings.menuAction())
        self.menuSettings.addAction(self.actionLine_Colors)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"WaveFilter", None))
        self.actionLine_Colors.setText(QCoreApplication.translate("MainWindow", u" Line Colors", None))
        self.actionLine_Colors.setIconText(QCoreApplication.translate("MainWindow", u" Line Colors", None))
        self.file_group.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.open_button.setText(QCoreApplication.translate("MainWindow", u"Open File", None))
        self.generate_button.setText(QCoreApplication.translate("MainWindow", u"Generate Test Signal", None))
        self.file_label.setText(QCoreApplication.translate("MainWindow", u"No file loaded", None))
        self.play_button.setText(QCoreApplication.translate("MainWindow", u"\u25b6 Play", None))
        self.stop_button.setText(QCoreApplication.translate("MainWindow", u"\u25fc Stop", None))
        self.fft_group.setTitle(QCoreApplication.translate("MainWindow", u"FFT", None))
        self.normalize_check.setText(QCoreApplication.translate("MainWindow", u"Normalize", None))
        self.window_check_fft.setText(QCoreApplication.translate("MainWindow", u"Hanning Window", None))
        self.label_fft_mode.setText(QCoreApplication.translate("MainWindow", u"FFT Mode", None))
        self.fft_mode_combo.setItemText(0, QCoreApplication.translate("MainWindow", u"FFT - Fast Fourier Transform", None))
        self.fft_mode_combo.setItemText(1, QCoreApplication.translate("MainWindow", u"IFFT - Inverse FFT", None))
        self.fft_mode_combo.setItemText(2, QCoreApplication.translate("MainWindow", u"RFFT - FFT of strictly real-valued sequence", None))
        self.fft_mode_combo.setItemText(3, QCoreApplication.translate("MainWindow", u"IRFFT - Inverse of RFFT", None))
        self.fft_mode_combo.setItemText(4, QCoreApplication.translate("MainWindow", u"HFFT - FFT of a Hermitian sequence (real spectrum)", None))
        self.fft_mode_combo.setItemText(5, QCoreApplication.translate("MainWindow", u"IHFFT - Inverse of HFFT", None))
        self.fft_mode_combo.setItemText(6, QCoreApplication.translate("MainWindow", u"DCT - Discrete cosine transform", None))
        self.fft_mode_combo.setItemText(7, QCoreApplication.translate("MainWindow", u"IDCT - Inverse DCT", None))
        self.fft_mode_combo.setItemText(8, QCoreApplication.translate("MainWindow", u"DST - Discrete sine transform", None))
        self.fft_mode_combo.setItemText(9, QCoreApplication.translate("MainWindow", u"IDST - Inverse DST", None))

        self.label_freq_thresh.setText(QCoreApplication.translate("MainWindow", u"\u2500\u2500 Frequency Thresholds \u2500\u2500", None))
        self.label_low_freq.setText(QCoreApplication.translate("MainWindow", u"Low Frequency", None))
        self.low_peak_freq_spin.setPrefix(QCoreApplication.translate("MainWindow", u"< ", None))
        self.low_peak_freq_spin.setSuffix(QCoreApplication.translate("MainWindow", u" Hz", None))
        self.label_high_freq.setText(QCoreApplication.translate("MainWindow", u"High Frequency", None))
        self.high_peak_freq_spin.setPrefix(QCoreApplication.translate("MainWindow", u"> ", None))
        self.high_peak_freq_spin.setSuffix(QCoreApplication.translate("MainWindow", u" Hz", None))
        self.label_min_amp.setText(QCoreApplication.translate("MainWindow", u"Min Peak Amplitude", None))
        self.kalman_check.setText(QCoreApplication.translate("MainWindow", u"Apply Kalman Filter", None))
        self.label_kalman_noise.setText(QCoreApplication.translate("MainWindow", u"Noise:", None))
        self.apply_fft_button.setText(QCoreApplication.translate("MainWindow", u"Apply FFT", None))
        self.plotting_group.setTitle(QCoreApplication.translate("MainWindow", u"Plotting", None))
        self.raw_visible_check.setText(QCoreApplication.translate("MainWindow", u"Raw Signal", None))
        self.filtered_visible_check.setText(QCoreApplication.translate("MainWindow", u"Filtered Signal", None))
        self.filters_group.setTitle(QCoreApplication.translate("MainWindow", u"Filters", None))
        self.window_check_filter.setText(QCoreApplication.translate("MainWindow", u"Hanning Window", None))
        self.filter_combo.setItemText(0, QCoreApplication.translate("MainWindow", u"Low Pass Filter", None))
        self.filter_combo.setItemText(1, QCoreApplication.translate("MainWindow", u"High Pass Filter", None))
        self.filter_combo.setItemText(2, QCoreApplication.translate("MainWindow", u"Band Pass Filter", None))
        self.filter_combo.setItemText(3, QCoreApplication.translate("MainWindow", u"Band Stop Filter", None))
        self.filter_combo.setItemText(4, QCoreApplication.translate("MainWindow", u"Notch Filter", None))
        self.filter_combo.setItemText(5, QCoreApplication.translate("MainWindow", u"Savitzky-Golay Filter", None))
        self.filter_combo.setItemText(6, QCoreApplication.translate("MainWindow", u"IFFT / Kalman Filter", None))

        self.label_filter_low.setText(QCoreApplication.translate("MainWindow", u"Low Frequency", None))
        self.filter_low_spin.setSuffix(QCoreApplication.translate("MainWindow", u" Hz", None))
        self.label_filter_high.setText(QCoreApplication.translate("MainWindow", u"High Frequency", None))
        self.filter_high_spin.setSuffix(QCoreApplication.translate("MainWindow", u" Hz", None))
        self.label_filter_order.setText(QCoreApplication.translate("MainWindow", u"Order", None))
        self.label_filter_design.setText(QCoreApplication.translate("MainWindow", u"Design", None))
        self.filter_design_combo.setItemText(0, QCoreApplication.translate("MainWindow", u"Butterworth", None))
        self.filter_design_combo.setItemText(1, QCoreApplication.translate("MainWindow", u"Chebyshev I", None))
        self.filter_design_combo.setItemText(2, QCoreApplication.translate("MainWindow", u"Chebyshev II", None))
        self.filter_design_combo.setItemText(3, QCoreApplication.translate("MainWindow", u"Elliptic", None))
        self.filter_design_combo.setItemText(4, QCoreApplication.translate("MainWindow", u"Bessel", None))

        self.label_ripple.setText(QCoreApplication.translate("MainWindow", u"Ripple (dB)", None))
        self.ripple_spin.setSuffix(QCoreApplication.translate("MainWindow", u" dB", None))
        self.label_attenuation.setText(QCoreApplication.translate("MainWindow", u"Attenuation (dB)", None))
        self.attenuation_spin.setSuffix(QCoreApplication.translate("MainWindow", u" dB", None))
        ___qtreewidgetitem = self.filter_tree.headerItem()
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("MainWindow", u"Parameters", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", u"Filter", None));
        self.preview_check.setText(QCoreApplication.translate("MainWindow", u"Preview", None))
        self.clear_button.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.apply_filter_button.setText(QCoreApplication.translate("MainWindow", u"Apply Filter", None))
        self.info_label.setStyleSheet(QCoreApplication.translate("MainWindow", u"color: gray;", None))
        self.info_label.setText(QCoreApplication.translate("MainWindow", u"Open a file to begin.", None))
        self.menuSettings.setTitle(QCoreApplication.translate("MainWindow", u"Settings", None))
    # retranslateUi

