# MiceStTM – Sprachsteuerung für Barrierefreiheit unter Linux
**MiceStTM** (Speech to Text Macro) ist eine auf MX Linux basierende Lösung, die darauf abzielt, die Barrierefreiheit in der Linux-Umgebung zu verbessern. Durch die Nutzung der Cinnamon-Desktop-Umgebung ermöglicht das System eine umfassende Steuerung des PCs sowie von Home-Automation-Geräten via Sprachbefehlen und Audio-Feedback.

📥 Installation & Download
*   **Vollständiges ISO-Image:** Ein optimiertes, sofort einsatzbereites Image (basierend auf MX Linux) finden Sie auf [SourceForge](https://sourceforge.net/projects/micesttm-mx-voice-control/)
*   **Update-Service:** Die Dateien in diesem GitHub-Repository können genutzt werden, um eine bestehende Installation zu aktualisieren.
> **Hinweis:** Das System ist aktuell für die **X11-Window-Umgebung** und die **deutsche Sprache** optimiert.

🎙️ Spracherkennung (Engines)
MiceStTM bietet zwei verschiedene Ansätze zur Spracherkennung:

1.  **Lokal (Vosk):** (`/opt/micesttm/speechrecognition/mice_sttm.py`)  
    Die Auswertung erfolgt komplett offline auf Ihrem System. Es werden keine Daten ins Internet gesendet. Diese Version unterstützt zudem eine **Diktierfunktion**.
2.  **Cloud-basiert (Google):** (`/opt/micesttm/speechrecognition/mice_sttm-google.py`)  
    Die Audioaufnahme wird erst nach Erkennung des Trigger-Wortes zur Analyse an Google gesendet. Diese Variante bietet eine höhere Präzision, unterstützt jedoch keine Diktierfunktion.

✨ Key Features & Barrierefreiheit*   
*   **Individuelle Anpassung:** Einfache Konfiguration von Sprachbefehlen und Hausautomatisierung.
*   **Automatische Mikrofon-Regulierung** für optimale Pegel (Befehle aus bis zu 3 Metern Entfernung möglich, muss manuel angepasst werden).
*   **Navigation & Visuelle Hilfen:**
    *   Bildschirmgitter zur präzisen Maussteuerung.
    *   Invertierung von Fenstern via Sprachbefehl ("Fenster invertieren") oder Shortcut (`Super+I`).
    *   Mausmarkierungen zwischen definierten Punkten.*   **OCR & Vorlesefunktion:**
    *   Briefe via Scanner vorlesen("Brief vorlesen").
    *   Überwachung des Verzeichnisses `~/MiceStTM/read_aloud` (Texte/Bilder werden ausgelesen und angesagt).
    *   Vorlesen der Zwischenablage oder markierter Texte.

🛠️ Konfiguration & Anpassung

Das System ist so aufgebaut, dass eine Portierung in andere Sprachen leicht möglich ist (aktuell: Deutsch).
---
*   **Wake-Word:** Standardmäßig reagiert das System auf **"Computer"**. Anpassbar in `~/.config/micesttm/micesttm.ini`.
*   **Haussteuerung:** Unterstützung für **Tasmota, Shelly** und weitere Protokolle via HTTP/Curl.
*   **Makros:** Über 170 vordefinierte Befehle unter `~/.config/micesttm/macros/de/macro`.

### Beispiel eines Makros (Syntax)
```yaml
category: Shelly Lampe
comment: Shelly Gerät schalten
trigger: (Decke.*) für (ein.*|an.*)
terminal_command: curl "http://192.168.0.46/relay/0?turn=on&timer={last_spoken_number}"
tts: Die Deckenlampe wurde für {last_spoken_number} Sekunden eingeschaltet.

------------------------------
🗣️ Beispiel-Befehle

* "Computer, wie spät ist es?"
* "Eine Nachricht an Peter" (Öffnet Signal/Telegram, wählt Kontakt und wartet auf Text-Input).
* "Computer, schreibe 'Dies ist mein Text Punkt setzen'" (Erzeugt: dies ist mein text.).
* "Computer, Maus 20 nach links" oder "Taste löschen 20 mal drücken".

------------------------------
```

🤝 Mitwirken & Kontakt
Dies ist ein Ein-Personen-Projekt. Feedback, Fehlerberichte und Erweiterungen sind ausdrücklich erwünscht!

„Feel free to fork this project and submit pull requests. Contributions are always welcome!“

Disclaimer: Die Nutzung erfolgt auf eigene Verantwortung. Da sich das Projekt in der Entwicklung befindet, können Fehler nicht ausgeschlossen werden.

