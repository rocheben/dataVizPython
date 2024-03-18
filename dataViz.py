import sys
import csv
import os.path
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QFileDialog, QWidget, QComboBox, QLabel, QTabWidget, QListWidget, QMessageBox
from PyQt5.QtCore import QDateTime
import pyqtgraph as pg
from scipy.stats import pearsonr
from statsmodels.formula.api import glm
import pandas as pd


class CSVViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CSV Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.tab1 = QWidget()
        self.tab_widget.addTab(self.tab1, "Select File")

        self.tab2 = QWidget()
        self.tab_widget.addTab(self.tab2, "Select Columns")

        self.tab3 = QWidget()
        self.tab_widget.addTab(self.tab3, "Select Columns for GLM")

        self.init_file_selection_tab()
        self.init_column_selection_tab()
        self.init_glm_column_selection_tab()

    def init_file_selection_tab(self):
        layout = QVBoxLayout()
        self.tab1.setLayout(layout)

        self.button_load = QPushButton("Load CSV")
        self.button_load.clicked.connect(self.load_csv)
        layout.addWidget(self.button_load)

        self.file_name_label = QLabel()
        layout.addWidget(self.file_name_label)

        self.file_summary_label = QLabel()
        layout.addWidget(self.file_summary_label)

        self.file_name = None

    def init_column_selection_tab(self):
        layout = QVBoxLayout()
        self.tab2.setLayout(layout)

        self.column_list = QListWidget()
        self.column_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.column_list)

        self.plot_button = QPushButton("Plot")
        self.plot_button.clicked.connect(self.plot_columns)
        layout.addWidget(self.plot_button)

        self.correlation_label = QLabel()
        layout.addWidget(self.correlation_label)

        self.pvalue_label = QLabel()
        layout.addWidget(self.pvalue_label)

        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)

    def init_glm_column_selection_tab(self):
        layout = QVBoxLayout()
        self.tab3.setLayout(layout)

        self.response_variable_label = QLabel("Response Variable:")
        layout.addWidget(self.response_variable_label)

        self.response_variable_combo = QComboBox()
        layout.addWidget(self.response_variable_combo)

        self.explanatory_variables_label = QLabel("Explanatory Variables:")
        layout.addWidget(self.explanatory_variables_label)

        self.explanatory_variables_list = QListWidget()
        self.explanatory_variables_list.setSelectionMode(QListWidget.MultiSelection)  # Autorise la sélection multiple
        layout.addWidget(self.explanatory_variables_list)

        self.glm_button = QPushButton("Run GLM")
        self.glm_button.clicked.connect(self.run_glm)
        layout.addWidget(self.glm_button)

        self.glm_results_label = QLabel()
        layout.addWidget(self.glm_results_label)

    def load_csv(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)", options=options)

        if file_name:
            self.file_name = file_name
            self.file_name_label.setText(f"Loaded File: {self.file_name}")
            self.populate_column_list()
            self.update_file_summary()
            self.populate_glm_variables()

    def populate_column_list(self):
        self.column_list.clear()

        with open(self.file_name, "r") as file:
            csv_reader = csv.reader(file)
            header = next(csv_reader)
            self.column_list.addItems(header)

    def update_file_summary(self):
        if self.file_name:
            num_lines = sum(1 for line in open(self.file_name))
            with open(self.file_name, 'r') as file:
                num_columns = len(file.readline().strip().split(','))
            last_modified = os.path.getmtime(self.file_name)
            last_modified_str = QDateTime.fromSecsSinceEpoch(int(last_modified)).toString()
            self.file_summary_label.setText(f"Number of Lines: {num_lines}, Number of Columns: {num_columns}, Last Modified: {last_modified_str}")

    def plot_columns(self):
        if not self.file_name:
            return

        selected_columns = [item.text() for item in self.column_list.selectedItems()]
        if len(selected_columns) != 2:
            QMessageBox.warning(self, "Warning", "Please select exactly two columns.")
            return

        data = {}
        with open(self.file_name, "r") as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                for column in selected_columns:
                    if column not in data:
                        data[column] = []
                    data[column].append(float(row[column]))

        correlation, p_value = pearsonr(data[selected_columns[0]], data[selected_columns[1]])
        self.correlation_label.setText(f"Correlation: {correlation}")
        self.pvalue_label.setText(f"P-value: {p_value}")

        self.plot_widget.clear()
        self.plot_widget.plot(data[selected_columns[1]], data[selected_columns[0]], pen=None, symbol='o')

    def populate_glm_variables(self):
        with open(self.file_name, "r") as file:
            csv_reader = csv.reader(file)
            header = next(csv_reader)
            self.response_variable_combo.addItems(header)
            self.explanatory_variables_list.addItems(header)

    def run_glm(self):
        if not self.file_name:
            return

        response_variable = self.response_variable_combo.currentText()
        explanatory_variables = [item.text() for item in self.explanatory_variables_list.selectedItems()]

        if not response_variable:
            QMessageBox.warning(self, "Warning", "Please select a response variable.")
            return
        if not explanatory_variables:
            QMessageBox.warning(self, "Warning", "Please select at least one explanatory variable.")
            return

        # Charger les données dans un DataFrame pandas
        df = pd.read_csv(self.file_name)

        # Construire la formule de régression
        formula = f"{response_variable} ~ {' + '.join(explanatory_variables)}"

        # Exécuter la régression
        try:
            model = glm(formula, data=df).fit()
            self.glm_results_label.setText(str(model.summary()))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = CSVViewer()
    viewer.show()
    sys.exit(app.exec_())
