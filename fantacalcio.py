import streamlit as st
import pandas as pd
import json
import os

# --- CONFIGURAZIONE FILE LOCALI (DATABASE) ---
FILE_SQUADRE = "squadre.json"
FILE_LEGHE = "leghe.json"
FILE_VOTI = "voti.json"
FILE_FORMAZIONI = "formazioni.json"

def carica_dati(file, default):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return default

def salva_dati(file, dati):
    with open(file, "w") as f:
        json.dump(dati, f, indent=4)

# Inizializzazione dati
dati_squadre = carica_dati(FILE_SQUADRE, {})
dati_leghe = carica_dati(FILE_LEGHE, ["Lega Globale"])
dati_voti = carica_dati(FILE_VOTI, {})
dati_formazioni = carica_dati(FILE_FORMAZIONI, {})

# Configurazione Pagina
st.set_page_config(page_title="Fantamondiale Dashboard", page_icon="🏆", layout="wide")

# --- GENERATORE AUTOMATICO DEL DATABASE CALCIATORI ---
# Se il file manca o è vuoto, lo creiamo noi direttamente da qui senza errori!
giocatori_default = """Nome,Ruolo,Nazione,Quotazione
Emiliano Martinez,Portiere,Argentina,18
Alisson,Portiere,Brasile,17
Donnarumma,Portiere,Italia,16
Dimarco,Difensore,Italia,18
Bastoni,Difensore,Italia,16
Theo Hernandez,Difensore,Francia,17
Barella,Centrocampista,Italia,20
Bellingham,Centrocampista,Inghilterra,28
De Bruyne,Centrocampista,Belgio,26
Messi,Attaccante,Argentina,35
Lautaro Martinez,Attaccante,Argentina,32
Mbappe,Attaccante,Francia,36
Kane,Attaccante,Inghilterra,34
Cristiano Ronaldo,Attaccante,Portogallo,26
Lamine Yamal,Attaccante,Spagna,28"""

if not os.path.exists("calciatori.csv") or os.path.getsize("calciatori.csv") == 0:
    with open("calciatori.csv", "w", encoding="utf-8") as f:
        f.write(giocatori_default)

# Caricamento sicuro
df_calciatori = pd.read_csv("calciatori.csv", encoding="utf-8")

# --- BARRA LATERALE: LOGIN GENERALE ---
st.sidebar.title("⚽ Fantamondiale")
ruolo = st.sidebar.radio("Scegli il tuo ruolo:", ["Partecipante", "Host / Amministratore"])

# =========================================================================
# 1. SEZIONE INTERFACCIA HOST
# =========================================================================
if ruolo == "Host / Amministratore":
    password = st.sidebar.text_input("Password Host:", type="password")
    if password != "admin123":
        st.warning("🔒 Inserisci la password corretta per sbloccare il menu di gestione. (Default: admin123)")
        st.stop()
        
    st.sidebar.markdown("---")
    st.sidebar.subheader("👑 MENU AMMINISTRATORE")
    
    menu_host = st.sidebar.radio(
        "Seleziona attività:",
        [
            "🆕 Crea / Gestisci Leghe",
            "🏷️ Svincolati",
            "👥 Listone",
            "📊 Statistiche di Lega",
            "📜 Registro attività Admin",
            "🏥 Infermeria",
            "🧮 Calcolo giornata (Voti e Bonus)",
            "⚙️ Gestione rose",
            "📋 Gestione formazioni",
            "⚙️ Crediti",
            "📉 Penalità e punti extra",
            "🏆 Sala trofei",
            "🎖️ Albo d'oro",
            "📁 Documenti di Lega",
            "📢 Comunicazioni"
        ]
    )
    
    st.title(f"Pannello Host: {menu_host}")
    
    if "Crea / Gestisci Leghe" in menu_host:
        nuova_lega = st.text_input("Nome nuova lega da creare:")
        if st.button("Conferma e Crea"):
            if nuova_lega and nuova_lega not in dati_leghe:
                dati_leghe.append(nuova_lega)
                salva_dati(FILE_LEGHE, dati_leghe)
                st.success(f"Lega '{nuova_lega}' creata!")
                st.rerun()
                
    elif "Calcolo giornata" in menu_host:
        st.write("Inserisci il voto base e spunta i bonus/malus del giocatore:")
        giocatore_voto = st.selectbox("Calciatore:", df_calciatori['Nome'].tolist())
        voto_base = st.number_input("Voto Pagella:", min_value=0.0, max_value=10.0, value=6.0, step=0.5)
        
        c1, c2 = st.columns(2)
        with c1:
            n_gol = st.number_input("Gol (+3 cad.):", min_value=0, value=0)
            assist_soft = st.checkbox("Assist Soft (+1)")
            assist_standard = st.checkbox("Assist Standard (+1)")
            assist_gold = st.checkbox("Assist Gold (+1)")
            potm = st.checkbox("Player of the Match (+0.5)")
        with c2:
            clean_sheet = st.checkbox("Porta inviolata (+1)")
            espulsione = st.checkbox("Espulsione (-1)")
            autogol = st.checkbox("Autogol (-2)")
            ammonizione = st.checkbox("Ammonizione (-0.5)")
            
        punteggio_finale = voto_base + (n_gol * 3) + (1 if assist_soft else 0) + (1 if assist_standard else 0) + (1 if assist_gold else 0) + (0.5 if potm else 0) + (1 if clean_sheet else 0) - (1 if espulsione else 0) - (2 if autogol else 0) - (0.5 if ammonizione else 0)
        st.info(f"Calcolo in tempo reale: **{punteggio_finale} punti**")
        
        if st.button("Salva Punteggio Ufficiale"):
            dati_voti[giocatore_voto] = punteggio_finale
            salva_dati(FILE_VOTI, dati_voti)
            st.success(f"Punteggio di {giocatore_voto} memorizzato!")
            st.rerun()
            
    else:
        st.info(f"La sezione '{menu_host}' è attiva sul menu laterale.")

# =========================================================================
# 2. SEZIONE INTERFACCIA PARTECIPANTE REGOLARE
# =========================================================================
else:
    st.sidebar.subheader("Seleziona la tua Lega")
    lega_selezionata = st.sidebar.selectbox("Lega:", dati_leghe)
    nome_utente = st.sidebar.text_input("Tuo Nome Squadra:").strip()

    if not nome_utente:
        st.info("👈 Inserisci il nome della tua squadra nella barra laterale per entrare.")
        st.stop()

    user_key = f"{lega_selezionata}_{nome_utente}"
    
    menu_utente = st.sidebar.radio(
        "Menu Partecipante:",
        ["📅 Calendario", "👕 Gestione Squadra (Mercato e Formazione)", "📊 Classifica"]
    )
    
    st.title(f"Squadra: {nome_utente} | {lega_selezionata}")
    
    if menu_utente == "📅 Calendario":
        st.header("📅 Calendario Partite del Mondiale")
        st.write("⚽ **Giornata 1**")
        st.text("Gara 1: Squadra A vs Squadra B\nGara 2: Squadra C vs Squadra D")
        
    elif menu_utente == "👕 Gestione Squadra (Mercato e Formazione)":
        tab_mercato, tab_campo = st.tabs(["🛒 Mercato Acquisti (+)", "📋 Schiera 11 Titolari"])
        
        with tab_mercato:
            st.subheader("🛒 Acquista i tuoi giocatori")
            BUDGET_MASSIMO = 250
            squadra_salvata = dati_squadre.get(user_key, [])
            
            if f"rosa_{user_key}" not in st.session_state:
                st.session_state[f"rosa_{user_key}"] = squadra_salvata

            rosa_corrente = st.session_state[f"rosa_{user_key}"]
            df_scelti = df_calciatori[df_calciatori['Nome'].isin(rosa_corrente)]
            totale_speso = df_scelti['Quotazione'].sum()
            rimanente = BUDGET_MASSIMO - totale_speso

            st.markdown(f"""
            <div style="background-color:#1e1e1e; padding:15px; border-radius:10px; margin-bottom:20px;">
                <h3 style="margin:0; color:#deff9a;">Crediti Rimasti: {rimanente} <span style="font-size:16px; color:#fff;">(Spesi: {totale_speso}/{BUDGET_MASSIMO})</span></h3>
            </div>
            """, unsafe_allow_html=True)

            if rosa_corrente:
                st.write("##### 🏃‍♂️ I tuoi calciatori acquistati:")
                for calc_rimosso in list(rosa_corrente):
                    col_r1, col_r2 = st.columns([5, 1])
                    if calc_rimosso in df_calciatori['Nome'].values:
                        ruolo_calc = df_calciatori[df_calciatori['Nome'] == calc_rimosso]['Ruolo'].values[0]
                        col_r1.write(f"• **{calc_rimosso}** ({ruolo_calc})")
                        if col_r2.button("❌ Rimuovi", key=f"rem_{calc_rimosso}"):
                            st.session_state[f"rosa_{user_key}"].remove(calc_rimosso)
                            st.rerun()
                
                if st.button("💾 SALVA LA ROSA NEL DATABASE"):
                    dati_squadre[user_key] = rosa_corrente
                    salva_dati(FILE_SQUADRE, dati_squadre)
                    st.success("Rosa salvata nel database!")
            else:
                st.info("La tua rosa è vuota. Clicca sui tasti + nel listone sotto per comprare.")

            st.write("---")
            st.write("### 📋 Listone Diviso per Ruoli")

            tab_p, tab_d, tab_c, tab_a = st.tabs(["🧤 Portieri", "🛡️ Difensori", "🪄 Centrocampisti", "🏹 Attaccanti"])
            ruoli_mappa = {"🧤 Portieri": "Portiere", "🛡️ Difensori": "Difensore", "🪄 Centrocampisti": "Centrocampista", "🏹 Attaccanti": "Attaccante"}

            for tab_attivato, ruolo_stringa in ruoli_mappa.items():
                with tab_attivato:
                    df_filtrato = df_calciatori[df_calciatori['Ruolo'] == ruolo_stringa]
                    for index, row in df_filtrato.iterrows():
                        nome_c = row['Nome']
                        costo_c = row['Quotazione']
                        nazione_c = row['Nazione']
                        
                        col_info, col_costo, col_btn = st.columns([4, 1, 1])
                        col_info.write(f"**{nome_c}** ({nazione_c})")
                        col_costo.write(f"💰 {costo_c} CR")
                        
                        if nome_c in rosa_corrente:
                            col_btn.write("✅ In Rosa")
                        else:
                            if col_btn.button("➕", key=f"add_{nome_c}"):
                                if costo_c > rimanente:
                                    st.error("Crediti insufficienti!")
                                else:
                                    st.session_state[f"rosa_{user_key}"].append(nome_c)
                                    st.rerun()
                                    
        with tab_campo:
            st.subheader("📋 Scegli gli 11 Titolari")
            rosa_disponibile = dati_squadre.get(user_key, [])
            
            if not rosa_disponibile:
                st.warning("Torna nel Tab del mercato e acquista dei calciatori prima di fare la formazione!")
            else:
                formazione_precedente = dati_formazioni.get(user_key, [])
                titolari = st.multiselect(
                    "Seleziona gli 11 titolari:",
                    options=rosa_disponibile,
                    default=[p for p in formazione_precedente if p in rosa_disponibile]
                )
                
                if len(titolari) > 11:
                    st.error("Errore: puoi schierare al massimo 11 giocatori!")
                else:
                    st.info(f"Selezionati: {len(titolari)} / 11")
                    if st.button("Invia Formazione Ufficiale"):
                        dati_formazioni[user_key] = titolari
                        salva_dati(FILE_FORMAZIONI, dati_formazioni)
                        st.success("Formazione schierata!")

    elif menu_utente == "📊 Classifica":
        st.header("📊 Classifica Generale della Lega")
        squadre_in_lega = {k.split("_")[1]: v for k, v in dati_squadre.items() if k.startswith(f"{lega_selezionata}_")}
        
        if squadre_in_lega:
            classifica_lista = []
            for fanta_allenatore, lista_giocatori in squadre_in_lega.items():
                punteggio_totale = 0
                giocatori_in_campo = dati_formazioni.get(f"{lega_selezionata}_{fanta_allenatore}", lista_giocatori)
                for g in giocatori_in_campo:
                    punteggio_totale += dati_voti.get(g, 0.0)
                classifica_lista.append({"Squadra": fanta_allenatore, "Punti": punteggio_totale})
            
            df_classifica = pd.DataFrame(classifica_lista).sort_values(by="Punti", ascending=False)
            st.dataframe(df_classifica, use_container_width=True)
        else:
            st.info("Nessun partecipante iscritto a questa lega.")