import sys
import sqlite3
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QMessageBox,
    QDialog,
    QListWidget,
)


class Database:
    def __init__(self, db_name="zag.db"):
        # Инициализация соединения с базой данных и создание таблицы(если её нет)
        self.connection = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        # Создание таблицы 'info', если её не существует
        with self.connection:
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    text TEXT NOT NULL
                )
            ''')

    def add_note(self, title, text):
        # Добавление новой заметки в базу данных
        with self.connection:
            self.connection.execute('INSERT INTO info (title, text) VALUES (?, ?)', (title, text))

    def get_notes(self):
        # Получение всех заметок из базы данных
        with self.connection:
            cursor = self.connection.execute('SELECT id, title, text FROM info')
            return cursor.fetchall()

    def delete_note(self, note_id):
        # Удаление заметки по её идентификатору
        with self.connection:
            self.connection.execute('DELETE FROM info WHERE id = ?', (note_id,))

    def update_note(self, note_id, title, text):
        # Обновление существующей заметки по её идентификатору
        with self.connection:
            self.connection.execute('UPDATE info SET title = ?, text = ? WHERE id = ?', (title, text, note_id))


class NoteWindow(QDialog):
    def __init__(self, title="", text="", note_id=None, onsave=None):
        # Конструктор окна заметки, принимает заголовок, текст, айди заметки и функцию для сохранения
        super().__init__()
        self.setWindowTitle("Заметка")
        self.onsave = onsave
        self.note_id = note_id

        # Поля для ввода заголовка и текста заметки
        self.title_edit = QTextEdit()
        self.title_edit.setText(title)
        self.text_edit = QTextEdit()
        self.text_edit.setText(text)

        # Кнопка для сохранения заметки
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_note)

        # Кнопка для удаления заметки
        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_note)

        # Кнопка для сохранения заметки в файл
        self.save_to_file_button = QPushButton("Сохранить в файл")
        self.save_to_file_button.clicked.connect(self.save_note_to_file)

        # Основа интерфейса(поле для заметок)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Заголовок:"))
        layout.addWidget(self.title_edit)
        layout.addWidget(QLabel("Текст:"))
        layout.addWidget(self.text_edit)
        layout.addWidget(self.save_button)
        layout.addWidget(self.save_to_file_button)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

    def save_note(self):
        # Сохранение заметки, проверка на пустые поля
        title = self.title_edit.toPlainText().strip()
        text = self.text_edit.toPlainText().strip()

        if not title or not text:
            QMessageBox.warning(self, "Ошибка", "Заполните заголовок и текст!")
            return

        # Вызов функции сохранения (если задана) и закрытие окна
        if self.onsave:
            self.onsave(title, text, self.note_id)
        self.accept()

    def save_note_to_file(self):
        # Сохранение заметки в текстовый файл
        title = self.title_edit.toPlainText().strip()
        text = self.text_edit.toPlainText().strip()

        if not title or not text:
            QMessageBox.warning(self, "Ошибка", "Заполните заголовок и текст для сохранения в файл!")
            return

        try:
            # Запись содержимого заметки в файл
            with open(f"{title}.txt", "w", encoding="utf-8") as file:
                file.write(f"{title}\n{text}")
            QMessageBox.information(self, "Успех", f"Заметка успешно сохранена в '{title}.txt'.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить заметку в файл: {e}")

    def delete_note(self):
        # Подтверждение удаления заметки
        reply = QMessageBox.question(self, "Удаление", "Удалить заметку?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if self.onsave:
                self.onsave(None, None, self.note_id, delete=True)
            self.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        # основа для основного окна приложения
        super().__init__()
        self.setWindowTitle("Проект")
        self.db = Database()
        self.layout = QVBoxLayout()

        # Список заметок
        self.notes_list = QListWidget()
        self.notes_list.itemClicked.connect(self.open_selected_note)

        self.layout.addWidget(QLabel("Список заметок:"))
        self.layout.addWidget(self.notes_list)

        # Кнопка создания новой заметки
        self.create_note_button = QPushButton("Создать новую заметку")
        self.create_note_button.clicked.connect(self.create_new_note)
        self.layout.addWidget(self.create_note_button)

        # Контейнер для размещения элементов интерфейса
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.display_notes()  # Отображение заметок в списке

    def display_notes(self):
        # Очистка списка и отображение заметок
        self.notes_list.clear()

        for note in self.db.get_notes():
            note_id, title, text = note
            self.notes_list.addItem(title)  # Добавление заголовков заметок в список

    def open_selected_note(self, item):
        # Открытие окна редактирования выбранной заметки
        title = item.text()
        for note in self.db.get_notes():
            if note[1] == title:
                self.open_note_window(note)
                break

    def create_new_note(self):
        # Создание новой заметки
        note_window = NoteWindow(onsave=self.save_note)
        note_window.exec()

    def open_note_window(self, note):
        # Открытие окна для редактирования существующей заметки
        note_window = NoteWindow(title=note[1], text=note[2], note_id=note[0], onsave=self.save_note)
        note_window.exec()

    def save_note(self, title, text, note_id=None, delete=False):
        # Сохранение или удаление заметки в зависимости от параметров
        if delete:
            self.db.delete_note(note_id)
            QMessageBox.information(self, "Успех", "Заметка удалена.")
        else:
            if note_id is not None:
                self.db.update_note(note_id, title, text)
                QMessageBox.information(self, "Успех", f"Заметка '{title}' обновлена.")
            else:
                self.db.add_note(title, text)
                QMessageBox.information(self, "Успех", f"Добавлена новая заметка: '{title}'.")
        self.update_note_display()  # Обновление списка заметок

    def update_note_display(self):
        # Обновление отображения заметок в списке
        self.display_notes()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
