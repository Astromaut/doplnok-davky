"""
Doplnok dávky rádioterapie pre ÚVN SNP Ružomberok FN

(c) Radoslav Paučo 2026
"""

import streamlit as st
import numpy as np
import pandas as pd
from datetime import date, timedelta
import reporting

# Nastavenie stranky
# Pod doplnkom mame na mysli bud navysenie a/alebo pridanie frakcii po preruseni kurzu radioterapie
# aby sa dosiahla predpisana BED (TCP) na tumor
st.set_page_config(page_title='Doplnok dávky', page_icon=":radioactive:")
st.title('Doplnok dávky rádioterapie :radioactive:')

# Sidebar - vyber zakladnych parametrov
st.sidebar.markdown("## Výber parametrov pre tumor/OARs:")

ab_tumor = st.sidebar.number_input("$\\alpha/\\beta~pre~tumor$", min_value=0.1, max_value=20.0, value=10.0,
                                   step=0.1)
ab_org = st.sidebar.number_input("$\\alpha/\\beta~pre~OAR$", min_value=0.1, max_value=20.0, value=3.0, step=0.1)

k = st.sidebar.number_input("$k~pre~tumor$", min_value=0.0, max_value=3.0, step=0.05, value=0.9,
                            help="Útlm BED za deň (Gy/d) pre tumor v dôsledku repopulácie. Pre OARs uvažujeme k=0.")

t_delay = st.sidebar.number_input("$t_{delay}$", min_value=0, max_value=100, value=28,
                            help="Čas od začiatku terapie kedy nastupuje akcelerovaná repopulácia v dňoch. V prípade adjuvancie je dobré zvoliť 0.")

st.sidebar.markdown("## Parametre predpísaného kurzu (ideál):")

frakcia_pk = st.sidebar.number_input("dávka na frakciu", min_value=0.1, max_value=10.0, value=2.0, step=0.1)

pocet_f_pk = st.sidebar.number_input("počet frakcií", min_value=1, max_value=50, value=27)

pocet_dni_pk = st.sidebar.number_input("počet dní kurzu", min_value=1, max_value=365, value=37,
                                       help="Ideálna dĺžka predpísanej rádioterapie bez prerušení v dňoch.")

st.markdown('####')

# Vypocet BED pre OARs a tumor
# _pk znaci predpisany kurz, _rk znaci realny kurz
bed_org_pk = pocet_f_pk * frakcia_pk * (1 + frakcia_pk/ab_org)

# predpisana BED na tumor
if pocet_dni_pk > t_delay:
    bed_tumor_pk = pocet_f_pk * frakcia_pk * (1 + frakcia_pk/ab_tumor) - k * (pocet_dni_pk - t_delay)
else:
    bed_tumor_pk = pocet_f_pk * frakcia_pk * (1 + frakcia_pk / ab_tumor)

# Stredovy - hlavny panel
cols = st.columns(2)
with cols[0]:
    st.metric(label="Predpísaná tumor BED s repopuláciou", value=f"{bed_tumor_pk:0.2f} Gy_{ab_tumor}")
with cols[1]:
    st.metric(label="Predpísaná OARs BED", value=f"{bed_org_pk:0.2f} Gy_{ab_org}")

cols = st.columns(2)
with cols[0]:
    tumor_eqd2 = bed_tumor_pk/(1+2/ab_tumor)
    st.metric(label="Predpísaná tumor EQD2 s repopuláciou", value=f"{tumor_eqd2:0.2f} Gy")
with cols[1]:
    org_eqd2 = bed_org_pk/(1+2/ab_org)
    st.metric(label="Predpísaná OARs EQD2", value=f"{org_eqd2:0.2f} Gy")

st.markdown('####')

st.markdown("#### Parametre odžiareného kurzu (reál):")

# Parametre realneho kurzu
cez_datumy = st.checkbox("Zaklikni, ak chceš zadať dĺžku kurzu podľa kalendára.")
if cez_datumy:
    cols = st.columns(2)
    with cols[0]:
        start_date = st.date_input('dátum zahájenia rádioterapie', date(2025, 11, 26))
    with cols[1]:
        end_date = st.date_input('dátum ukončenia rádioterapie', date(2026, 1, 14))
    pocet_dni_rk = (end_date - start_date + timedelta(days=1)).days

    cols = st.columns(2)
    with cols[0]:
        pocet_f_pred_pauzou = st.number_input("počet odžiarených frakcií", min_value=1, max_value=365, value=23,
                                              help="Počet frakcií, ktoré boli odžiarené a už ich nie je možné navýšiť.")
    with cols[1]:
        pocet_f_po_pauze = st.number_input("počet frakcií, kt. chceme navýšiť", min_value=0, max_value=50, value=4,
                                           help="Počet frakcií na konci predpísaného kurzu, ktoré chceme navýšiť.")

    cols = st.columns(2)
    with cols[0]:
        pocet_pridanych_f = st.number_input("počet pridaných extra frakcií", min_value=0, max_value=50, value=2,
                                            help="Počet frakcií, ktoré chceme pridať extra po dožiarení pôvodného " \
                                            "kurzu (s navýšenými frakciami).")
    with cols[1]:
        tumor_control = st.number_input("% predpísanej BED", min_value=0.1, max_value=100.0, value=100.0, step=0.1)
        tumor_control = tumor_control / 100.0  # 1 <=> 100% prepisanej BED
else:
    cols = st.columns(2)
    with cols[0]:
        pocet_f_pred_pauzou = st.number_input("počet odžiarených frakcií", min_value=1, max_value=365, value=23,
                                              help="Počet frakcií, ktoré boli odžiarené a už ich nie je možné navýšiť.")
    with cols[1]:
        pocet_f_po_pauze = st.number_input("počet frakcií, kt. chceme navýšiť", min_value=0, max_value=50, value=4,
                                           help="Počet frakcií na konci predpísaného kurzu, ktoré chceme navýšiť.")

    cols = st.columns(2)
    with cols[0]:
        pocet_pridanych_f = st.number_input("počet pridaných extra frakcií", min_value=0, max_value=50, value=2,
                                            help="Počet frakcií, ktoré chceme pridať extra po dožiarení pôvodného " \
                                            "kurzu (s navýšenými frakciami).")
    with cols[1]:
        pocet_dni_rk = st.number_input("celkový počet dní kurzu", min_value=1, max_value=365, value=50,
                                        help="Celkový počet dní reálneho kurzu rádioterapie, vrátane prerušení a extra dní "
                                        "kvôli extra frakciám.")

    cols = st.columns(2)
    with cols[0]:
        tumor_control = st.number_input("% predpísanej BED", min_value=0.1, max_value=100.0, value=100.0, step=0.1,
                                        help="Percento pôvodne predpísanej BED, ktoré chceme dosiahnuť na tumor. " \
                                        "Tu vieme vybalansovať navýšenie BED na tumor vs. OARs.")
        tumor_control = tumor_control / 100.0  # 1 <=> 100% prepisanej BED

# Sidebar - volitelne parametre pre vypocet TCP
tcp_on = st.checkbox("Zaklikni, ak chceš spočítať aj zmenu Tumor Control Probability TCP. Vyžaduje zadať " \
                     "referenčné TCP pôvodne zamýšľaného kurzu a parameter $\\alpha$ pre tumor v ľavom stĺpci dole.")

a_tumor = None
tcp_pk = None
if tcp_on:
    st.sidebar.markdown("## Výber prídavných parametrov pre výpočet TCP:")
    a_tumor = st.sidebar.number_input("$\\alpha~pre~tumor$", min_value=0.1, max_value=5.0, value=0.3, step=0.01)
    tcp_pk= st.sidebar.number_input("$ref.~TCP~pôvodného~kurzu$", min_value=0.01, max_value=0.99, value=0.90, step=0.01)

st.sidebar.markdown("##")

# Sidebar - link na navod
st.sidebar.link_button(
    "Návod na použitie", "https://docs.google.com/document/d/1n_Z8EeC6_0RDR-sbpcFmgmya2mYR6AAW/edit?usp=sharing&ouid=109514329545120121337&rtpof=true&sd=true"
)

# Osetrenie nefyzikalnych vstupov 
if pocet_f_po_pauze == 0 and pocet_pridanych_f == 0:
    # ak su obe hodnoty parametrov nula, nastavime 1 pridanu frakciu
    pocet_pridanych_f = 1
    st.warning(
        "Obe hodnoty parametrov - počet frakcií, kt. chceme navýšiť a počet pridaných frakcií - boli nula. " \
        "Automaticky som nastavil 1 pridanú extra frakciu, aby sa mohol vypočítať doplnok."
    )

if pocet_f_pred_pauzou + pocet_f_po_pauze != pocet_f_pk:
    st.warning(
        "Počet odžiarených frakcií + počet frakcií, kt. chceme navýšiť, sa musí rovnať počtu frakcií " \
        "predpísaného kurzu. Skontrolujte zadané parametre."
    )

if pocet_dni_rk <= pocet_dni_pk:
    st.warning(
        "Celkový počet dní reálneho kurzu je menší alebo rovný počtu dní predpísaného kurzu. " \
        "Skontrolujte zadané parametre."
    )

if pocet_f_pk > pocet_dni_pk:
    st.warning(
        "Počet frakcií predpísaného kurzu je väčší ako počet dní predpísaného kurzu. " \
        "Program momentálne neumožňuje prípad viac frakcií za deň. Skontrolujte zadané parametre."
    )

if t_delay > pocet_dni_rk:
    st.warning(
        "Čas od začiatku terapie do nástupu akcelerovanej repopulácie je menší ako celkový počet dní reálneho kurzu. " \
        "Skontrolujte zadané parametre."
    )

# Vypocet doplnku
bed_tumor_rk = bed_tumor_pk*tumor_control

bed_pred_pauzou_k0 = pocet_f_pred_pauzou * frakcia_pk * (1 + frakcia_pk / ab_tumor)
repopulacia_dni = max(0.0, pocet_dni_rk - t_delay)
utlm = k * repopulacia_dni if pocet_dni_rk > t_delay else 0.0

zostavajuce_f = pocet_f_po_pauze + pocet_pridanych_f
c = bed_pred_pauzou_k0 - utlm - bed_tumor_rk
b = zostavajuce_f
a = zostavajuce_f / ab_tumor
discriminant = b * b - 4 * a * c

if discriminant < 0:
    doplnok_f = 0.0
    st.warning(
        "Zvolené parametre nie sú fyzikálne alebo inak nedávajú zmysel." \
        "Skontrolujte zadané parametre."
    )

else:
    doplnok_f = (-b + np.sqrt(discriminant)) / (2*a)

if np.isnan(doplnok_f):
    doplnok_f = 0.0

# Klinicke pravidlo: ak je vypocitana (rovnomerna) kompenzacia mensia
# ako povodne predpisana frakcia, nechame zostavajuce frakcie po pauze 
# nezmenene a pracujeme len s pridanymi frakciami
pridanie = doplnok_f
if doplnok_f > 0 and doplnok_f < frakcia_pk and pocet_pridanych_f > 0:
    zvysok = frakcia_pk - doplnok_f
    pridanie = doplnok_f - (pocet_f_po_pauze * zvysok) / pocet_pridanych_f
    doplnok_f = frakcia_pk

st.markdown('####')

# navysena BED na organy
bed_org_add = (pocet_f_pred_pauzou * frakcia_pk * (1+frakcia_pk/ab_org) + pocet_f_po_pauze *
               doplnok_f * (1+doplnok_f/ab_org) + pocet_pridanych_f * pridanie * (1+pridanie/ab_org))
bed_org_navyse_perc = ((bed_org_add/bed_org_pk)-1)*100

# kontrola znizenie BED na tumor
bed_tumor_ponize_perc = ((bed_tumor_rk/bed_tumor_pk)-1)*100

# Vypocet znizeneho TCP
# tu bude samotny vypocet povodne TCP - nove TCP ako pokles
tcp_rk = None
tcp_rk_perc = None
if tcp_on:
    delta_bed = bed_tumor_pk - bed_tumor_rk
    tcp_rk = tcp_pk**(np.exp(a_tumor * delta_bed))
    tcp_rk_perc = ((tcp_rk/tcp_pk)-1)*100

# Stredovy panel - prezentacia vysledkov
cols = st.columns(2)
with cols[0]:
    st.metric(label="Navýšenie a pridanie frakcií", value=f"{pocet_f_po_pauze} x {doplnok_f:0.2f} + "
                                                                  f"{pocet_pridanych_f} x {pridanie:0.2f} Gy",
              border=True,
              icon=":material/add_task:")
    with cols[1]:
        st.metric(label="Počet dní reálneho kurzu rádioterapie", value=pocet_dni_rk,
                  delta=f"{((pocet_dni_rk/pocet_dni_pk)-1)*100:0.1f}\%", delta_color="inverse")
        
cols = st.columns(2)
if tcp_on:
    with cols[0]:
        st.metric(label="TCP s manažmentom prerušení", 
                  value=f"{tcp_rk:0.2f}",
                  delta=f"{tcp_rk_perc:0.1f}\%")
    with cols[1]:
        bed_tumor_rk_bezm = pocet_f_pk * frakcia_pk * (1 + frakcia_pk/ab_tumor) - k * (pocet_dni_rk - pocet_pridanych_f 
                                                                                       - t_delay)
        delta_bed_bezm = bed_tumor_pk - bed_tumor_rk_bezm
        tcp_rk_bezm = tcp_pk**(np.exp(a_tumor * delta_bed_bezm))
        tcp_rk_bezm_perc = ((tcp_rk_bezm /tcp_pk)-1)*100
        st.metric(label="TCP bez manažmentu prerušení",
                  value=f"{tcp_rk_bezm:0.2f}",
                  delta=f"{tcp_rk_bezm_perc:0.1f}\%")

cols = st.columns(2)
with cols[0]:
    st.metric(label="Tumor BED s manažmentom prerušení", value=f"{bed_tumor_rk:0.2f} Gy_{ab_tumor}",
              delta=f"{bed_tumor_ponize_perc:0.1f}\%")
with cols[1]:
    bed_tumor_rk_bezm = pocet_f_pk * frakcia_pk * (1 + frakcia_pk/ab_tumor) - k * (pocet_dni_rk - pocet_pridanych_f
                                                                                   - t_delay)
    bed_tumor_ponize_bezm_perc = ((bed_tumor_rk_bezm/bed_tumor_pk)-1)*100
    st.metric(label="Tumor BED bez manažmentu prerušení", value=f"{bed_tumor_rk_bezm:0.2f} Gy_{ab_tumor}",
              delta=f"{bed_tumor_ponize_bezm_perc:0.1f}\%", help="Pre presný výpočet tejto metriky nastav " \
              "$počet~pridaných~frakcií$ na 0 a $celkový~počet~dní~kurzu$ na reálny počet dní za ktorý (by) " \
              "bol pôvodný predpísaný kurz odžiarený, inak útlm dávky defaultne ráta s hodnotou " \
              "$celkový~počet~dní~kurzu - počet~pridaných~frakcií$. Toto je dôležité pri prídavkoch, " \
              "ktoré zasahujú do viacerých pracovných týždňov.")

cols = st.columns(2)
with cols[0]:
    st.metric(label="OARs BED s manažmentom prerušení", value=f"{bed_org_add:0.2f} Gy_{ab_org}",
              delta=f"+{bed_org_navyse_perc:0.1f}\%", delta_color="inverse")
with cols[1]:
    eqd2_org_add = bed_org_add/(1+2/ab_org)
    eqd2_org_navyse_perc = ((eqd2_org_add/org_eqd2)-1)*100
    st.metric(label="OARs EQD2 s manažmentom prerušení", value=f"{eqd2_org_add :0.2f} Gy",
              delta=f"+{eqd2_org_navyse_perc:0.1f}\%", delta_color="inverse", border=True,
              icon=":material/cardio_load:")

# Reporting
st.markdown('####')

if st.button("Generuj report do PDF"):
    report_data = {
        "title": "Doplnok dávky rádioterapie",
        "ab_tumor": ab_tumor,
        "a_tumor": a_tumor,
        "ref_tcp": tcp_pk,
        "ab_org": ab_org,
        "k": k,
        "t_delay": t_delay,
        "frakcia_pk": frakcia_pk,
        "pocet_f_pk": pocet_f_pk,
        "pocet_dni_pk": pocet_dni_pk,
        "pocet_f_pred_pauzou": pocet_f_pred_pauzou,
        "pocet_f_po_pauze": pocet_f_po_pauze,
        "pocet_pridanych_f": pocet_pridanych_f,
        "pocet_dni_rk": pocet_dni_rk,
        "bed_tumor_pk": bed_tumor_pk,
        "bed_org_pk": bed_org_pk,
        "bed_tumor_rk": bed_tumor_rk,
        "bed_org_add": bed_org_add,
        "bed_org_navyse_perc": bed_org_navyse_perc,
        "bed_tumor_ponize_perc": bed_tumor_ponize_perc,
        "eqd2_org_add": eqd2_org_add,
        "eqd2_org_add_perc": eqd2_org_navyse_perc,
        "combo_summary": f"{pocet_f_po_pauze} x {doplnok_f:.2f} + {pocet_pridanych_f} x {pridanie:.2f} Gy",
        "tcp_rk": tcp_rk,
        "tcp_rk_perc": tcp_rk_perc
    }

    pdf_bytes = reporting.export_report_pdf_reportlab(tcp_on, report_data)

    st.download_button(
        label="Stiahnuť PDF report",
        data=pdf_bytes,
        file_name="radiotherapy_report.pdf",
        mime="application/pdf",
    )

# Paticka - copyright
st.markdown('#')
st.markdown('(c) Radoslav Paučo, ÚVN SNP Ružomberok FN, paucor@uvn.sk')
st.image("linac.jpg")
