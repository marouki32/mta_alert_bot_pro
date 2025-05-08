from PyQt5.QtWidgets import QWidget, QFormLayout, QLineEdit, QPushButton, QSpinBox, QDoubleSpinBox, QMessageBox
import json
import os

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

        # EMA spans (comma-separated)
        self.ema_input = QLineEdit()
        self.ema_input.setText(",".join(str(x) for x in self.config['indicators']['ema']))
        layout.addRow("EMA spans (comma-separated)", self.ema_input)

        # Bollinger window
        self.boll_window_input = QSpinBox()
        self.boll_window_input.setRange(1, 100)
        self.boll_window_input.setValue(self.config['indicators']['bollinger']['window'])
        layout.addRow("Bollinger window", self.boll_window_input)

        # Bollinger std dev
        self.boll_std_input = QDoubleSpinBox()
        self.boll_std_input.setRange(0.1, 10.0)
        self.boll_std_input.setSingleStep(0.1)
        self.boll_std_input.setValue(self.config['indicators']['bollinger']['std'])
        layout.addRow("Bollinger std dev", self.boll_std_input)

        # Confidence threshold
        self.threshold_input = QDoubleSpinBox()
        self.threshold_input.setRange(0.0, 1.0)
        self.threshold_input.setSingleStep(0.01)
        self.threshold_input.setValue(self.config['alerts']['confidence_threshold'])
        layout.addRow("Confidence threshold", self.threshold_input)

        # Save button
        self.save_button = QPushButton("Sauvegarder")
        self.save_button.clicked.connect(self.save_settings)
        layout.addRow(self.save_button)

        self.setLayout(layout)

    def save_settings(self):
        # 1) Met à jour la config en mémoire
        self.config['indicators']['rsi'] = self.rsi_input.value()
        spans = [int(x.strip()) for x in self.ema_input.text().split(',') if x.strip().isdigit()]
        self.config['indicators']['ema'] = spans
        self.config['indicators']['bollinger']['window'] = self.boll_window_input.value()
        self.config['indicators']['bollinger']['std'] = self.boll_std_input.value()
        self.config['alerts']['confidence_threshold'] = self.threshold_input.value()

        # 2) Sauvegarde dans data/config.json
        try:
            os.makedirs('data', exist_ok=True)
            with open('data/config.json', 'w') as f:
                json.dump(self.config, f, indent=2)
            QMessageBox.information(self, "Paramètres", "Configuration sauvée avec succès.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de sauvegarder :\n{e}")
