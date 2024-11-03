import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QMessageBox,
    QGridLayout,
    QSizePolicy,
    QDialog,
)

class NoteWindow(QDialog):
    def __init__(self, title="", text="", on_save=None):
        super().__init__()
        self.setWindowTitle("Заметка")
        self.on_save = on_save

        # Поля для редактирования заголовка и текста заметки
        self.title_edit = QTextEdit()
        self.title_edit.setText(title)
        self.text_edit = QTextEdit()
        self.text_edit.setText(text)

        # Кнопки для сохранения и удаления заметки
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_note)

        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_note)

        # Установка макета
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Заголовок:"))
        layout.addWidget(self.title_edit)
        layout.addWidget(QLabel("Текст:"))
        layout.addWidget(self.text_edit)
        layout.addWidget(self.save_button)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

    def save_note(self):
        title = self.title_edit.toPlainText().strip()  # Получаем заголовок
        text = self.text_edit.toPlainText()  # Получаем текст заметки
        if self.on_save:
            self.on_save(title, text)  # Вызов функции сохранения из MainWindow
        self.accept()  # Закрытие окна заметки

    def delete_note(self):
        reply = QMessageBox.question(
            self, "Удаление", "Вы точно хотите удалить заметку?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self.on_save:
                self.on_save(self.title_edit.toPlainText(), None, delete=True)  # Удаление
            self.accept()  # Закрытие окна заметки

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Проект")

        # Глобальный набор заметок
        self.notes = []

        self.layout = QGridLayout()
        self.display_notes()  # Отображение заметок

        self.create_note_button = QPushButton("Создать новую заметку")
        self.create_note_button.clicked.connect(self.create_new_note)

        self.layout.addWidget(self.create_note_button, 0, 0)  # Добавление кнопки в макет

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def display_notes(self):
        # Очистка старых кнопок перед обновлением
        while self.layout.count() > 1:  # Учтем кнопку создания заметки
            widget = self.layout.takeAt(1)  # Удаляем старые кнопки заметок
            if widget.widget():
                widget.widget().deleteLater()

        for i, note in enumerate(self.notes):
            button = QPushButton(note['title'])
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.clicked.connect(lambda _, n=note: self.open_note_window(n))
            self.layout.addWidget(button, i + 1, 0)  # Индекс увеличивается на 1 для кнопок заметок

    def create_new_note(self):
        note_window = NoteWindow(on_save=self.save_note)
        note_window.exec()  # Используем exec для открытия диалога модально

    def open_note_window(self, note):
        note_window = NoteWindow(title=note['title'], text=note['text'], on_save=self.save_note)
        note_window.exec()  # Используем exec для открытия диалога модально

    def save_note(self, title, text, delete=False):
        if delete:
            # Удаляем заметку
            self.notes = [note for note in self.notes if note['title'] != title]
            QMessageBox.information(self, "Успех", f"Заметка '{title}' успешно удалена.")  # Уведомление о удалении
        else:
            # Сохранение или обновление заметки
            if title and text:  # Проверка на пустые значения
                for note in self.notes:
                    if note['title'] == title:
                        note['text'] = text
                        QMessageBox.information(self, "Успех", f"Заметка '{title}' обновлена.")  # Уведомление об обновлении
                        break
                else:
                    self.notes.append({"title": title, "text": text})
                    QMessageBox.information(self, "Успех", f"Добавлена новая заметка: '{title}'.")  # Уведомление о добавлении

        # Обновление отображения заметок
        self.update_note_display()

    def update_note_display(self):
        # Обновляем отображение заметок
        self.display_notes()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
