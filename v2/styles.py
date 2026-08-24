APP_STYLE = """
QMainWindow { background-color: #F5F5F5; }
QWidget { background-color: #F5F5F5; }
QLabel { color: #222222; }
QLabel#goodStatus { color: #2E7D32; font-weight: bold; }
QLabel#simulationStatus { color: #1565C0; font-weight: bold; }

QPushButton, QToolButton {
    background-color: white;
    color: #222222;
    border: 2px solid #444444;
    border-radius: 12px;
    padding: 10px;
}
QPushButton:hover, QToolButton:hover { background-color: #E8E8E8; }
QPushButton:pressed, QToolButton:pressed { background-color: #D0D0D0; }

QPushButton#startButton {
    background-color: #2E7D32;
    color: white;
    border: none;
    border-radius: 18px;
}
QPushButton#startButton:hover { background-color: #388E3C; }
QPushButton#startButton:pressed { background-color: #1B5E20; }

QPushButton#teleopButton {
    background-color: #1565C0;
    color: white;
    border: none;
    border-radius: 18px;
}
QPushButton#teleopButton:hover { background-color: #1976D2; }
QPushButton#teleopButton:pressed { background-color: #0D47A1; }

QPushButton#statusButton {
    background-color: #424242;
    color: white;
    border: none;
    border-radius: 18px;
}
QPushButton#statusButton:hover { background-color: #616161; }
QPushButton#statusButton:pressed { background-color: #212121; }

QToolButton#artButton {
    background-color: white;
    color: #222222;
    border: 2px solid #BDBDBD;
    border-radius: 18px;
    padding: 15px;
}
QToolButton#artButton:hover {
    background-color: #E8F5E9;
    border: 3px solid #2E7D32;
}
QToolButton#artButton:pressed { background-color: #C8E6C9; }

QPushButton#cancelButton { background-color: #C62828; color: white; }
QPushButton#cancelButton:hover { background-color: #D32F2F; }

QPushButton#homeButton { background-color: #1565C0; color: white; }
QPushButton#homeButton:hover { background-color: #1976D2; }

QPushButton#backButton { background-color: #333333; color: white; }
QPushButton#backButton:hover { background-color: #555555; }
"""
