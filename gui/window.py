import os
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QSystemTrayIcon
from PyQt5.QtGui import QIcon
from gui.tabs.performance_tab import PerformanceTab
from gui.tabs.surveillance_tab    import SurveillanceTab
from gui.tabs.settings_tab        import SettingsTab
from gui.tabs.history_tab         import HistoryTab
from gui.tabs.backtest_tab        import BacktestTab
from gui.tabs.backtest_multi_tab  import BacktestMultiTab
from gui.tabs.chart_tab           import ChartTab
from gui.tabs.export_tab          import ExportTab
from gui.tabs.optimize_tab import OptimizeTab
from gui.tabs.paper_trading_tab import PaperTradingTab

class MainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.setWindowTitle("MTA Alert Bot Pro")
        self.resize(800, 600)

        # 🔧 Charger icon.png via un chemin absolu pour Qt
        icon_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "icon.png")
        )
        if not os.path.isfile(icon_path):
            print("⚠️ icon.png introuvable à :", icon_path)
        # Définir l’icône de la fenêtre (et de la tray‑icon)
        self.setWindowIcon(QIcon(icon_path))

        # Créer et afficher la System Tray Icon
        self.tray_icon = QSystemTrayIcon(self.windowIcon(), parent=self)
        self.tray_icon.show()

        # Création des onglets
        tabs = QTabWidget()
        tabs.addTab(SurveillanceTab(config),            "Surveillance")
        tabs.addTab(SettingsTab(config),                "Paramètres")
        tabs.addTab(HistoryTab(config),                 "Historique")
        tabs.addTab(PaperTradingTab(config),            "Paper-Trading")
        tabs.addTab(BacktestTab(config),                "Backtest")
        tabs.addTab(BacktestMultiTab(config),           "Backtest Multi‑Périodes")
        tabs.addTab(ChartTab(config),                   "Graphiques")
        tabs.addTab(OptimizeTab(config),                "Optimisation")
        tabs.addTab(ExportTab(config),                  "Export")
        tabs.addTab(PerformanceTab(config),             "Performance")
        self.setCentralWidget(tabs)
