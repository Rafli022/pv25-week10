import sys
import sqlite3
import csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QLabel, QHeaderView
)
from PyQt5.QtCore import Qt

class BookManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manajemen Data Buku")
        self.resize(800, 500)
        self.conn = sqlite3.connect("books.db")
        self.create_table()
        self.init_ui()
        self.load_data()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT,
                            author TEXT,
                            year INTEGER)''')
        self.conn.commit()

    def init_ui(self):
        layout = QVBoxLayout()

        # Input Fields
        form_layout = QHBoxLayout()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Judul Buku")
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Penulis")
        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("Tahun Terbit")
        self.save_button = QPushButton("Simpan")
        self.save_button.clicked.connect(self.save_data)
        form_layout.addWidget(self.title_input)
        form_layout.addWidget(self.author_input)
        form_layout.addWidget(self.year_input)
        form_layout.addWidget(self.save_button)
        layout.addLayout(form_layout)

        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari judul buku...")
        self.search_input.textChanged.connect(self.load_data)
        layout.addWidget(self.search_input)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Judul", "Penulis", "Tahun"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.cellChanged.connect(self.update_data)
        layout.addWidget(self.table)

        # Buttons
        button_layout = QHBoxLayout()
        self.delete_button = QPushButton("Hapus Data Terpilih")
        self.delete_button.clicked.connect(self.delete_data)
        self.export_button = QPushButton("Export ke CSV")
        self.export_button.clicked.connect(self.export_csv)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.export_button)
        layout.addLayout(button_layout)

        # Footer
        footer = QLabel("Dibuat oleh: Rafli (F1D022022)")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)

        self.setLayout(layout)

    def save_data(self):
        title = self.title_input.text()
        author = self.author_input.text()
        year = self.year_input.text()

        if not title or not author or not year:
            QMessageBox.warning(self, "Peringatan", "Semua field harus diisi.")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO books (title, author, year) VALUES (?, ?, ?)",
                           (title, author, int(year)))
            self.conn.commit()
            self.title_input.clear()
            self.author_input.clear()
            self.year_input.clear()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def load_data(self):
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        keyword = self.search_input.text().lower()
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM books")
        for row_index, row_data in enumerate(cursor.fetchall()):
            if keyword in row_data[1].lower():
                self.table.insertRow(row_index)
                for col_index, col_data in enumerate(row_data):
                    self.table.setItem(row_index, col_index, QTableWidgetItem(str(col_data)))
        self.table.blockSignals(False)

    def update_data(self, row, column):
        try:
            id_item = self.table.item(row, 0)
            new_value = self.table.item(row, column).text()
            column_name = ["id", "title", "author", "year"][column]
            cursor = self.conn.cursor()
            cursor.execute(f"UPDATE books SET {column_name} = ? WHERE id = ?", (new_value, id_item.text()))
            self.conn.commit()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_data(self):
        selected = self.table.currentRow()
        if selected >= 0:
            id_item = self.table.item(selected, 0)
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM books WHERE id = ?", (id_item.text(),))
            self.conn.commit()
            self.load_data()

    def export_csv(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM books")
            data = cursor.fetchall()
            with open("data_buku.csv", "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Judul", "Penulis", "Tahun"])
                writer.writerows(data)
            QMessageBox.information(self, "Berhasil", "Data berhasil diekspor ke data_buku.csv")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BookManager()
    window.show()
    sys.exit(app.exec_())
