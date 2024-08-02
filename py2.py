import sys
import string
import random
import pyperclip
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QCheckBox, QPushButton,
    QVBoxLayout, QHBoxLayout, QMenuBar, QMenu, QAction, QProgressBar,
    QComboBox, QTextEdit, QFileDialog, QMessageBox, QSlider  # Aggiunta di QSlider
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QPropertyAnimation


class AnimatedProgressBar(QProgressBar):
    def __init__(self):
        super().__init__()
        self.setMaximum(100)
        self.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                width: 20px;
                margin: 1px;
            }
        """)

    def animate_progress(self, value):
        self.setValue(0)
        self.clearFocus()
        self.anim = QPropertyAnimation(self, b"value")
        self.anim.setDuration(1000)
        self.anim.setStartValue(self.value())
        self.anim.setEndValue(value)
        self.anim.start()


class PasswordGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Generatore di Password')
        self.setGeometry(100, 100, 600, 500)

        menubar = QMenuBar(self)
        file_menu = QMenu("File", self)
        help_menu = QMenu("Help", self)
        theme_menu = QMenu("Theme", self)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        save_action = QAction("Save Password", self)
        save_action.triggered.connect(self.save_password)
        file_menu.addAction(save_action)

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        light_theme_action = QAction("Light Theme", self)
        light_theme_action.triggered.connect(self.light_theme)
        theme_menu.addAction(light_theme_action)

        dark_theme_action = QAction("Dark Theme", self)
        dark_theme_action.triggered.connect(self.dark_theme)
        theme_menu.addAction(dark_theme_action)

        menubar.addMenu(file_menu)
        menubar.addMenu(theme_menu)
        menubar.addMenu(help_menu)

        self.label_length = QLabel('Lunghezza della password:', self)
        self.label_length.setFont(QFont('Helvetica', 12))

        self.slider_length = QSlider(Qt.Horizontal, self)  # Corretta l'importazione di QSlider
        self.slider_length.setMinimum(1)
        self.slider_length.setMaximum(50)
        self.slider_length.setValue(12)
        self.slider_length.setTickInterval(1)
        self.slider_length.setTickPosition(QSlider.TicksBelow)
        self.slider_length.valueChanged.connect(self.update_length_label)

        self.length_display = QLabel('12', self)
        self.length_display.setFont(QFont('Helvetica', 12))

        self.check_number = QCheckBox('Includi numeri', self)
        self.check_number.setFont(QFont('Helvetica', 12))
        self.check_symbol = QCheckBox('Includi simboli', self)
        self.check_symbol.setFont(QFont('Helvetica', 12))

        self.combo_case = QComboBox(self)
        self.combo_case.addItem("Case sensitive")
        self.combo_case.addItem("Uppercase only")
        self.combo_case.addItem("Lowercase only")
        self.combo_case.setFont(QFont('Helvetica', 12))

        self.button_generate = QPushButton('🔒 Genera Password', self)
        self.button_generate.setFont(QFont('Helvetica', 12))
        self.button_generate.clicked.connect(self.on_generate)
        self.button_generate.setToolTip("Clicca per generare una nuova password")

        self.entry_password = QLineEdit(self)
        self.entry_password.setFont(QFont('Helvetica', 12))
        self.entry_password.setReadOnly(True)

        self.button_copy = QPushButton('📋 Copia Password', self)
        self.button_copy.setFont(QFont('Helvetica', 12))
        self.button_copy.clicked.connect(self.copy_to_clipboard)
        self.button_copy.setToolTip("Clicca per copiare la password negli appunti")

        self.strength_bar = AnimatedProgressBar()

        self.saved_passwords = QTextEdit(self)
        self.saved_passwords.setFont(QFont('Helvetica', 12))
        self.saved_passwords.setReadOnly(True)

        vbox = QVBoxLayout()
        vbox.addWidget(menubar)

        hbox_length = QHBoxLayout()
        hbox_length.addWidget(self.label_length)
        hbox_length.addWidget(self.length_display)
        vbox.addLayout(hbox_length)

        vbox.addWidget(self.slider_length)
        vbox.addWidget(self.check_number)
        vbox.addWidget(self.check_symbol)
        vbox.addWidget(self.combo_case)
        vbox.addWidget(self.button_generate)
        vbox.addWidget(self.entry_password)
        vbox.addWidget(self.button_copy)
        vbox.addWidget(self.strength_bar)
        vbox.addWidget(QLabel('Password salvate:', self))
        vbox.addWidget(self.saved_passwords)

        self.setLayout(vbox)
        self.dark_theme()

    def generapassword(self, length, include_numbers, include_symbols, case_option):
        lista_caratteri = []
        if case_option == "Case sensitive" or case_option == "Uppercase only":
            lista_caratteri += string.ascii_uppercase
        if case_option == "Case sensitive" or case_option == "Lowercase only":
            lista_caratteri += string.ascii_lowercase
        if include_numbers:
            lista_caratteri += string.digits
        if include_symbols:
            lista_caratteri += string.punctuation

        if not lista_caratteri:
            raise ValueError("Deve essere selezionata almeno una categoria di caratteri")

        password = ''.join(random.choice(lista_caratteri) for _ in range(length))
        return password

    def on_generate(self):
        length = self.slider_length.value()
        include_numbers = self.check_number.isChecked()
        include_symbols = self.check_symbol.isChecked()
        case_option = self.combo_case.currentText()

        try:
            password = self.generapassword(length, include_numbers, include_symbols, case_option)
            self.entry_password.setText(password)
            self.update_strength_bar(password)
        except ValueError as e:
            self.strength_bar.setFormat(str(e))

    def copy_to_clipboard(self):
        password = self.entry_password.text()
        pyperclip.copy(password)
        QMessageBox.information(self, "Copiato", "La password è stata copiata negli appunti.")

    def is_password_secure(self, password):
        return (
                len(password) >= 8 and
                any(char.isdigit() for char in password) and
                any(char in string.punctuation for char in password) and
                any(char.isupper() for char in password) and
                any(char.islower() for char in password)
        )

    def update_length_label(self):
        self.length_display.setText(str(self.slider_length.value()))

    def update_strength_bar(self, password):
        score = 0
        if len(password) >= 8:
            score += 20
        if any(char.isdigit() for char in password):
            score += 20
        if any(char in string.punctuation for char in password):
            score += 20
        if any(char.isupper() for char in password):
            score += 20
        if any(char.islower() for char in password):
            score += 20
        self.strength_bar.animate_progress(score)
        if self.is_password_secure(password):
            self.strength_bar.setFormat("La password generata è sicura.")
        else:
            self.strength_bar.setFormat("La password generata non è sufficientemente sicura.")

    def save_password(self):
        password = self.entry_password.text()
        if password:
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Password", "", "Text Files (*.txt);;All Files (*)")
            if file_name:
                with open(file_name, 'w') as file:
                    file.write(password)
                self.saved_passwords.append(password)
                QMessageBox.information(self, "Salvato", "La password è stata salvata.")
        else:
            QMessageBox.warning(self, "Errore", "Nessuna password da salvare.")

    def show_about(self):
        QMessageBox.about(self, "About", "Generatore di Password v2.0\nCreato da OpenAI")

    def light_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;  /* Colore di sfondo principale */
                color: #000000;  /* Colore del testo */
            }
            QMenuBar::item:selected {
                background-color: #ffffff;  /* Colore di sfondo al passaggio del mouse */
                color: #000000;  /* Colore del testo al passaggio del mouse */
            }
            QMenu::item:selected {
                background-color: #ffffff;  /* Colore di sfondo al passaggio del mouse */
                color: #000000;  /* Colore del testo al passaggio del mouse */
            }
            QPushButton {
                background-color: #3498db;  /* Colore di sfondo pulsante */
                color: white;  /* Colore del testo */
                border: 2px solid #2980b9;  /* Bordo del pulsante */
                border-radius: 5px;  /* Bordo arrotondato del pulsante */
                padding: 10px;  /* Spaziatura interna del pulsante */
                font-size: 16px;  /* Dimensione del font del pulsante */
            }
            QPushButton:hover {
                background-color: #2980b9;  /* Colore di sfondo al passaggio del mouse */
                border: 2px solid #3498db;  /* Bordo del pulsante al passaggio del mouse */
            }
            QLineEdit, QTextEdit {
                background-color: #ffffff;  /* Colore di sfondo caselle di testo */
                border: 1px solid #000000;  /* Bordo delle caselle di testo */
                color: #000000;  /* Colore del testo */
            }
            QSlider::groove:horizontal {
                border: 1px solid #bbb;  /* Bordo dello slider */
                background: #f0f0f0;  /* Colore di sfondo dello slider */
                height: 10px;  /* Altezza dello slider */
                border-radius: 4px;  /* Bordo arrotondato dello slider */
            }
            QSlider::handle:horizontal {
                background: #ffffff;  /* Colore di sfondo del manico dello slider */
                border: 1px solid #000000;  /* Bordo del manico dello slider */
                width: 20px;  /* Larghezza del manico dello slider */
                margin: -5px 0;  /* Margine del manico dello slider */
                border-radius: 4px;  /* Bordo arrotondato del manico dello slider */
            }
        """)

    def dark_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;  /* Colore di sfondo principale */
                color: #ecf0f1;  /* Colore del testo */
            }
            QMenuBar::item:selected {
                background-color: #34495e;  /* Colore di sfondo al passaggio del mouse */
                color: #ecf0f1;  /* Colore del testo al passaggio del mouse */
            }
            QMenu::item:selected {
                background-color: #34495e;  /* Colore di sfondo al passaggio del mouse */
                color: #ecf0f1;  /* Colore del testo al passaggio del mouse */
            }
            QPushButton {
                background-color: #3498db;  /* Colore di sfondo pulsante */
                color: white;  /* Colore del testo */
                border: 2px solid #2980b9;  /* Bordo del pulsante */
                border-radius: 5px;  /* Bordo arrotondato del pulsante */
                padding: 10px;  /* Spaziatura interna del pulsante */
                font-size: 16px;  /* Dimensione del font del pulsante */
            }
            QPushButton:hover {
                background-color: #2980b9;  /* Colore di sfondo al passaggio del mouse */
                border: 2px solid #3498db;  /* Bordo del pulsante al passaggio del mouse */
            }
            QLineEdit, QTextEdit {
                background-color: #34495e;  /* Colore di sfondo caselle di testo */
                border: 1px solid #ecf0f1;  /* Bordo delle caselle di testo */
                color: #ecf0f1;  /* Colore del testo */
            }
            QSlider::groove:horizontal {
                border: 1px solid #bbb;  /* Bordo dello slider */
                background: #2c3e50;  /* Colore di sfondo dello slider */
                height: 10px;  /* Altezza dello slider */
                border-radius: 4px;  /* Bordo arrotondato dello slider */
            }
            QSlider::handle:horizontal {
                background: #34495e;  /* Colore di sfondo del manico dello slider */
                border: 1px solid #ecf0f1;  /* Bordo del manico dello slider */
                width: 20px;  /* Larghezza del manico dello slider */
                margin: -5px 0;  /* Margine del manico dello slider */
                border-radius: 4px;  /* Bordo arrotondato del manico dello slider */
            }
        """)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PasswordGenerator()
    ex.show()
    sys.exit(app.exec_())
