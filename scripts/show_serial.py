#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph
import serial
import threading
import time
import signal
from serial.tools import list_ports

Settings = QtCore.QSettings('alexlexx', 'graph_view')
signal.signal(signal.SIGINT, signal.SIG_DFL)


class SettingFrame(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()
        self.combo_box_port_path = QtWidgets.QComboBox()
        self.combo_box_port_path.setToolTip("Path to the COM port file")
        for desc in list_ports.comports():
            self.combo_box_port_path.addItem(desc.device)
        port_path = Settings.value("port_path")
        dev_id = self.combo_box_port_path.findText(
            port_path if port_path is not None else "/dev/ttyACM0")

        self.combo_box_port_path.setCurrentIndex(0 if dev_id == -1 else dev_id)
        self.combo_box_port_path.setEditable(True)
        self.combo_box_port_path.currentTextChanged.connect(
            self.on_port_changed)

        self.push_button_open = QtWidgets.QPushButton("Open")
        self.push_button_open.setToolTip(
            "Open/Close the COM port for reading/writing.")
        self.combo_box_speed = QtWidgets.QComboBox()
        self.combo_box_speed.setToolTip("List of standard COM port speeds")
        for speed in serial.Serial.BAUDRATES:
            self.combo_box_speed.addItem(str(speed), speed)

        speed = Settings.value("port_speed")
        speed = int(speed) if speed is not None else 115200
        self.combo_box_speed.setCurrentIndex(
            self.combo_box_speed.findData(speed))
        self.combo_box_speed.currentIndexChanged.connect(self.on_speed_changed)

        self.group_box_line_parsing = QtWidgets.QGroupBox(self)
        self.group_box_line_parsing.setTitle('Line parsing')
        self.group_box_line_parsing.setToolTip(
            "Enable string parsing mode to display graphs")
        self.group_box_line_parsing.setCheckable(True)
        self.group_box_line_parsing.toggled.connect(
            self.on_string_parsing_changed)
        string_parsing = Settings.value("string_parsing")
        string_parsing = int(string_parsing) if string_parsing is not None else 1
        self.group_box_line_parsing.setChecked(string_parsing)

        self.spin_box_max_points = QtWidgets.QSpinBox()
        self.spin_box_max_points.setMaximum(2147483647)
        self.spin_box_max_points.setValue(10000)
        self.spin_box_max_points.setToolTip(
            "Maximum number of points displayed on graphs.")

        self.spin_box_max_points.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Fixed)

        v_box_layout = QtWidgets.QVBoxLayout(self)
        h_box_layout = QtWidgets.QHBoxLayout()
        v_box_layout.addLayout(h_box_layout)

        self.push_button_clear = QtWidgets.QPushButton("Clear")
        self.push_button_clear.setToolTip(
            "Delete all data displayed on the graphs.")

        self.push_button_pause = QtWidgets.QPushButton("Pause")
        self.push_button_pause.setToolTip(
            "Suspend updating data on the graphs "
            "(data is not lost, it accumulates in the background).")

        self.check_box_flat_mode = QtWidgets.QCheckBox("Flat_mode")
        self.check_box_flat_mode.setToolTip(
            "This mode replaces the time-based display with a "
            "dot display (data for the dots: "
            "x - the first element of the row, y - the second element).")

        self.check_box_show_only_cmd_response = QtWidgets.QCheckBox(
            "Only response")
        self.check_box_show_only_cmd_response.setToolTip(
            "Display only responses to commands "
            "(everything that starts with RE and ER) in the console.")

        h_box_layout_graphs = QtWidgets.QHBoxLayout(self.group_box_line_parsing)
        v_box_layout.addWidget(self.group_box_line_parsing)
        h_box_layout_graphs.addWidget(QtWidgets.QLabel("Max points:"))
        h_box_layout_graphs.addWidget(self.spin_box_max_points)
        h_box_layout_graphs.addWidget(self.push_button_clear)
        h_box_layout_graphs.addWidget(self.push_button_pause)
        h_box_layout_graphs.addWidget(self.check_box_flat_mode)
        h_box_layout_graphs.addWidget(self.check_box_show_only_cmd_response)
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

    def on_port_changed(self, port_path):
        Settings.setValue('port_path', port_path),

    def on_speed_changed(self, index):
        speed = self.combo_box_speed.itemData(index)
        Settings.setValue("port_speed", speed)

    def on_string_parsing_changed(self, value):
        Settings.setValue("string_parsing", int(value))


class ConsoleFrame(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()
        self.combo_box_cmd = QtWidgets.QComboBox()
        self.combo_box_cmd.setEditable(True)
        self.combo_box_cmd.setToolTip(
            "Enter a new command and press the Enter button to send "
            "(includes command history).")
        self.push_button_send = QtWidgets.QPushButton("Send")
        self.push_button_send.setToolTip("Send command to port.")
        self.ser = None
        self.splitter = None

        self.combo_box_cmd.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Fixed)

        self.push_button_send.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Fixed)

        v_box_layout = QtWidgets.QVBoxLayout(self)
        h_box_layout = QtWidgets.QHBoxLayout()
        v_box_layout.addLayout(h_box_layout)

        h_box_layout.addWidget(self.combo_box_cmd)
        h_box_layout.addWidget(self.push_button_send)

        self.plain_text_editor = QtWidgets.QPlainTextEdit()
        self.plain_text_editor.setToolTip(
            "Displays incoming stream from the COM port.")
        self.plain_text_editor.setReadOnly(True)
        v_box_layout.addWidget(self.plain_text_editor)

        self.push_button_send.clicked.connect(self.send)
        self.set_serial(None, None)

        self.clear_action = QtWidgets.QAction("Clear")
        self.plain_text_editor.addAction(self.clear_action)
        self.clear_action.triggered.connect(self.on_clear_history)
        self.plain_text_editor.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.ActionsContextMenu)
        self.combo_box_cmd.lineEdit().editingFinished.connect(self.send)
        self.combo_box_cmd.currentIndexChanged.connect(
            self.on_currentIndexChanged)

        commands = Settings.value("commands")
        last_commands_index = Settings.value("last_commands_index")

        if commands is not None and last_commands_index is not None:
            last_block = self.combo_box_cmd.blockSignals(True)
            self.combo_box_cmd.addItems(commands)
            self.combo_box_cmd.setCurrentIndex(int(last_commands_index))
            self.combo_box_cmd.blockSignals(last_block)

        history = Settings.value("history")
        if history:
            self.plain_text_editor.setPlainText(history)

        self.remove_action = QtWidgets.QAction("Remove")
        self.combo_box_cmd.addAction(self.remove_action)
        self.remove_action.triggered.connect(self.on_remove_item)

        self.remove_all_action = QtWidgets.QAction("Remove All")
        self.combo_box_cmd.addAction(self.remove_all_action)
        self.remove_all_action.triggered.connect(self.on_remove_all_item)

        self.combo_box_cmd.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.ActionsContextMenu)

    def on_remove_all_item(self):
        if QtWidgets.QMessageBox.question(
            self,
            'Remove all commands',
            "Are you sure you want to remove all items?") ==\
                QtWidgets.QMessageBox.StandardButton.Yes:
            self.combo_box_cmd.clear()

    def on_remove_item(self):
        self.combo_box_cmd.removeItem(
            self.combo_box_cmd.currentIndex())

    def on_clear_history(self):
        self.plain_text_editor.clear()
        Settings.setValue("history", "")

    def set_serial(self, ser, splitter):
        self.ser = ser
        self.splitter = splitter
        if ser:
            self.combo_box_cmd.setEnabled(True)
            self.push_button_send.setEnabled(True)
            self.plain_text_editor.setEnabled(True)
        else:
            self.combo_box_cmd.setEnabled(False)
            self.push_button_send.setEnabled(False)
            self.plain_text_editor.setEnabled(False)

    def send(self):
        if self.ser:
            line = self.combo_box_cmd.currentText()
            cursor = QtGui.QTextCursor(self.plain_text_editor.document())
            cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
            cursor.insertText(line)
            Settings.setValue("history", self.plain_text_editor.toPlainText())
            data = line.encode()
            self.ser.write(data)

    def on_currentIndexChanged(self, index):
        Settings.setValue(
            "commands",
            [self.combo_box_cmd.itemText(index) for index in range(self.combo_box_cmd.count())])
        Settings.setValue("last_commands_index",
                          self.combo_box_cmd.currentIndex())

    def on_new_line(self, line):
        cursor = QtGui.QTextCursor(self.plain_text_editor.document())
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
        cursor.insertText(line.decode())


class MainWindow(QtWidgets.QMainWindow):
    max_len = 10000
    timeout = 0.5
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
    NEW_LINE = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Graph View")
        self.points = {}

        self.plot_graph = pyqtgraph.PlotWidget(self)
        self.setCentralWidget(self.plot_graph)
        self.plot_graph.setLabel("left", "value")
        self.plot_graph.setLabel("bottom", "time")
        self.plot_graph.setTitle("test curve")
        self.plot_graph.showGrid(x=True, y=True)
        self.legend = self.plot_graph.addLegend()

        self.settings_frame = SettingFrame()

        self.settings_dock_widget = QtWidgets.QDockWidget(
            "Port settings", self)
        self.settings_dock_widget.setFeatures(
            QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.settings_dock_widget.setAllowedAreas(
            QtCore.Qt.AllDockWidgetAreas)
        self.settings_dock_widget.setWidget(self.settings_frame)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea,
                           self.settings_dock_widget)

        self.settings_frame.push_button_open.clicked.connect(self.on_open_port)
        self.settings_frame.push_button_clear.clicked.connect(
            self.on_clear_graphs)
        self.settings_frame.push_button_pause.clicked.connect(self.pause)
        self.settings_frame.check_box_flat_mode.toggled.connect(
            self.flat_mode_changed)
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
        self.NEW_LINE.connect(self.console_frame.on_new_line)
        self.console_dock_widget = QtWidgets.QDockWidget("Console", self)
        self.console_dock_widget.setFeatures(
            QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetFloatable)

        self.console_dock_widget.setAllowedAreas(
            QtCore.Qt.AllDockWidgetAreas)
        self.console_dock_widget.setWidget(self.console_frame)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea,
                           self.console_dock_widget)

        self.file_menu = self.menuBar().addMenu("&View")

        self.show_settings = QtWidgets.QAction("Settings")
        self.show_settings.setCheckable(True)
        self.show_settings.setChecked(True)
        self.file_menu.addAction(self.show_settings)
        self.show_settings.triggered.connect(
            self.settings_dock_widget.setVisible)

        self.show_console = QtWidgets.QAction("Console")
        self.show_console.setCheckable(True)
        self.show_console.setChecked(True)
        self.file_menu.addAction(self.show_console)
        self.show_console.triggered.connect(
            self.console_dock_widget.setVisible)

        self.help_menu = self.menuBar().addMenu("&Help")
        self.action_about = QtWidgets.QAction("About")
        self.help_menu.addAction(self.action_about)
        self.action_about.triggered.connect(self.on_help)

    def on_clear_graphs(self):
        self.clear(False)

    def on_help(self):
        QtWidgets.QMessageBox.about(
            self,
            "Help",
            "Purpose of the application:\nThe application reads data from the COM port, "
            "parses each line as a set of floats separated by spaces/tabs, "
            "and then displays the data on graphs. \n"
            "The timestamp used is the moment when the data is read from the port.\n\n"
            "This is my attempt to fight against the stupid implementation of  "
            "Serial Monitor and Serial Plotter in the Arduino IDE.\n\n"
            "Author:\n"
            "Alexey Kalmykov\n"
            "alexlexx1@gmail.com")

    def on_open_port(self):
        if self.ser is None:
            try:
                path = self.settings_frame.combo_box_port_path.currentText()
                baudrate = self.settings_frame.combo_box_speed.currentData()
                self.ser = serial.Serial(
                    path, baudrate=baudrate, timeout=self.timeout)

                self.serial_thread = threading.Thread(target=self.read_serial)
                self.exit_flag.clear()
                self.clear()
                self.serial_thread.start()
                self.settings_frame.push_button_open.setText("close")
                self.settings_frame.combo_box_port_path.setEnabled(False)
                self.settings_frame.combo_box_speed.setEnabled(False)
                self.settings_frame.group_box_line_parsing.setEnabled(False)
                self.console_frame.set_serial(
                    self.ser,
                    self.settings_frame.group_box_line_parsing.isChecked())

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
            self.settings_frame.group_box_line_parsing.setEnabled(True)
            self.console_frame.set_serial(None, None)

    def clear(self, remove_items=True):
        with self.lock:
            self.results = {}
            self.points = {}

            if remove_items:
                self.plot_graph.clear()
                self.curves = {}
            else:
                for _id, desc in self.curves.items():
                    desc['time'] = []
                    desc['val'] = []
                    desc['curve'].clear()

    def pause(self):
        if self.timer.isActive():
            self.timer.stop()
            self.settings_frame.push_button_pause.setText("Play")
        else:
            self.timer.start(self.UPDATE_RATE)
            self.settings_frame.push_button_pause.setText("Pause")

    def flat_mode_changed(self, state):
        if state:
            self.plot_graph.setAspectLocked(lock=True)
            self.clear()
            self.plot_graph.setLabel("left", "Y")
            self.plot_graph.setLabel("bottom", "X")
        else:
            self.plot_graph.setAspectLocked(lock=False)
            self.clear()
            self.plot_graph.setLabel("left", "value")
            self.plot_graph.setLabel("bottom", "time")

    def read_serial(self):
        is_string_parsing = self.settings_frame.group_box_line_parsing.isChecked()
        with self.ser:
            # row mode
            if not is_string_parsing:
                while not self.exit_flag.is_set():
                    symbol = self.ser.read(100)
                    if symbol:
                        self.NEW_LINE.emit(symbol)
            # string parsing
            else:
                splitter = b''
                state = 0
                # detect string splitter
                while not self.exit_flag.is_set():
                    symbol = self.ser.read(1)
                    if state == 0 and symbol not in b'\r\n':
                        state = 1
                    elif state == 1:
                        if symbol in b'\r\n':
                            splitter += symbol
                        elif splitter:
                            break
                else:
                    return
                self.process_line(
                    symbol + self.ser.read_until(splitter), time.time())
                while not self.exit_flag.is_set():
                    self.process_line(
                        self.ser.read_until(splitter), time.time())

    def process_line(self, row_line, cur_time):
        strip_line = row_line.strip()
        if strip_line:
            if not self.settings_frame.check_box_show_only_cmd_response.isChecked() or\
                    strip_line[:2] in [b'RE', b'ER']:
                self.NEW_LINE.emit(strip_line + b'\n')
            data = strip_line.split()
            if data:
                try:
                    data = [float(d) for d in data]
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

        # draw graphs
        if not self.settings_frame.check_box_flat_mode.isChecked():
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
        # draw points
        else:
            # use first and second value as x, y coordinates
            if 0 in res and 1 in res:
                # first points pair
                index = 0
                desc = self.points.setdefault(0, {'x': [], 'y': []})
                desc['x'].extend(res[0][1])
                desc['y'].extend(res[1][1])
                desc['x'] = desc['x'][-max_len:]
                desc['y'] = desc['y'][-max_len:]

                # creating of scatter
                scatter = desc.get("scatter")
                if scatter is None:
                    scatter = pyqtgraph.ScatterPlotItem()
                    pen = pyqtgraph.mkPen(
                        self.COLOURS[index % len(self.COLOURS)],
                        width=self.GRAPH_WIDTH)
                    scatter.setPen(pen)
                    self.legend.addItem(
                        scatter,
                        f"{index}")

                    self.plot_graph.addItem(scatter)
                    desc['scatter'] = scatter
                # update points in scatter
                scatter.setData(desc['x'], desc['y'])

    def closeEvent(self, event):
        self.exit_flag.set()
        event.accept()


app = QtWidgets.QApplication([])
main = MainWindow()
main.show()
app.exec()
