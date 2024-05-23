#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph
import serial
import threading
import time
import signal
from serial.tools import list_ports

signal.signal(signal.SIGINT, signal.SIG_DFL)


class SettingFrame(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()
        self.combo_box_port_path = QtWidgets.QComboBox()
        for desc in list_ports.comports():
            self.combo_box_port_path.addItem(desc.device)
        dev_id = self.combo_box_port_path.findText("/dev/ttyACM0")
        self.combo_box_port_path.setCurrentIndex(0 if dev_id == -1 else dev_id)
        self.combo_box_port_path.setEditable(True)

        self.push_button_open = QtWidgets.QPushButton("Open")
        self.combo_box_speed = QtWidgets.QComboBox()
        for speed in serial.Serial.BAUDRATES:
            self.combo_box_speed.addItem(str(speed), speed)
        self.combo_box_speed.setCurrentIndex(
            self.combo_box_speed.findData(115200))

        self.combo_box_splitter = QtWidgets.QComboBox()
        self.combo_box_splitter.addItem('CR(\\r)', b'\r')
        self.combo_box_splitter.addItem('LF(\\n)', b'\n')

        self.spin_box_max_points = QtWidgets.QSpinBox()
        self.spin_box_max_points.setMaximum(2147483647)
        self.spin_box_max_points.setValue(10000)

        self.spin_box_max_points.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Fixed)

        v_box_layout = QtWidgets.QVBoxLayout(self)
        h_box_layout = QtWidgets.QHBoxLayout(self)
        v_box_layout.addLayout(h_box_layout)

        self.push_button_clear = QtWidgets.QPushButton("Clear")
        self.push_button_pause = QtWidgets.QPushButton("Pause")

        h_box_layout_graphs = QtWidgets.QHBoxLayout(self)
        v_box_layout.addLayout(h_box_layout_graphs)
        h_box_layout_graphs.addWidget(QtWidgets.QLabel("Max points:"))
        h_box_layout_graphs.addWidget(self.spin_box_max_points)
        h_box_layout_graphs.addWidget(self.combo_box_splitter)
        h_box_layout_graphs.addWidget(self.push_button_clear)
        h_box_layout_graphs.addWidget(self.push_button_pause)
        h_box_layout_graphs.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Expanding))

        self.combo_box_port_path.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed)

        self.combo_box_speed.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Fixed)

        h_box_layout.addWidget(self.combo_box_port_path)
        h_box_layout.addWidget(self.push_button_open)
        h_box_layout.addWidget(self.combo_box_speed)


class ConsoleFrame(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()
        self.combo_box_cmd = QtWidgets.QComboBox()
        self.combo_box_cmd.setEditable(True)
        self.push_button_send = QtWidgets.QPushButton("Send")
        self.ser = None
        self.splitter = None

        self.combo_box_cmd.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed)

        self.push_button_send.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Fixed)

        h_box_layout = QtWidgets.QHBoxLayout(self)
        h_box_layout.addWidget(self.combo_box_cmd)
        h_box_layout.addWidget(self.push_button_send)

        self.push_button_send.clicked.connect(self.send)
        self.set_serial(None, None)

    def set_serial(self, ser, splitter):
        self.ser = ser
        self.splitter = splitter
        if ser:
            self.combo_box_cmd.setEnabled(True)
            self.push_button_send.setEnabled(True)
        else:
            self.combo_box_cmd.setEnabled(False)
            self.push_button_send.setEnabled(False)

    def send(self):
        if self.ser:
            data = self.combo_box_cmd.currentText().encode() + self.splitter
            self.ser.write(data)


class MainWindow(QtWidgets.QMainWindow):
    max_len = 10000
    timeout = 2
    GRAPH_WIDTH = 2
    COLOURS = [
        QtGui.QColor(QtCore.Qt.white),
        QtGui.QColor(QtCore.Qt.red),
        QtGui.QColor(QtCore.Qt.darkRed),
        QtGui.QColor(QtCore.Qt.green),
        QtGui.QColor(QtCore.Qt.lightGray),
        QtGui.QColor(QtCore.Qt.blue),
        QtGui.QColor(QtCore.Qt.cyan),
        QtGui.QColor(QtCore.Qt.magenta),
        QtGui.QColor(QtCore.Qt.yellow),
        QtGui.QColor(QtCore.Qt.darkRed),
        QtGui.QColor(QtCore.Qt.darkGreen),
        QtGui.QColor(QtCore.Qt.darkBlue),
        QtGui.QColor(QtCore.Qt.darkCyan),
        QtGui.QColor(QtCore.Qt.darkMagenta),
        QtGui.QColor(QtCore.Qt.darkYellow)]

    UPDATE_RATE = 80  # ms

    def __init__(self):
        super().__init__()
        # Temperature vs time plot
        self.plot_graph = pyqtgraph.PlotWidget(self)
        self.setCentralWidget(self.plot_graph)
        self.plot_graph.setLabel("left", "value")
        self.plot_graph.setLabel("bottom", "time")
        self.plot_graph.setTitle("test curve")
        self.plot_graph.showGrid(x=True, y=True)
        self.legend = self.plot_graph.addLegend()

        self.settings_frame = SettingFrame()

        dock_widget = QtWidgets.QDockWidget("Port settings", self)
        dock_widget.setAllowedAreas(
            QtCore.Qt.AllDockWidgetAreas)
        dock_widget.setWidget(self.settings_frame)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, dock_widget)

        self.settings_frame.push_button_open.clicked.connect(self.on_open_port)
        self.settings_frame.push_button_clear.clicked.connect(self.clear)
        self.settings_frame.push_button_pause.clicked.connect(self.pause)

        self.curves = {}
        self.exit_flag = threading.Event()
        self.ser = None
        self.lock = threading.Lock()
        self.results = {}

        self.serial_thread = None
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(self.UPDATE_RATE)
        self.setWindowState(QtCore.Qt.WindowMaximized)

        self.console_frame = ConsoleFrame()
        dock_widget = QtWidgets.QDockWidget("Console", self)
        dock_widget.setAllowedAreas(
            QtCore.Qt.AllDockWidgetAreas)
        dock_widget.setWidget(self.console_frame)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock_widget)

    def on_open_port(self):
        if self.ser is None:
            try:
                path = self.settings_frame.combo_box_port_path.currentText()
                baudrate = self.settings_frame.combo_box_speed.currentData()
                self.ser = serial.Serial(
                    path, baudrate=baudrate, timeout=self.timeout)

                self.serial_thread = threading.Thread(target=self.read_serial)
                self.exit_flag.clear()
                self.serial_thread.start()
                self.settings_frame.push_button_open.setText("close")
                self.settings_frame.combo_box_port_path.setEnabled(False)
                self.settings_frame.combo_box_speed.setEnabled(False)
                self.settings_frame.combo_box_splitter.setEnabled(False)
                self.console_frame.set_serial(
                    self.ser,
                    self.settings_frame.combo_box_splitter.currentData())

            except serial.serialutil.SerialException as e:
                QtWidgets.QMessageBox.warning(
                    self, "Warning", str(e))
        else:
            self.exit_flag.set()
            self.serial_thread.join()
            self.ser = None
            self.settings_frame.push_button_open.setText("open")
            self.settings_frame.combo_box_port_path.setEnabled(True)
            self.settings_frame.combo_box_speed.setEnabled(True)
            self.settings_frame.combo_box_splitter.setEnabled(True)
            self.console_frame.set_serial(None, None)

    def clear(self):
        with self.lock:
            self.plot_graph.clear()
            self.results = {}
            self.curves = {}

    def pause(self):
        if self.timer.isActive():
            self.timer.stop()
            self.settings_frame.push_button_pause.clicked.setText("Play")
        else:
            self.timer.start(self.UPDATE_RATE)
            self.settings_frame.push_button_pause.clicked.setText("Pause")

    def read_serial(self):
        spliter = self.settings_frame.combo_box_splitter.currentData()
        with self.ser:
            while not self.exit_flag.is_set():
                row_line = self.ser.read_until(spliter)

                for line in row_line.splitlines():
                    data = line.strip().split()
                    if not data:
                        continue
                    try:
                        data = [float(d) for d in data]
                        cur_time = time.time()
                        self.put(cur_time, data)
                    except ValueError as e:
                        print(f'error:{e} line:{row_line}')

    def put(self, cur_time, data):
        with self.lock:
            for index, value in enumerate(data):
                store = self.results.setdefault(index, [[], []])
                store[0].append(cur_time)
                store[1].append(value)

    def get(self):
        with self.lock:
            res = self.results
            self.results = {}
            return res

    def update(self):
        res = self.get()

        if not res:
            return
        max_len = self.settings_frame.spin_box_max_points.value()
        for index, data in res.items():
            _time, val = data
            desc = self.curves.setdefault(index, {})
            desc.setdefault('time', []).extend(_time)
            desc.setdefault('val', []).extend(val)
            desc['time'] = desc['time'][-max_len:]
            desc['val'] = desc['val'][-max_len:]

            if 'curve' not in desc:
                curve = pyqtgraph.PlotCurveItem()
                pen = pyqtgraph.mkPen(
                    self.COLOURS[index % len(self.COLOURS)],
                    width=self.GRAPH_WIDTH)
                curve.setPen(pen)
                self.legend.addItem(
                    curve,
                    f"{index}")

                self.plot_graph.addItem(curve)
                desc['curve'] = curve
            else:
                curve = desc['curve']
            curve.setData(desc['time'], desc['val'])

    def closeEvent(self, event):
        self.exit_flag.set()
        event.accept()


app = QtWidgets.QApplication([])
main = MainWindow()
main.show()
app.exec()