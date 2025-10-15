import sys
from datetime import datetime
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtGui import QTextDocument

def categorie_imc(imc: float, sexe: str) -> tuple[str, str]:
    ajust = -0.5 if sexe == "Femme" else 0.0
    imc_adj = imc + ajust
    if imc_adj < 18.5:
        return "Insuffisance pondérale", "#2D9CDB"
    elif imc_adj < 25:
        return "Corpulence normale", "#27AE60"
    elif imc_adj < 30:
        return "Surpoids", "#F2C94C"
    elif imc_adj < 35:
        return "Obésité modérée (classe I)", "#F2994A"
    elif imc_adj < 40:
        return "Obésité sévère (classe II)", "#EB5757"
    else:
        return "Obésité massive (classe III)", "#9B51E0"

def conseils_par_categorie(cat: str) -> str:
    if "Insuffisance" in cat:
        return "Augmenter légèrement l’apport calorique avec des aliments riches en nutriments."
    if "normale" in cat:
        return "Maintenir une alimentation équilibrée et une activité physique régulière."
    if "Surpoids" in cat:
        return "Réduire les sucres rapides et pratiquer plus d’exercice."
    if "modérée" in cat:
        return "Rééquilibrage alimentaire et suivi médical conseillés."
    if "sévère" in cat:
        return "Accompagnement médical et nutritionniste recommandés."
    return "Prise en charge médicale urgente recommandée."

class IMCApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculateur d'IMC - BARMEDISERV")
        self.setMinimumWidth(520)

        # ✅ Icône personnalisée
        self.setWindowIcon(QtGui.QIcon("ico.png"))

        self.setStyleSheet("""
            QWidget {
                background-color: #F7F9FC;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QDoubleSpinBox, QComboBox {
                border: 1px solid #C5C6CA;
                border-radius: 6px;
                padding: 6px;
                background: white;
            }
            QPushButton {
                background-color: #2D9CDB;
                color: white;
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #56CCF2; }
            QPushButton#secondary { background-color: #6C757D; }
            QPushButton#secondary:hover { background-color: #868E96; }
            QLabel#title {
                font-size: 20px;
                font-weight: 700;
                color: #2D3436;
            }
        """)

        # Champs
        self.combo_sexe = QtWidgets.QComboBox()
        self.combo_sexe.addItems(["Homme", "Femme"])
        self.spin_poids = QtWidgets.QDoubleSpinBox()
        self.spin_poids.setRange(20.0, 300.0)
        self.spin_poids.setDecimals(1)
        self.spin_poids.setSuffix(" kg")
        self.spin_poids.setValue(70.0)
        self.spin_taille = QtWidgets.QDoubleSpinBox()
        self.spin_taille.setRange(50.0, 250.0)
        self.spin_taille.setDecimals(1)
        self.spin_taille.setSuffix(" cm")
        self.spin_taille.setValue(175.0)

        # Boutons
        self.btn_calc = QtWidgets.QPushButton("Calculer l’IMC")
        self.btn_reset = QtWidgets.QPushButton("Réinitialiser"); self.btn_reset.setObjectName("secondary")
        self.btn_export = QtWidgets.QPushButton("Exporter le rapport (PDF)")
        self.btn_quit = QtWidgets.QPushButton("Quitter"); self.btn_quit.setObjectName("secondary")

        # Résultat
        self.label_result = QtWidgets.QLabel("Résultat affiché ici")
        self.label_result.setAlignment(QtCore.Qt.AlignCenter)
        self.label_result.setWordWrap(True)
        self.label_result.setStyleSheet("""
            QLabel {
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding: 14px;
                font-size: 16px;
                background: #FAFAFA;
            }
        """)

        # Layout
        form = QtWidgets.QFormLayout()
        form.addRow("Sexe :", self.combo_sexe)
        form.addRow("Poids :", self.spin_poids)
        form.addRow("Taille :", self.spin_taille)

        buttons1 = QtWidgets.QHBoxLayout()
        buttons1.addWidget(self.btn_calc)
        buttons1.addWidget(self.btn_export)

        buttons2 = QtWidgets.QHBoxLayout()
        buttons2.addWidget(self.btn_reset)
        buttons2.addStretch()
        buttons2.addWidget(self.btn_quit)

        layout = QtWidgets.QVBoxLayout(self)
        title = QtWidgets.QLabel(" Calculateur d’Indice de Masse Corporelle (IMC)")
        title.setObjectName("title")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addLayout(form)
        layout.addWidget(self.label_result)
        layout.addSpacing(10)
        layout.addLayout(buttons1)
        layout.addLayout(buttons2)
        note = QtWidgets.QLabel("ℹ️ Taille en cm, Poids en kg. L’IMC = poids(kg) / [taille(m)]².")
        note.setStyleSheet("color: #777;")
        layout.addWidget(note)

        # Connexions
        self.btn_calc.clicked.connect(self.calc_imc)
        self.btn_reset.clicked.connect(self.reset_fields)
        self.btn_quit.clicked.connect(self.close)
        self.btn_export.clicked.connect(self.export_pdf)

    def calc_imc(self):
        poids = self.spin_poids.value()
        taille_cm = self.spin_taille.value()
        sexe = self.combo_sexe.currentText()
        if poids <= 0 or taille_cm <= 0:
            QtWidgets.QMessageBox.warning(self, "Erreur", "Veuillez entrer des valeurs valides.")
            return
        taille_m = taille_cm / 100
        self.imc = poids / (taille_m ** 2)
        self.sexe, self.poids, self.taille_cm = sexe, poids, taille_cm
        texte_cat, couleur = categorie_imc(self.imc, sexe)
        self.categorie, self.couleur = texte_cat, couleur
        self.label_result.setText(f"<b>IMC : {self.imc:.2f}</b><br>{texte_cat}")
        self.label_result.setStyleSheet(f"""
            QLabel {{
                border-radius: 10px;
                padding: 14px;
                font-size: 16px;
                background: {couleur}20;
                color: #2D3436;
                border: 1px solid {couleur};
            }}
        """)

    def reset_fields(self):
        self.combo_sexe.setCurrentIndex(0)
        self.spin_poids.setValue(70.0)
        self.spin_taille.setValue(175.0)
        self.label_result.setText("Résultat affiché ici")
        self.label_result.setStyleSheet("""
            QLabel {
                border: 1px solid #E0E0E0;
                border-radius: 10px;
                padding: 14px;
                font-size: 16px;
                background: #FAFAFA;
            }
        """)

    def export_pdf(self):
        if not hasattr(self, "imc"):
            QtWidgets.QMessageBox.information(self, "Info", "Calculez d’abord l’IMC avant d’exporter le rapport.")
            return

        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Enregistrer le rapport PDF", "rapport_imc.pdf", "Fichier PDF (*.pdf)"
        )
        if not path:
            return

        date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        conseils = conseils_par_categorie(self.categorie)

        html = f"""
        <html>
        <body style="font-family:Arial; color:#333;">
        <div style="text-align:center;">
            <img src='ico.png' width='120'><br>
            <h2 style="color:#2D9CDB;">Rapport IMC - BARMEDISERV</h2>
        </div>
        <p><b>Date :</b> {date_str}</p>
        <p><b>Sexe :</b> {self.sexe}<br>
        <b>Poids :</b> {self.poids:.1f} kg<br>
        <b>Taille :</b> {self.taille_cm:.1f} cm<br>
        <b>IMC :</b> {self.imc:.2f}<br>
        <b>Catégorie :</b> {self.categorie}</p>
        <h3>Conseils :</h3>
        <p>{conseils}</p>
        <hr>
        <p style="text-align:center;font-size:10pt;color:#777;">
        Signature : <b>EL KAOURI CHOAIB 🖋️</b><br>
        Rapport généré automatiquement par le calculateur IMC.
        </p>
        </body>
        </html>
        """

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(path)
        printer.setPageMargins(12, 12, 12, 12, QPrinter.Millimeter)
        doc = QTextDocument()
        doc.setHtml(html)
        doc.print_(printer)
        QtWidgets.QMessageBox.information(self, "Succès", f"Rapport exporté :\n{path}")

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = IMCApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

