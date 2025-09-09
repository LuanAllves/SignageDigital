from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QSpinBox, QDateEdit, QTimeEdit, QPushButton, 
                               QDialogButtonBox)
from PySide6.QtCore import QDate, QTime

class MediaEditDialog(QDialog):
    def __init__(self, media_type, duration_seconds, scheduled_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Mídia")
        self.setGeometry(200, 200, 400, 450)
        
        dialog_layout = QVBoxLayout(self)

        self.duration_layout = QHBoxLayout()
        self.duration_label = QLabel("<b>Duração (segundos):</b>")
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setMinimum(1)
        self.duration_spinbox.setMaximum(3600)
        self.duration_spinbox.setValue(duration_seconds)
        self.duration_layout.addWidget(self.duration_label)
        self.duration_layout.addWidget(self.duration_spinbox)
        self.duration_layout.addStretch()
        dialog_layout.addLayout(self.duration_layout)
        
        if media_type != "Imagem":
            self.duration_label.hide()
            self.duration_spinbox.hide()

        start_label = QLabel("<b>Agendamento de Início:</b>")
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setDisplayFormat("HH:mm")
        self.start_time_edit.setTime(QTime.currentTime())
        dialog_layout.addWidget(start_label)
        
        start_schedule_layout = QHBoxLayout()
        start_schedule_layout.addWidget(self.start_date_edit)
        start_schedule_layout.addWidget(self.start_time_edit)
        dialog_layout.addLayout(start_schedule_layout)
        
        end_label = QLabel("<b>Agendamento de Fim:</b>")
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setDisplayFormat("HH:mm")
        self.clear_end_button = QPushButton("Limpar Agendamento")
        
        dialog_layout.addWidget(end_label)
        end_schedule_layout = QHBoxLayout()
        end_schedule_layout.addWidget(self.end_date_edit)
        end_schedule_layout.addWidget(self.end_time_edit)
        end_schedule_layout.addWidget(self.clear_end_button)
        dialog_layout.addLayout(end_schedule_layout)
        
        self.clear_end_button.clicked.connect(self._clear_end_schedule)
        self.end_date_edit.dateChanged.connect(lambda: self._set_end_schedule_enabled(True))
        self.end_time_edit.timeChanged.connect(lambda: self._set_end_schedule_enabled(True))

        if scheduled_data.get('start_date'):
            start_date = QDate.fromString(scheduled_data['start_date'], "dd/MM/yyyy")
            start_time = QTime.fromString(scheduled_data['start_time'], "HH:mm")
            self.start_date_edit.setDate(start_date)
            self.start_time_edit.setTime(start_time)
            
        if scheduled_data.get('end_date'):
            end_date = QDate.fromString(scheduled_data['end_date'], "dd/MM/yyyy")
            end_time = QTime.fromString(scheduled_data['end_time'], "HH:mm")
            self.end_date_edit.setDate(end_date)
            self.end_time_edit.setTime(end_time)
        else:
            self._clear_end_schedule()

        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        dialog_layout.addWidget(button_box)

    def _set_end_schedule_enabled(self, enabled):
        self.end_date_edit.setEnabled(enabled)
        self.end_time_edit.setEnabled(enabled)

    def _clear_end_schedule(self):
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_time_edit.setTime(QTime(0, 0))
        self._set_end_schedule_enabled(False)

    def get_schedule_data(self):
        start_date = self.start_date_edit.date().toString("dd/MM/yyyy")
        start_time = self.start_time_edit.time().toString("HH:mm")
        
        end_date = None
        end_time = None
        if self.end_date_edit.isEnabled():
            end_date = self.end_date_edit.date().toString("dd/MM/yyyy")
            end_time = self.end_time_edit.time().toString("HH:mm")
        
        duration = self.duration_spinbox.value()
        
        return {
            "start_date": start_date,
            "start_time": start_time,
            "end_date": end_date,
            "end_time": end_time,
            "duration": duration
        }