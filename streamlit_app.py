"""
Doplnok dávky rádioterapie pre ÚVN Ružomberok

(c) Radoslav Paučo
"""

import streamlit as st
import numpy as np
import pandas as pd
from datetime import date, timedelta

st.set_page_config(page_title='Doplnok dávky', page_icon=":radioactive:")
st.title('Doplnok dávky rádioterapie :radioactive:')

st.sidebar.markdown("## Výber parametrov pre tumor/OARs:")

ab_tumor = st.sidebar.number_input("$\\alpha/\\beta~pre~tumor$", min_value=0.1, max_value=20.0, value=10.0,
                                   step=0.1)
ab_org = st.sidebar.number_input("$\\alpha/\\beta~pre~OAR$", min_value=0.1, max_value=20.0, value=3.0, step=0.1)

k = st.sidebar.number_input("$k~pre~tumor$", min_value=0.0, max_value=3.0, step=0.05, value=0.9,
                            help="Útlm BED za deň (Gy/d) pre tumor v dôsledku repopulácie. Pre OARs uvažujeme k=0.")

t_delay = st.sidebar.number_input("$t_{delay}$", min_value=0, max_value=100, value=28,
                            help="Čas od začiatku terapie kedy nastupuje akcelerovaná repopulácia v dňoch.")

st.sidebar.markdown("## Parametre predpísaného kurzu (ideál):")

frakcia_pk = st.sidebar.number_input("dávka na frakciu", min_value=1, max_value=10, value=2)

pocet_f_pk = st.sidebar.number_input("počet frakcií", min_value=1, max_value=50, value=27)

pocet_dni_pk = st.sidebar.number_input("počet dní kurzu", min_value=1, max_value=365, value=37,
                                       help="Ideálna dĺžka predpísanej rádioterapie bez prerušení v dňoch.")

st.markdown('####')

# predpisana BED na organy (_pk znaci predpisany kurz, _rk znaci realny kurz)
bed_org_pk = pocet_f_pk * frakcia_pk * (1 + frakcia_pk/ab_org)

# predpisana BED na tumor
if pocet_dni_pk > t_delay:
    bed_tumor_pk = pocet_f_pk * frakcia_pk * (1 + frakcia_pk/ab_tumor) - k * (pocet_dni_pk - t_delay)
else:
    bed_tumor_pk = pocet_f_pk * frakcia_pk * (1 + frakcia_pk / ab_tumor)

cols = st.columns(2)
with cols[0]:
    st.metric(label="Predpísaná tumor BED", value=f"{bed_tumor_pk:0.2f} Gy_{ab_tumor}")
with cols[1]:
    st.metric(label="Predpísaná OARs BED", value=f"{bed_org_pk:0.2f} Gy_{ab_org}")

st.markdown('####')

st.markdown("#### Parametre odžiareného kurzu (reál):")

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
        pocet_f_pred_pauzou = st.number_input("počet frakcií pred pauzou", min_value=1, max_value=365, value=23)
    with cols[1]:
        pocet_f_po_pauze = st.number_input("počet frakcií po pauze", min_value=0, max_value=50, value=4)

    cols = st.columns(2)
    with cols[0]:
        pocet_pridanych_f = st.number_input("počet pridaných frakcií", min_value=0, max_value=50, value=2)
    with cols[1]:
        tumor_control = st.number_input("tumor control %", min_value=0.1, max_value=100.0, value=100.0, step=0.1)
        tumor_control = tumor_control / 100.0  # 1 <=> 100% prepisanej BED
else:
    cols = st.columns(2)
    with cols[0]:
        pocet_f_pred_pauzou = st.number_input("počet frakcií pred pauzou", min_value=1, max_value=365, value=23)
    with cols[1]:
        pocet_f_po_pauze = st.number_input("počet frakcií po pauze", min_value=0, max_value=50, value=4)

    cols = st.columns(2)
    with cols[0]:
        pocet_pridanych_f = st.number_input("počet pridaných frakcií", min_value=0, max_value=50, value=2)
    with cols[1]:
        pocet_dni_rk = st.number_input("celkový počet dní kurzu", min_value=1, max_value=365, value=50)

    cols = st.columns(2)
    with cols[0]:
        tumor_control = st.number_input("tumor control %", min_value=0.1, max_value=100.0, value=100.0, step=0.1)
        tumor_control = tumor_control / 100.0  # 1 <=> 100% prepisanej BED

bed_tumor_rk = bed_tumor_pk*tumor_control

# Vypocet navysenia doplnku
bed_pred_pauzou_k0 = pocet_f_pred_pauzou * frakcia_pk * (1 + frakcia_pk/ab_tumor)
if pocet_dni_rk > t_delay:
    utlm = k * (pocet_dni_rk - t_delay)
else:
    utlm = 0.0
c = bed_pred_pauzou_k0 - utlm - bed_tumor_rk
b = (pocet_f_po_pauze + pocet_pridanych_f)
a = (pocet_f_po_pauze + pocet_pridanych_f) / ab_tumor
doplnok_f = (-b + np.sqrt(b*b-4*a*c))/(2*a)

if np.isnan(doplnok_f):
    doplnok_f = 0

st.markdown('####')

# navysena BED na organy
bed_org_add = (pocet_f_pred_pauzou * frakcia_pk * (1+frakcia_pk/ab_org) + (pocet_f_po_pauze + pocet_pridanych_f) *
               doplnok_f * (1+doplnok_f/ab_org))
bed_org_navyse_perc = ((bed_org_add/bed_org_pk)-1)*100

# kontrola znizenie BED na tumor
bed_tumor_ponize_perc = ((bed_tumor_rk/bed_tumor_pk)-1)*100

cols = st.columns(2)
with cols[0]:
    st.metric(label="Navýšenie frakcií a doplnok po pauze", value=f"{pocet_f_po_pauze} x {doplnok_f:0.2f} + "
                                                                 f"{pocet_pridanych_f} x {doplnok_f:0.2f} Gy")
with cols[1]:
    st.metric(label="Počet dní reálneho kurzu rádioterapie", value=pocet_dni_rk,
              delta=f"{((pocet_dni_rk/pocet_dni_pk)-1)*100:0.1f}\%", delta_color="inverse")

cols = st.columns(2)
with cols[0]:
    st.metric(label="Tumor BED s manažmentom prerušení", value=f"{bed_tumor_rk:0.2f} Gy_{ab_tumor}",
              delta=f"{bed_tumor_ponize_perc:0.1f}\%")
with cols[1]:
    bed_tumor_rk_bezm = pocet_f_pk * frakcia_pk * (1 + frakcia_pk/ab_tumor) - k * (pocet_dni_rk - pocet_pridanych_f
                                                                                   - t_delay)
    bed_tumor_ponize_bezm_perc = ((bed_tumor_rk_bezm/bed_tumor_pk)-1)*100
    st.metric(label="Tumor BED bez manažmentu prerušení", value=f"{bed_tumor_rk_bezm:0.2f} Gy_{ab_tumor}",
              delta=f"{bed_tumor_ponize_bezm_perc:0.1f}\%", help="Pre presný výpočet tejto metriky nastav $počet~pridaných~frakcií$ na 0 a $celkový~počet~dní~kurzu$ na reálny počet dní za ktorý (by) bol pôvodný predpísaný kurz odžiarený, " \
              "inak útlm dávky defaultne ráta s hodnotou $celkový~počet~dní~kurzu - počet~pridaných~frakcií$. Toto je dôležité pri prídavkoch, ktoré zasahujú do viacerých pracovných týždňov.")

cols = st.columns(2)
with cols[0]:
    st.metric(label="OARs BED s manažmentom prerušení", value=f"{bed_org_add:0.2f} Gy_{ab_org}",
              delta=f"+{bed_org_navyse_perc:0.1f}\%", delta_color="inverse")

st.markdown('#')
pomocka = st.checkbox("Pomôcka: zaklikni, ak chceš vidieť prehľad parametrov tumorov z literatúry. Vzťah medzi "
                      "$k$ a $D_{prolif}$: $k=D_{prolif}(1 + d/(\\alpha/\\beta))$, kde $d$ je veľkosť referenčnej "
                      "frakcie.")

if pomocka:
    ab_params = pd.read_csv("ab_params.csv", sep=";", dtype=str)
    ab_params = ab_params.rename(columns={"ab": "$\\alpha/\\beta$ (Gy)",
                                          "ab-rozsah": "95% CL pre $\\alpha/\\beta$ (Gy)",
                                          "ref": "referencia"})

    st.table(ab_params)

    prolif_params = pd.read_csv("prolif_params.csv", sep=";", dtype=str)
    prolif_params = prolif_params.rename(columns={"dprolif": "$D_{prolif}$ (Gy/d)",
                                                  "dprolif-rozsah": "95% CL pre $D_{prolif}$ (Gy/d)",
                                                  "tdelay": "$t_{delay}$ (d)",
                                                  "ref": "referencia"})

    st.table(prolif_params)

st.markdown('#')
st.markdown('(c) Radoslav Paučo, ÚVN SNP Ružomberok FN, paucor@uvn.sk')
st.image("linac.jpg")
