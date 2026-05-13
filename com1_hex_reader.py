"""
COM1 HEX Reader
Legge dati esadecimali dalla porta COM1,
scarta i primi 2 caratteri e stampa il valore decimale corrispondente.

Requisiti:
    pip install pyserial

Per compilare in .exe su Windows:
    pip install pyinstaller
    pyinstaller --onefile --console com1_hex_reader.py
"""

import serial
import sys
import time

# ─── Configurazione porta seriale ──────────────────────────────────────────────
PORT       = "COM1"
BAUD_RATE  = 9600
BYTESIZE   = serial.EIGHTBITS
PARITY     = serial.PARITY_NONE
STOPBITS   = serial.STOPBITS_ONE
TIMEOUT    = 1          # secondi di attesa per ogni read()
READ_SIZE  = 64         # byte letti per volta


def process_hex_line(raw: str) -> None:
    """
    Riceve una stringa hex grezza (es. "FF1A2B"),
    scarta i primi 2 caratteri e converte il resto in decimale.
    """
    raw = raw.strip()
    if len(raw) < 3:
        print(f"  [SKIP] Dato troppo corto dopo trim: '{raw}'")
        return

    # Scarta i primi 2 caratteri
    trimmed = raw[2:]

    # Rimuove eventuali spazi interni prima della conversione
    hex_clean = trimmed.replace(" ", "").replace("\t", "")

    if not hex_clean:
        print(f"  [SKIP] Nessun dato rimasto dopo aver scartato i primi 2 caratteri.")
        return

    # Verifica che sia hex valido
    try:
        decimal_value = int(hex_clean, 16)
        print(f"  HEX originale : {raw}")
        print(f"  HEX trimmed   : {hex_clean}")
        print(f"  Valore decimale: {decimal_value}")
        print("-" * 40)
    except ValueError:
        print(f"  [ERRORE] '{hex_clean}' non è un valore esadecimale valido.")


def main():
    print("=" * 40)
    print("  COM1 HEX Reader")
    print(f"  Porta: {PORT}  |  Baud: {BAUD_RATE}")
    print("  Premi CTRL+C per uscire.")
    print("=" * 40)

    try:
        ser = serial.Serial(
            port     = PORT,
            baudrate = BAUD_RATE,
            bytesize = BYTESIZE,
            parity   = PARITY,
            stopbits = STOPBITS,
            timeout  = TIMEOUT
        )
    except serial.SerialException as e:
        print(f"\n[ERRORE] Impossibile aprire {PORT}: {e}")
        print("Verifica che la porta esista e non sia già in uso.")
        input("\nPremi INVIO per uscire...")
        sys.exit(1)

    print(f"\nPorta {PORT} aperta correttamente. In ascolto...\n")

    buffer = ""

    try:
        while True:
            try:
                raw_bytes = ser.read(READ_SIZE)
            except serial.SerialException as e:
                print(f"[ERRORE lettura] {e}")
                time.sleep(1)
                continue

            if not raw_bytes:
                # Timeout senza dati
                continue

            # Decodifica (ignora byte non validi)
            chunk = raw_bytes.decode("ascii", errors="ignore")
            buffer += chunk

            # Processa riga per riga (separatore \n o \r\n)
            while "\n" in buffer or "\r" in buffer:
                # Divide al primo fine-riga
                for sep in ("\r\n", "\n", "\r"):
                    if sep in buffer:
                        line, buffer = buffer.split(sep, 1)
                        if line.strip():
                            process_hex_line(line)
                        break

    except KeyboardInterrupt:
        print("\n\nInterruzione utente. Chiusura porta...")
    finally:
        if ser.is_open:
            ser.close()
            print(f"Porta {PORT} chiusa.")
        input("\nPremi INVIO per uscire...")


if __name__ == "__main__":
    main()
