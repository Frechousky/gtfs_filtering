from dataclasses import dataclass
from io import StringIO
from os.path import join
from sys import argv
from typing import List
from zipfile import ZipFile

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QLineEdit, QMainWindow, QPushButton, QWidget,
                             QFileDialog, QFormLayout, QMessageBox, QListWidget, QAbstractItemView)
from pandas import read_csv

from gtfs_filtering.core import FilterType, perform_filter

APP_NAME = "GTFS Filtering"

WARNING_NO_FILTER_VALUES = "Veuillez sélectionner au moins un valeur à filtrer"
WARNING_INPUT_GTFS_NOT_SELECTED = "Veuillez sélectionner le GTFS à filtrer"
ERROR_READING_INPUT_GTFS = ("Erreur lors de la lecture du GTFS à filtrer. Vérifier que le GTFS existe et qu'il est "
                            "valide")
ERROR_LABEL = "Erreur"
SUCCESS_LABEL = "Succès"
WARNING_LABEL = "Avertissement"
FILTER_VALUES_LABEL = "Valeur à filtrer"
FILTERING_IS_SUCCESSFUL = "Filtrage réaliser avec succès"
START_FILTERING_LABEL = "Lancer le filtrage"
OUTPUT_GTFS_FOLDER_SELECT_CAPTION_LABEL = "Sélectionner le dossier de sortie"
INPUT_GTFS_SELECT_FILTER_LABEL = "Fichier zip (*.zip)"
INPUT_GTFS_SELECT_CAPTION_LABEL = "Sélectionner le GTFS à filtrer"
FILTER_TYPE_LABEL = "Type de filtre"
OVERWRITE_OUTPUT_GTFS_LABEL = "Ecraser le GTFS de sortie s'il existe ?"
OUTPUT_GTFS_FULLPATH_LABEL = "Chemin complet vers l'archive de sortie"
OUTPUT_GTFS_FOLDER_LABEL = "Sélection du répertoire de sortie"
OUTPUT_GTFS_FILENAME_LABEL = "Nom de l'archive de sortie"
INPUT_GTFS_LABEL = "GTFS à filtrer"
SELECT_INPUT_GTFS_LABEL = "Sélection du GTFS à filtrer (.zip)"
SELECT_LABEL = "Sélectionner"
DELETE_FILTER_VALUES_LABEL = "Supprimer la/les valeur(s) à filtrer sélectionnée(s)"


@dataclass
class MainWindowModel:
    input_gtfs_zip: str = None
    output_gtfs_zip_folder: str = "."
    output_gtfs_zip_filename: str = "output_gtfs.zip"
    filter_type: FilterType = FilterType.ROUTE_ID
    route_ids_from_input_gtfs: List[str] = None
    trip_ids_from_input_gtfs: List[str] = None

    def output_gtfs_zip_fullpath(self):
        return join(self.output_gtfs_zip_folder, self.output_gtfs_zip_filename)


def open_error_message_box(message: str):
    QMessageBox(QMessageBox.Icon.Critical, ERROR_LABEL, message).exec()


def open_warning_message_box(message: str):
    QMessageBox(QMessageBox.Icon.Warning, WARNING_LABEL, message).exec()


def open_success_message_box(message: str):
    QMessageBox(QMessageBox.Icon.Information, SUCCESS_LABEL, message).exec()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(APP_NAME)
        self.model = MainWindowModel()

        main_layout = QFormLayout()

        # GTFS input zip
        self.input_gtfs_zip_select_button = QPushButton(text=SELECT_LABEL)
        self.input_gtfs_zip_selected_file_line_edit = QLineEdit()
        self.input_gtfs_zip_selected_file_line_edit.setReadOnly(True)

        # GTFS output zip
        self.output_gtfs_zip_folder_select_button = QPushButton(text=SELECT_LABEL)
        self.output_gtfs_zip_folder_line_edit = QLineEdit(text=self.model.output_gtfs_zip_folder)
        self.output_gtfs_zip_folder_line_edit.setReadOnly(True)
        self.output_gtfs_zip_filename_line_edit = QLineEdit(text=self.model.output_gtfs_zip_filename)
        self.output_gtfs_zip_fullpath_line_edit = QLineEdit(text=self.model.output_gtfs_zip_fullpath())
        self.output_gtfs_zip_fullpath_line_edit.setReadOnly(True)

        # Overwrite output GTFS
        self.overwrite_output_gtfs_check_box = QCheckBox()
        self.overwrite_output_gtfs_check_box.setChecked(False)

        # Filter type
        self.filter_type_select = QComboBox()
        self.filter_type_select.addItem("routeId", FilterType.ROUTE_ID)
        self.filter_type_select.addItem("tripId", FilterType.TRIP_ID)
        self.filter_type_select.setDisabled(True)

        # Filter values
        self.filter_values_list = QListWidget()
        self.filter_values_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        # Delete filter values
        self.delete_filter_values_push_button = QPushButton(DELETE_FILTER_VALUES_LABEL)
        self.delete_filter_values_push_button.setDisabled(True)

        # Start filtering
        self.start_filtering_push_button = QPushButton(START_FILTERING_LABEL)

        # Signal handlers
        self.input_gtfs_zip_select_button.clicked.connect(self.on__select_input_gtfs_zip__clicked_handler)
        self.output_gtfs_zip_filename_line_edit.textChanged.connect(
            self.on__output_gtfs_zip_filename_line_edit__text_changed_handler)
        self.output_gtfs_zip_folder_select_button.clicked.connect(
            self.on__select_output_gtfs_zip_folder__clicked_handler)
        self.filter_type_select.currentIndexChanged.connect(self.on__filter_type_select__current_index_changed_handler)
        self.delete_filter_values_push_button.clicked.connect(self.on__delete_filter_values_push_button__clicked_handler)
        self.start_filtering_push_button.clicked.connect(self.on__start_filtering_push_button__clicked_handler)

        # Add widgets to main_layout
        main_layout.addRow(SELECT_INPUT_GTFS_LABEL, self.input_gtfs_zip_select_button)
        main_layout.addRow(INPUT_GTFS_LABEL, self.input_gtfs_zip_selected_file_line_edit)
        main_layout.addRow(OUTPUT_GTFS_FILENAME_LABEL, self.output_gtfs_zip_filename_line_edit)
        main_layout.addRow(OUTPUT_GTFS_FOLDER_LABEL, self.output_gtfs_zip_folder_select_button)
        main_layout.addRow(OUTPUT_GTFS_FULLPATH_LABEL, self.output_gtfs_zip_fullpath_line_edit)
        main_layout.addRow(OVERWRITE_OUTPUT_GTFS_LABEL, self.overwrite_output_gtfs_check_box)
        main_layout.addRow(FILTER_TYPE_LABEL, self.filter_type_select)
        main_layout.addRow(FILTER_VALUES_LABEL, self.filter_values_list)
        main_layout.addRow(self.delete_filter_values_push_button)
        main_layout.addWidget(self.start_filtering_push_button)

        # Add main_layout to main_widget
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def _disable_all_inputs(self, disable: bool):
        self.input_gtfs_zip_select_button.setDisabled(disable)
        self.output_gtfs_zip_filename_line_edit.setDisabled(disable)
        self.output_gtfs_zip_folder_select_button.setDisabled(disable)
        self.overwrite_output_gtfs_check_box.setDisabled(disable)
        self.filter_type_select.setDisabled(disable)
        self.filter_values_list.setDisabled(disable)
        self.delete_filter_values_push_button.setDisabled(disable)
        self.start_filtering_push_button.setDisabled(disable)

    def _get_filter_values(self) -> List[str]:
        return [self.filter_values_list.item(i).text() for i in range(self.filter_values_list.count())]

    def _get_filter_type(self) -> FilterType:
        return self.filter_type_select.currentData()

    def _is_overwrite_output_gtfs(self) -> bool:
        return self.overwrite_output_gtfs_check_box.checkState() == Qt.CheckState.Checked

    def _retrieve_route_ids_and_trip_ids_from_input_gtfs(self):
        try:
            input_gtfs_zip = ZipFile(self.model.input_gtfs_zip)
            routes_bytes = input_gtfs_zip.read("routes.txt")
            trips_bytes = input_gtfs_zip.read("trips.txt")
            routes_str = StringIO(routes_bytes.decode("UTF-8"))
            trips_str = StringIO(trips_bytes.decode("UTF-8"))
            routes = read_csv(routes_str)
            trips = read_csv(trips_str)
        except Exception:
            open_error_message_box(ERROR_READING_INPUT_GTFS)
        self.model.route_ids_from_input_gtfs = routes['route_id'].tolist()
        self.model.trip_ids_from_input_gtfs = trips['trip_id'].tolist()
        self.model.route_ids_from_input_gtfs.sort()
        self.model.trip_ids_from_input_gtfs.sort()
        pass

    def _update_filter_values(self):
        self.filter_values_list.clear()
        if self._get_filter_type() == FilterType.ROUTE_ID:
            self.filter_values_list.addItems(self.model.route_ids_from_input_gtfs)
        elif self._get_filter_type() == FilterType.TRIP_ID:
            self.filter_values_list.addItems(self.model.trip_ids_from_input_gtfs)

    def on__select_input_gtfs_zip__clicked_handler(self):
        input_gtfs_zip, _ = QFileDialog.getOpenFileName(self, caption=INPUT_GTFS_SELECT_CAPTION_LABEL, directory=".",
                                                        filter=INPUT_GTFS_SELECT_FILTER_LABEL)
        if input_gtfs_zip:
            self.model.input_gtfs_zip = input_gtfs_zip
            self.input_gtfs_zip_selected_file_line_edit.setText(self.model.input_gtfs_zip)
            self._retrieve_route_ids_and_trip_ids_from_input_gtfs()
            self._update_filter_values()
            self.filter_type_select.setEnabled(True)
            self.delete_filter_values_push_button.setEnabled(True)

    def on__select_output_gtfs_zip_folder__clicked_handler(self):
        self.model.output_gtfs_zip_folder = QFileDialog.getExistingDirectory(self,
                                                                             OUTPUT_GTFS_FOLDER_SELECT_CAPTION_LABEL)
        self.output_gtfs_zip_folder_line_edit.setText(self.model.output_gtfs_zip_folder)
        self.output_gtfs_zip_fullpath_line_edit.setText(self.model.output_gtfs_zip_fullpath())

    def on__output_gtfs_zip_filename_line_edit__text_changed_handler(self, text: str):
        self.model.output_gtfs_zip_filename = text
        self.output_gtfs_zip_fullpath_line_edit.setText(self.model.output_gtfs_zip_fullpath())

    def on__filter_type_select__current_index_changed_handler(self, index: int):
        self._update_filter_values()

    def on__start_filtering_push_button__clicked_handler(self):
        if not self.model.input_gtfs_zip:
            open_warning_message_box(WARNING_INPUT_GTFS_NOT_SELECTED)
            return
        filter_values = self._get_filter_values()
        if not filter_values:
            open_warning_message_box(WARNING_NO_FILTER_VALUES)
            return
        self._disable_all_inputs(True)
        try:
            perform_filter(self.model.input_gtfs_zip, self.model.output_gtfs_zip_fullpath(), self._get_filter_type(),
                           filter_values, self._is_overwrite_output_gtfs())
            open_success_message_box(FILTERING_IS_SUCCESSFUL)
        except Exception as e:
            open_error_message_box(str(e))
        self._disable_all_inputs(False)

    def on__delete_filter_values_push_button__clicked_handler(self):
        if not self.filter_values_list.selectedItems():
            return
        for item in self.filter_values_list.selectedItems():
            self.filter_values_list.takeItem(self.filter_values_list.row(item))


if __name__ == '__main__':
    app = QApplication(argv)
    window = MainWindow()
    window.show()
    app.exec()
