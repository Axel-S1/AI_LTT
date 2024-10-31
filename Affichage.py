from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QTextEdit
from PyQt5.QtGui import QScreen
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import sys
import pandas as pd
import numpy as np

def CSVtoNumpyArray(file_path):
    """Convertit un fichier CSV en tableau NumPy."""
    data = pd.read_csv(file_path)
    return data.to_numpy()

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Simulation de Trading")
        self.setGeometry(100, 100, 800, 600)

        # Créer un widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Créer un layout horizontal
        self.layout = QHBoxLayout()

        # Graphique pour afficher l'évolution de l'argent
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        # Zone de données
        self.data_area = QTextEdit()
        self.data_area.setReadOnly(True)
        self.layout.addWidget(self.data_area)

        # Appliquer le layout au widget central
        self.central_widget.setLayout(self.layout)

        # Simuler quelques données
        simu_data = CSVtoNumpyArray('sim_data.csv')
        trade_data = CSVtoNumpyArray('trade_data.csv')
        
        self.trade_gain = []
        for trade in trade_data:
            self.trade_gain.append(trade[2]-trade[1])
          
        self.day_gain = []    
        for i in range(len(simu_data)):
            if i > 96:
                self.day_gain.append(simu_data[i, 3] / simu_data[i-96, 3])
            
        
            
            
        self.money_history = simu_data[:, 3]            # Historique de l'argent
        self.final_money = simu_data[-1, 3]             # Argent final (exemple)
        self.worst_trade =  np.min(self.trade_gain)
        self.best_trade =   np.max(self.trade_gain)
        self.worst_day = (np.min(self.day_gain)-1)*100
        self.best_day = (np.max(self.day_gain)-1)*100
        
        # Mettre à jour les informations
        self.update_info()

    def update_info(self):
        # Mettre à jour le graphique
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(self.money_history, label='Évolution de l\'argent')
        ax.set_title('Historique de l\'argent')
        ax.set_xlabel('Pas de temps')
        ax.set_ylabel('Montant')
        ax.legend()
        self.canvas.draw()

        # Mettre à jour les données
        data_text = (
            f"Argent de fin : {self.final_money}\n"
            f"Meilleur trade : {self.best_trade}\n"
            f"Pire trade : {self.worst_trade}\n"
            f"Plus gros drawdown (daily) : {self.worst_day}%\n"
            f"Plus gros drawup   (daily) : {self.best_day}%\n"
        )
        self.data_area.setPlainText(data_text)

    def capture_screen(self):
        screen = QApplication.primaryScreen()
        img = screen.grabWindow(self.winId())
        img.save("screenshot.png", "PNG")
        self.data_area.append("Capture d'écran enregistrée : screenshot.png")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    # window.capture_screen()
    sys.exit(app.exec_())
