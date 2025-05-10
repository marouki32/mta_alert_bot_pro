# gui/tabs/settings_tab.py

from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QPushButton,
    QSpinBox, QDoubleSpinBox, QMessageBox, QCheckBox, QApplication
)
import json, os

class SettingsTab(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        layout = QFormLayout()

        # RSI period
        self.rsi_input = QSpinBox()
        self.rsi_input.setRange(1, 100)
        self.rsi_input.setValue(self.config['indicators']['rsi'])
        layout.addRow("RSI period", self.rsi_input)

        # EMA spans
        self.ema_input = QLineEdit(",".join(str(x) for x in self.config['indicators']['ema']))
        layout.addRow("EMA spans (comma‑sep)", self.ema_input)

        # Bollinger window & std
        self.boll_window_input = QSpinBox();  self.boll_window_input.setRange(1,100)
        self.boll_window_input.setValue(self.config['indicators']['bollinger']['window'])
        layout.addRow("Bollinger window", self.boll_window_input)

        self.boll_std_input = QDoubleSpinBox(); self.boll_std_input.setRange(0.1,10.0)
        self.boll_std_input.setSingleStep(0.1)
        self.boll_std_input.setValue(self.config['indicators']['bollinger']['std'])
        layout.addRow("Bollinger std dev", self.boll_std_input)

        # Confidence threshold
        self.threshold_input = QDoubleSpinBox(); self.threshold_input.setRange(0.0,1.0)
        self.threshold_input.setSingleStep(0.01)
        self.threshold_input.setValue(self.config['alerts']['confidence_threshold'])
        layout.addRow("Confidence threshold", self.threshold_input)

        # ─── Dark Mode toggle ─────────────────────────────────────────
        self.dark_cb = QCheckBox("Dark Mode")
        # initial state based on whether a styleSheet is applied
        is_dark = bool(QApplication.instance().styleSheet().strip())
        self.dark_cb.setChecked(is_dark)
        self.dark_cb.toggled.connect(self.toggle_dark_mode)
        layout.addRow(self.dark_cb)
        # ───────────────────────────────────────────────────────────────

        # Save button
        self.save_button = QPushButton("Sauvegarder")
        self.save_button.clicked.connect(self.save_settings)
        layout.addRow(self.save_button)

        self.setLayout(layout)

    def toggle_dark_mode(self, checked: bool):
        """Active/désactive le QSS sombre sans redémarrer."""
        app = QApplication.instance()
        qss_path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), '..', '..', 'dark.qss')
        )
        if checked and os.path.isfile(qss_path):
            with open(qss_path, 'r') as f:
                app.setStyleSheet(f.read())
        else:
            app.setStyleSheet("")

    def save_settings(self):
        # 1) Met à jour la config en mémoire
        self.config['indicators']['rsi'] = self.rsi_input.value()
        spans = [int(x.strip()) for x in self.ema_input.text().split(',') if x.strip().isdigit()]
        self.config['indicators']['ema'] = spans
        self.config['indicators']['bollinger']['window'] = self.boll_window_input.value()
        self.config['indicators']['bollinger']['std'] = self.boll_std_input.value()
        self.config['alerts']['confidence_threshold'] = self.threshold_input.value()

        # 2) Sauvegarde sur disque
        try:
            os.makedirs('data', exist_ok=True)
            with open('data/config.json', 'w') as f:
                json.dump(self.config, f, indent=2)
            QMessageBox.information(self, "Paramètres", "Configuration sauvée avec succès.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de sauvegarder :\n{e}")
