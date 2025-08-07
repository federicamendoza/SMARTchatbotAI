import os
from company_vector_store import CompanyVectorStore

# Nomi dei file dell'indice da rimuovere
INDEX_FILE = "company_index.bin"
TEXTS_FILE = "company_texts.pkl"

def rebuild():
    """
    Forza la ricostruzione del vector store cancellando i file vecchi
    e creando una nuova istanza della classe.
    """
    print("🚀 Inizio della ricostruzione del Company Vector Store...")

    # Step 1: Cancella i file dell'indice esistenti, se presenti
    if os.path.exists(INDEX_FILE):
        os.remove(INDEX_FILE)
        print(f"🗑️  File '{INDEX_FILE}' cancellato.")
        
    if os.path.exists(TEXTS_FILE):
        os.remove(TEXTS_FILE)
        print(f"🗑️  File '{TEXTS_FILE}' cancellato.")

    # Step 2: Crea una nuova istanza per forzare la ricostruzione
    # La logica interna di CompanyVectorStore si occuperà di creare il nuovo indice
    # perché non troverà i file esistenti.
    print("\n✨ Creazione del nuovo indice in corso...")
    
    try:
        # Questa riga attiverà il metodo _create_index()
        store = CompanyVectorStore()
        print("\n✅ Successo! Il Company Vector Store è stato ricostruito correttamente.")
    except Exception as e:
        print(f"\n❌ ERRORE durante la ricostruzione: {e}")
        print("Verifica che tutte le dipendenze (es. sentence-transformers) siano installate.")


if __name__ == "__main__":
    rebuild()