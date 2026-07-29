import sys
import random
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QLineEdit, QAction,
    QDockWidget, QWidget, QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout, QLabel
)
from PyQt5.QtWebEngineWidgets import QWebEngineView

# ========== Запрет на создание новых окон ==========
class SingleWindowWebView(QWebEngineView):
    def createWindow(self, _type):
        # Возвращаем себя, чтобы всё открывалось в этом же виджете
        return self

# ========== Панель помощника Акакия ==========
class AkakyPanel(QWidget):
    def __init__(self, browser_ref):
        super().__init__()
        self.browser_ref = browser_ref  # ссылка на главное окно браузера
        self.last_query = ""

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Заголовок
        title = QLabel("🧔 Акакий-помощник")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(title)

        # Окно чата
        self.chat_view = QTextBrowser()
        self.chat_view.setReadOnly(True)
        self.chat_view.setOpenExternalLinks(False)
        layout.addWidget(self.chat_view)

        # Поле ввода и кнопки
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Спроси Акакия...")
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        send_btn = QPushButton("➤")
        send_btn.setFixedWidth(40)
        send_btn.clicked.connect(self.send_message)
        send_btn.setStyleSheet("QPushButton { font-size: 18px; }")
        input_layout.addWidget(send_btn)

        layout.addLayout(input_layout)

        search_btn = QPushButton("🔍 Искать этот запрос в Google")
        search_btn.clicked.connect(self.search_last_query)
        layout.addWidget(search_btn)

        # Приветственное сообщение
        self.add_akaky_message("Привет! Я Акакий. Могу подсказать, как работать с браузером, или помочь найти что-нибудь. Просто напиши мне.")

    def add_user_message(self, text):
        self.chat_view.append(f"<b style='color:#2a5db0'>Вы:</b> {text}")

    def add_akaky_message(self, text):
        self.chat_view.append(f"<b style='color:#b34141'>Акакий:</b> {text}")

    def send_message(self):
        text = self.input_field.text().strip()
        if not text:
            return
        self.last_query = text
        self.add_user_message(text)
        self.input_field.clear()

        # Генерируем ответ Акакия
        response = self.generate_akaky_response(text)
        self.add_akaky_message(response)

    def generate_akaky_response(self, text):
        """Простая логика ответов помощника на ключевые слова."""
        t = text.lower()
        if any(word in t for word in ["привет", "здравствуй", "хай"]):
            return random.choice([
                "Привет! Чем могу помочь?",
                "Здравствуй! Хочешь найти что-то в интернете?",
                "Привет-привет! Я тут, чтобы помогать."
            ])
        if "как дела" in t:
            return "У меня всё отлично, я же программа! А у тебя как?"
        if "что ты умеешь" in t or "что умеешь" in t:
            return ("Я могу подсказывать, как пользоваться браузером, "
                    "а также помочь с поиском. Напиши запрос, и я предложу найти его в Google.")
        if "спасибо" in t:
            return random.choice(["Пожалуйста!", "Всегда рад помочь.", "Обращайся ещё!"])
        if "пока" in t or "до свидания" in t:
            return "До встречи! Если что, я здесь."

        # Иначе предложение поискать
        return (f'Я не совсем понял, но могу помочь найти " {text} " в интернете. '
                f'Нажми кнопку ниже, и я перенесу запрос в адресную строку.')

    def search_last_query(self):
        """Переносит последний запрос в адресную строку браузера и запускает поиск."""
        if self.last_query:
            self.browser_ref.url_bar.setText(self.last_query)
            self.browser_ref.navigate_to_url()

# ========== Основное окно браузера ==========
class MinimalBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Акакий-Браузер")
        self.setGeometry(100, 100, 1200, 800)

        # Главный веб-виджет с запретом новых окон
        self.browser = SingleWindowWebView()
        self.browser.setUrl(QUrl("https://www.google.com"))
        self.setCentralWidget(self.browser)

        # Панель навигации
        nav_bar = QToolBar("Навигация")
        nav_bar.setMovable(False)
        nav_bar.setIconSize(nav_bar.iconSize() * 0.8)
        self.addToolBar(Qt.TopToolBarArea, nav_bar)

        # Кнопка "Назад"
        back_action = QAction("◀", self)
        back_action.setToolTip("Назад")
        back_action.triggered.connect(self.browser.back)
        nav_bar.addAction(back_action)

        # Кнопка "Вперёд"
        fwd_action = QAction("▶", self)
        fwd_action.setToolTip("Вперёд")
        fwd_action.triggered.connect(self.browser.forward)
        nav_bar.addAction(fwd_action)

        # Кнопка "Обновить"
        reload_action = QAction("⟳", self)
        reload_action.setToolTip("Обновить страницу")
        reload_action.triggered.connect(self.browser.reload)
        nav_bar.addAction(reload_action)

        # Кнопка "Домой" (Google)
        home_action = QAction("⌂", self)
        home_action.setToolTip("Домашняя страница")
        home_action.triggered.connect(lambda: self.browser.setUrl(QUrl("https://www.google.com")))
        nav_bar.addAction(home_action)

        # Адресная строка
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Введите адрес или поисковый запрос...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setMinimumWidth(300)
        nav_bar.addWidget(self.url_bar)

        # Кнопка вызова панели Акакия
        akaky_action = QAction("🧔", self)
        akaky_action.setToolTip("Показать/скрыть помощника Акакия")
        akaky_action.setCheckable(True)
        akaky_action.toggled.connect(self.toggle_akaky_panel)
        nav_bar.addAction(akaky_action)

        # Боковая панель с Акакием
        self.akaky_dock = QDockWidget("Акакий", self)
        self.akaky_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.akaky_panel = AkakyPanel(self)  # передаём ссылку на браузер
        self.akaky_dock.setWidget(self.akaky_panel)
        self.akaky_dock.setMinimumWidth(320)
        self.addDockWidget(Qt.RightDockWidgetArea, self.akaky_dock)
        self.akaky_dock.hide()  # по умолчанию скрыта

        # Связь: обновление адресной строки при смене страницы
        self.browser.urlChanged.connect(self.update_url_bar)
        self.browser.titleChanged.connect(self.update_title)

    def navigate_to_url(self):
        """Превращает ввод в URL или поисковый запрос Google."""
        text = self.url_bar.text().strip()
        if not text:
            return

        # Если это явный URL (содержит точку или начинается с http/ftp), открываем как есть
        if '.' in text or text.startswith(('http://', 'https://', 'ftp://')):
            if not text.startswith(('http://', 'https://', 'ftp://')):
                text = 'https://' + text
            self.browser.setUrl(QUrl(text))
        else:
            # Иначе считаем поисковым запросом и ищем в Google
            query = text.replace(' ', '+')
            search_url = 'https://www.google.com/search?q=' + query
            self.browser.setUrl(QUrl(search_url))

    def update_url_bar(self, url):
        """Отображает текущий URL в адресной строке."""
        self.url_bar.setText(url.toString())
        self.url_bar.setCursorPosition(0)

    def update_title(self, title):
        """Динамический заголовок окна."""
        self.setWindowTitle(f"{title} — Акакий-Браузер" if title else "Акакий-Браузер")

    def toggle_akaky_panel(self, visible):
        """Показать/скрыть панель помощника."""
        self.akaky_dock.setVisible(visible)

# ========== Стилизация (QSS) ==========
STYLE_SHEET = """
QMainWindow {
    background-color: #f5f5f5;
}
QToolBar {
    background: #ffffff;
    border-bottom: 1px solid #d0d0d0;
    spacing: 4px;
    padding: 4px;
}
QToolBar QToolButton {
    background: transparent;
    border: none;
    font-size: 18px;
    color: #333;
    padding: 4px 8px;
    border-radius: 4px;
}
QToolBar QToolButton:hover {
    background: #e0e0e0;
}
QToolBar QToolButton:checked {
    background: #b0d0ff;
}
QLineEdit {
    border: 1px solid #c0c0c0;
    border-radius: 12px;
    padding: 6px 12px;
    font-size: 14px;
    background: #ffffff;
    min-width: 200px;
}
QLineEdit:focus {
    border-color: #4a90d9;
}
QTextBrowser {
    border: 1px solid #ccc;
    border-radius: 8px;
    background: #fafafa;
    font-size: 13px;
    padding: 6px;
}
QPushButton {
    border: 1px solid #aaa;
    border-radius: 8px;
    padding: 6px 16px;
    background: #f0f0f0;
    font-size: 13px;
}
QPushButton:hover {
    background: #e0e0e0;
}
QDockWidget {
    font-weight: bold;
    background: #ffffff;
    border: 1px solid #ccc;
}
"""

# ========== Запуск ==========
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_SHEET)
    window = MinimalBrowser()
    window.show()
    sys.exit(app.exec_())
