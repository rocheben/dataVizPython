
import sys
import csv
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QFileDialog, QWidget
from PyQt5.QtCore import Qt


class CSVViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CSV Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.button = QPushButton("Load CSV")
        self.button.clicked.connect(self.load_csv)
        self.layout.addWidget(self.button)

        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)

    def load_csv(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)", options=options)

        if file_name:
            self.plot_csv(file_name)

    def plot_csv(self, file_name):
        x = []
        y = []

        with open(file_name, "r") as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header
            for row in csv_reader:
                x.append(float(row[0]))
                y.append(float(row[1]))

        self.plot_widget.plot(x, y, clear=True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = CSVViewer()
    viewer.show()
    sys.exit(app.exec_())
