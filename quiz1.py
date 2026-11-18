"""Krypto-Quiz als Streamlit-App.

Die Fragen stehen in der Textdatei krypto_fragen.txt (im selben Ordner).
Pro Zeile eine Frage, durch Semikolon getrennt:
Frage; Antwort 1; Antwort 2; Antwort 3; Nummer der richtigen Antwort (1-3)
"""

import random
from pathlib import Path

import streamlit as st

FRAGEN_DATEI = Path(__file__).parent / "krypto_fragen.txt"
ANZAHL_FRAGEN = 20

st.set_page_config(page_title="Krypto-Quiz", page_icon="❓")


@st.cache_data
def lade_fragen(pfad):
    """Liest die Fragendatei und gibt eine Liste von Fragen zurück."""
    fragen = []
    with open(pfad, encoding="utf-8-sig") as datei:
        for zeile in datei:
            zeile = zeile.strip()
            if not zeile or zeile.startswith("#"):
                continue
            teile = [t.strip() for t in zeile.split(";")]
            if len(teile) != 5 or teile[4] not in ("1", "2", "3"):
                continue  # fehlerhafte Zeile überspringen
            fragen.append(
                {
                    "frage": teile[0],
                    "antworten": teile[1:4],
                    "richtig": int(teile[4]) - 1,  # Index 0-2
                }
            )
    return fragen


def neues_spiel():
    pool = lade_fragen(FRAGEN_DATEI)
    anzahl = min(ANZAHL_FRAGEN, len(pool))
    st.session_state.fragen = random.sample(pool, anzahl)
    st.session_state.nummer = 0
    st.session_state.punkte = 0
    st.session_state.antwort = None


def antwort_geben(index):
    st.session_state.antwort = index
    frage = st.session_state.fragen[st.session_state.nummer]
    if index == frage["richtig"]:
        st.session_state.punkte += 1


def naechste_frage():
    st.session_state.nummer += 1
    st.session_state.antwort = None


# ---------------------------------------------------------------- Start
st.title("Krypto-Quiz")

if not FRAGEN_DATEI.exists():
    st.error(f"Die Fragendatei '{FRAGEN_DATEI.name}' wurde nicht gefunden.")
    st.stop()

if "fragen" not in st.session_state:
    neues_spiel()

fragen = st.session_state.fragen
gesamt = len(fragen)

if gesamt == 0:
    st.error("In der Fragendatei wurden keine gültigen Fragen gefunden.")
    st.stop()

nummer = st.session_state.nummer

# ------------------------------------------------------------- Ergebnis
if nummer >= gesamt:
    punkte = st.session_state.punkte
    st.header("Ihr Ergebnis")
    st.subheader(f"{punkte} von {gesamt} Fragen richtig")
    st.progress(punkte / gesamt)

    if punkte == gesamt:
        st.success("Ausgezeichnet! Alle Fragen richtig.")
    elif punkte >= gesamt * 0.7:
        st.success("Sehr gut! Sie kennen sich schon gut aus.")
    elif punkte >= gesamt * 0.4:
        st.info("Ordentlich. Ein zweiter Durchgang lohnt sich.")
    else:
        st.warning("Da ist noch Luft nach oben. Versuchen Sie es gern noch einmal.")

    st.button("Neues Spiel", on_click=neues_spiel, use_container_width=True)
    st.stop()

# ---------------------------------------------------------------- Frage
frage = fragen[nummer]
beantwortet = st.session_state.antwort is not None

st.caption(f"Frage {nummer + 1} von {gesamt}")
st.progress(nummer / gesamt)
st.subheader(frage["frage"])

for i, text in enumerate(frage["antworten"]):
    st.button(
        text,
        key=f"antwort_{nummer}_{i}",
        on_click=antwort_geben,
        args=(i,),
        disabled=beantwortet,
        use_container_width=True,
    )

# ----------------------------------------------------------- Rückmeldung
if beantwortet:
    if st.session_state.antwort == frage["richtig"]:
        st.success("Richtig!")
    else:
        richtige_antwort = frage["antworten"][frage["richtig"]]
        st.error(f"Leider falsch. Richtig ist: {richtige_antwort}")

    letzte = nummer + 1 >= gesamt
    st.button(
        "Ergebnis anzeigen" if letzte else "Nächste Frage",
        on_click=naechste_frage,
        type="primary",
        use_container_width=True,
    )

st.caption(f"Punkte bisher: {st.session_state.punkte}")
