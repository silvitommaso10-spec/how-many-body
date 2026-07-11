# Più o Meno — I signori della storia

Un gioco in stile **Higher / Lower** con oltre **1000 personaggi storici** reali
(imperatori, condottieri, re, sultani, dittatori, esploratori…).

Ti viene mostrato un personaggio con un valore rivelato; per lo sfidante devi
indovinare se il suo valore è **di più** o **di meno**. Ogni risposta giusta
allunga la serie; sbagli una volta e la partita finisce. Il record viene salvato
sul dispositivo.

## Categorie

| Categoria | Domanda |
|-----------|---------|
| ⚔️ **Vittime** | Chi ha ucciso di più (morti attribuite a guerre e campagne) |
| ❤️ **Donne** | Chi ha avuto più donne (mogli, amanti, concubine note) |
| 🗺️ **Territorio** | Chi ha conquistato più terra (massima estensione, in km²) |

## Come giocare

Apri semplicemente **`index.html`** in un browser (funziona anche su telefono,
il layout è mobile-first). Nessuna dipendenza, nessun server necessario.

Su desktop puoi usare anche i tasti freccia **↑ / ↓** per rispondere.

## Struttura

```
index.html            Il gioco (HTML/CSS/JS, self-contained a parte i dati)
data.js               Il dataset dei personaggi (window.CHARACTERS)
tools/generate_data.py  Generatore del dataset
```

Per rigenerare o ampliare il dataset:

```bash
python3 tools/generate_data.py   # riscrive data.js
```

## Nota sui dati

I valori sono **approssimativi e a scopo puramente ludico**: per le figure più
famose sono impostati a mano su stime storiche, mentre per gli altri personaggi
reali sono assegnati in modo deterministico entro intervalli plausibili per la
loro scala storica. Servono a rendere il confronto divertente, non come fonte
storica accurata.
