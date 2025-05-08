from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit
from PyQt5.QtCore import QThreadPool
from gui.worker import Worker
import subprocess, os

class BacktestTab(QWidget):
    def __init__(self, config):
        super().__init__()
        self.threadpool = QThreadPool()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.run_btn = QPushButton("Lancer backtest")
        self.run_btn.clicked.connect(self.start_backtest)
        layout.addWidget(self.run_btn)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

    def start_backtest(self):
        worker = Worker(self.run_backtest)
        worker.signals.result.connect(lambda out: self.output.setPlainText(out))
        worker.signals.error.connect(lambda err: self.output.setPlainText(err[1]))
        self.threadpool.start(worker)

    def run_backtest(self):
        cwd = os.getcwd()
        proc = subprocess.Popen(
            ["python", os.path.join(cwd, "backtest.py")],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        out, err = proc.communicate()
        return err if err else out
