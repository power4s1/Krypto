"""Quiz: 20 zufaellige Fragen aus einem Pool, je drei Antwortmoeglichkeiten.

Die Fragen stehen in der Textdatei "fragen.txt" (im selben Ordner wie dieses
Programm), eine Frage pro Zeile, Teile durch Semikolon getrennt:

    Frage; Antwort 1; Antwort 2; Antwort 3; Nummer der richtigen Antwort (1-3)

Beispiel:
    Was ist die Hauptstadt von Deutschland?; Hamburg; Berlin; Muenchen; 2

Leere Zeilen und Zeilen, die mit # beginnen, werden ignoriert.
Die Datei sollte als UTF-8 gespeichert sein (damit Umlaute stimmen).
"""

import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox

ANZAHL_FRAGEN = 20
DATEINAME = "fragen.txt"


def lade_fragen(pfad):
    """Liest die Fragen aus der Textdatei. Gibt (Fragenliste, Anzahl uebersprungener Zeilen) zurueck."""
    fragen = []
    uebersprungen = 0
    with open(pfad, encoding="utf-8-sig") as datei:
        for zeile in datei:
            zeile = zeile.strip()
            if not zeile or zeile.startswith("#"):
                continue
            teile = [t.strip() for t in zeile.split(";")]
            gueltig = (
                len(teile) == 5
                and all(teile[:4])
                and teile[4] in ("1", "2", "3")
            )
            if not gueltig:
                uebersprungen += 1
                continue
            fragen.append(
                {
                    "frage": teile[0],
                    "antworten": teile[1:4],
                    "richtig": int(teile[4]) - 1,  # Index 0, 1 oder 2
                }
            )
    return fragen, uebersprungen


class QuizApp(tk.Tk):
    def __init__(self, fragen):
        super().__init__()
        self.title("Quiz")
        self.geometry("640x420")
        self.minsize(520, 380)

        self.pool = fragen
        self.anzahl = min(ANZAHL_FRAGEN, len(self.pool))

        # Widgets
        self.kopf = tk.Label(self, font=("Arial", 11))
        self.kopf.pack(pady=(14, 4))

        self.frage_label = tk.Label(
            self, font=("Arial", 15, "bold"), wraplength=580, justify="center"
        )
        self.frage_label.pack(pady=(6, 16), padx=20)

        self.buttons = []
        for i in range(3):
            b = tk.Button(
                self,
                font=("Arial", 13),
                wraplength=520,
                width=44,
                pady=6,
                command=lambda i=i: self.antwort_gewaehlt(i),
            )
            b.pack(pady=4)
            self.buttons.append(b)

        self.rueckmeldung = tk.Label(self, font=("Arial", 13, "bold"), wraplength=580)
        self.rueckmeldung.pack(pady=(12, 4))

        self.weiter_button = tk.Button(
            self, text="Weiter", font=("Arial", 13), command=self.naechste_frage
        )
        self.weiter_button.pack(pady=6)

        self.start()

    # ---- Ablauf ----------------------------------------------------------
    def start(self):
        """Neuer Durchgang: 20 verschiedene Fragen zufaellig ziehen."""
        self.auswahl = random.sample(self.pool, self.anzahl)
        self.nummer = 0
        self.punkte = 0
        self.richtige_antwort = None  # gespeicherter Index der richtigen Antwort
        self.beantwortet = False
        self.zeige_quiz_widgets()
        self.naechste_frage()

    def zeige_quiz_widgets(self):
        for b in self.buttons:
            b.pack_configure()
            b.pack(pady=4)
        self.frage_label.pack(pady=(6, 16), padx=20)
        self.rueckmeldung.pack(pady=(12, 4))
        self.weiter_button.pack(pady=6)
        if hasattr(self, "ende_frame"):
            self.ende_frame.destroy()
            del self.ende_frame

    def naechste_frage(self):
        if self.nummer >= self.anzahl:
            self.zeige_ergebnis()
            return

        frage = self.auswahl[self.nummer]
        self.richtige_antwort = frage["richtig"]  # richtige Antwort speichern
        self.beantwortet = False

        self.kopf.config(
            text=f"Frage {self.nummer + 1} von {self.anzahl}   |   Punkte: {self.punkte}"
        )
        self.frage_label.config(text=frage["frage"])
        for b, text in zip(self.buttons, frage["antworten"]):
            b.config(text=text, state="normal", bg="SystemButtonFace")
        self.rueckmeldung.config(text="")
        self.weiter_button.config(state="disabled")

    def antwort_gewaehlt(self, index):
        if self.beantwortet:
            return
        self.beantwortet = True

        for b in self.buttons:
            b.config(state="disabled")

        if index == self.richtige_antwort:
            self.punkte += 1
            self.rueckmeldung.config(text="Richtig!", fg="#1a7f37")
        else:
            richtig_text = self.buttons[self.richtige_antwort].cget("text")
            self.rueckmeldung.config(
                text=f"Leider falsch. Richtig ist: {richtig_text}", fg="#c62828"
            )

        self.nummer += 1
        self.kopf.config(
            text=f"Frage {min(self.nummer, self.anzahl)} von {self.anzahl}   |   Punkte: {self.punkte}"
        )
        text = "Weiter" if self.nummer < self.anzahl else "Ergebnis anzeigen"
        self.weiter_button.config(text=text, state="normal")

    def zeige_ergebnis(self):
        # Quiz-Elemente ausblenden
        for w in (self.frage_label, self.rueckmeldung, self.weiter_button, *self.buttons):
            w.pack_forget()

        prozent = round(100 * self.punkte / self.anzahl) if self.anzahl else 0
        self.kopf.config(text="Geschafft!")

        self.ende_frame = tk.Frame(self)
        self.ende_frame.pack(pady=20)
        tk.Label(
            self.ende_frame,
            text=f"Gesamtergebnis: {self.punkte} von {self.anzahl} richtig",
            font=("Arial", 18, "bold"),
        ).pack(pady=(10, 4))
        tk.Label(self.ende_frame, text=f"{prozent} %", font=("Arial", 16)).pack(pady=4)
        tk.Button(
            self.ende_frame,
            text="Nochmal spielen",
            font=("Arial", 13),
            command=self.start,
        ).pack(pady=(18, 6))
        tk.Button(
            self.ende_frame, text="Beenden", font=("Arial", 13), command=self.destroy
        ).pack(pady=4)


def main():
    ordner = os.path.dirname(os.path.abspath(__file__))
    pfad = os.path.join(ordner, DATEINAME)

    if not os.path.exists(pfad):
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(
            "Quiz",
            f"Die Datei {DATEINAME} wurde nicht gefunden.\nBitte die Fragendatei auswaehlen.",
        )
        pfad = filedialog.askopenfilename(
            title="Fragendatei waehlen", filetypes=[("Textdateien", "*.txt")]
        )
        root.destroy()
        if not pfad:
            return

    try:
        fragen, uebersprungen = lade_fragen(pfad)
    except UnicodeDecodeError:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Quiz",
            "Die Datei konnte nicht gelesen werden.\nBitte als UTF-8 speichern.",
        )
        root.destroy()
        return

    if not fragen:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Quiz", "In der Datei wurden keine gueltigen Fragen gefunden.")
        root.destroy()
        return

    if uebersprungen:
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning(
            "Quiz", f"{uebersprungen} Zeile(n) hatten ein falsches Format und wurden uebersprungen."
        )
        root.destroy()

    QuizApp(fragen).mainloop()


if __name__ == "__main__":
    main()
