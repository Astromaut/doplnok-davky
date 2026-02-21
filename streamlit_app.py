"""
Doplnok davky pre UVN RK

(c) Radoslav Paučo
"""

import streamlit as st
import numpy as np

# -- Set page config
apptitle = 'Doplnok dávky'

st.set_page_config(page_title=apptitle, page_icon=":radioactive:")

# Title the app
st.title('Doplnok dávky rádioterapie :radioactive:')

st.sidebar.markdown("## Výber parametrov pre tumor/OARs:")

ab_tumor = st.sidebar.number_input("$\\alpha/\\beta~pre~tumor$", min_value=1, max_value=10, value=10)
ab_org = st.sidebar.number_input("$\\alpha/\\beta~pre~OAR$", min_value=1, max_value=10, value=3)
k = st.sidebar.number_input("$k~pre~tumor$", min_value=0.0, max_value=3.0, step=0.05, value=0.9,
                            help="Proliferačný parameter v Gy/d pre tumor. Pre OARs uvažujeme k=0.")
t_delay = st.sidebar.number_input("$t_{delay}$", min_value=0, max_value=100, value=28,
                            help="Čas od začiatku terapie kedy nastupuje akcelerovaná repopulácia v dňoch.")

st.sidebar.markdown("## Parametre predpísaného kurzu (ideál):")
frakcia_pk = st.sidebar.number_input("dávka na frakciu", min_value=1, max_value=10, value=2)
pocet_f_pk = st.sidebar.number_input("počet frakcií", min_value=1, max_value=50, value=27)
pocet_dni_pk = st.sidebar.number_input("počet dní kurzu", min_value=1, max_value=365, value=37,
                                       help="Ideálna dĺžka predpísanej rádioterapie bez prerušení v dňoch.")

st.markdown('####')

# predpisana BED na organy
bed_org_pk = pocet_f_pk * frakcia_pk * (1 + frakcia_pk/ab_org)

# predpisana BED na tumor
bed_tumor_pk = pocet_f_pk * frakcia_pk * (1 + frakcia_pk/ab_tumor) - k * (pocet_dni_pk - t_delay)

cols = st.columns(2)
with cols[0]:
    st.metric(label="Predpísaná tumor BED", value=f"{bed_tumor_pk:0.2f} Gy_{ab_tumor}")
with cols[1]:
    st.metric(label="Predpísaná OARs BED", value=f"{bed_org_pk:0.2f} Gy_{ab_org}")

st.markdown('####')

st.markdown("#### Parametre odžiareného kurzu (reál):")

cols = st.columns(2)
with cols[0]:
    pocet_f_pred_pauzou = st.number_input("počet frakcií pred pauzou", min_value=1, max_value=365, value=23)
with cols[1]:
    pocet_f_po_pauze = st.number_input("počet frakcií po pauze", min_value=1, max_value=50, value=4)

cols = st.columns(2)
with cols[0]:
    pocet_pridanych_f = st.number_input("počet pridaných frakcií", min_value=1, max_value=50, value=2)
with cols[1]:
    pocet_dni_rk = st.number_input("celkový počet dní kurzu", min_value=1, max_value=365, value=50)

cols = st.columns(2)
with cols[0]:
    tumor_control = st.number_input("tumor control %", min_value=0, max_value=100, value=100)
    tumor_control = tumor_control/100.0 # 1 <=> 100% prepisanej BED

bed_tumor_rk = bed_tumor_pk*tumor_control

# doplnok
bed_pred_pauzou_k0 = pocet_f_pred_pauzou * frakcia_pk * (1 + frakcia_pk/ab_tumor)
utlm = k * (pocet_dni_rk - t_delay)
c = bed_pred_pauzou_k0 - utlm - bed_tumor_rk
b = (pocet_f_po_pauze + pocet_pridanych_f)
a = (pocet_f_po_pauze + pocet_pridanych_f) / ab_tumor
doplnok_f = (-b + np.sqrt(b*b-4*a*c))/(2*a)

st.markdown('####')

# navysena BED na organy
bed_org_add = pocet_f_pred_pauzou * frakcia_pk * (1+frakcia_pk/ab_org) + (pocet_f_po_pauze + pocet_pridanych_f) * doplnok_f * (1+doplnok_f/ab_org)
bed_org_navyse_perc = ((bed_org_add/bed_org_pk)-1)*100

# kontrola znizenie BED na tumor
bed_tumor_ponize_perc = ((bed_tumor_rk/bed_tumor_pk)-1)*100

cols = st.columns(2)
with cols[0]:
    st.metric(label="Navýšenie frakcií a doplnok po pauze",value=f"{pocet_f_po_pauze} x {doplnok_f:0.2f} + {pocet_pridanych_f} x "
                                              f"{doplnok_f:0.2f} Gy")
with cols[1]:
    st.metric(label="Celková tumor BED",value=f"{bed_tumor_rk:0.2f} Gy_{ab_tumor}",
              delta=f"{bed_tumor_ponize_perc:0.1f}\%")

cols = st.columns(2)
with cols[1]:
    st.metric(label="Celková OARs BED",value=f"{bed_org_add:0.2f} Gy_{ab_org}",
              delta=f"+{bed_org_navyse_perc:0.1f}\%", delta_color="inverse")


st.markdown('#')
st.markdown('(c) Radoslav Paučo, ÚVN SNP Ružomberok FN, paucor@uvn.sk')
st.image("linac.jpg")