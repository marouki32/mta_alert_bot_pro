from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit
from PyQt5.QtCore import QThreadPool
from gui.worker import Worker
import subprocess, os

class BacktestMultiTab(QWidget):
    def __init__(self, config):
        super().__init__()
        self.threadpool = QThreadPool()
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.btn = QPushButton("Lancer backtest multi‑périodes")
        self.btn.clicked.connect(self.start)
        layout.addWidget(self.btn)

        self.out = QTextEdit()
        self.out.setReadOnly(True)
        layout.addWidget(self.out)

    def start(self):
        worker = Worker(self.run)
        worker.signals.result.connect(lambda txt: self.out.setPlainText(txt))
        worker.signals.error.connect(lambda err: self.out.setPlainText(err[1]))
        self.threadpool.start(worker)

    def run(self):
        cwd = os.getcwd()
        proc = subprocess.Popen(
            ["python", os.path.join(cwd, "backtest_multi.py")],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        out, err = proc.communicate()
        return err if err else out
