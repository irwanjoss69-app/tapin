import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import google.generativeai as genai

# --- CONFIGURASI PRO ---
st.set_page_config(page_title="TAPIN SYSTEM v1.0", layout="wide", initial_sidebar_state="expanded")

# Gaya CSS agar tampilan tidak seperti web (menghilangkan spasi kosong & mempercantik tabel)
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    [data-testid="stSidebar"] { background-color: #1e2d3b; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI INTI ---
def get_connection():
    return sqlite3.connect("tapin.db")

# --- KEAMANAN LOGIN ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.write("# 🖥️ LOGIN SYSTEM")
        with st.container(border=True):
            user = st.text_input("USER ID")
            pw = st.text_input("PASSWORD", type="password")
            if st.button("LOGIN"):
                if user == "admin" and pw == "selawe25":
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Akses Ditolak!")
    st.stop()

# --- HEADER APLIKASI ---
col_l, col_r = st.columns([1, 4])
with col_l:
    # Jika Bapak punya file logo.png, pastikan ada di folder yang sama
    try: st.image("logo.png", width=100)
    except: st.write("Logo Belum Ada")
with col_r:
    st.title("SISTEM INFORMASI TABUNGAN - TAPIN")
    st.write(f"MIM SELAWE | Operator: Admin | {datetime.now().strftime('%d/%m/%Y')}")

st.divider()

# --- MENU SAMPING (SIDEBAR) ---
with st.sidebar:
    st.write("### 🧭 NAVIGATION")
    menu = st.radio("Menu Utama", ["DASHBOARD", "MASTER SISWA", "TRANSAKSI KASIR", "BANK SOAL AI", "LAPORAN"])
    if st.button("LOGOUT"):
        st.session_state.auth = False
        st.rerun()

conn = get_connection()

if menu == "DASHBOARD":
    st.subheader("📋 Ringkasan Statistik")
    c1, c2, c3, c4 = st.columns(4)
    df_trx = pd.read_sql("SELECT * FROM transaksi", conn)
    
    total_setor = df_trx[df_trx['jenis']=='SETOR']['jumlah'].sum()
    total_tarik = df_trx[df_trx['jenis']=='TARIK']['jumlah'].sum()
    
    c1.metric("TOTAL SIMPANAN", f"Rp {total_setor:,.0f}")
    c2.metric("TOTAL PENARIKAN", f"Rp {total_tarik:,.0f}")
    c3.metric("SALDO NETTO", f"Rp {total_setor - total_tarik:,.0f}")
    c4.metric("TOTAL TRANSAKSI", f"{len(df_trx)} Data")
    
    st.write("### 📈 Grafik Arus Kas")
    st.area_chart(df_trx.groupby('tanggal')['jumlah'].sum())

elif menu == "TRANSAKSI KASIR":
    st.subheader("🛒 Input Transaksi Layaknya Swalayan")
    col_a, col_b = st.columns([2, 1])
    
    with col_a:
        with st.container(border=True):
            df_s = pd.read_sql("SELECT no_rekening, nama FROM siswa", conn)
            pilih_siswa = st.selectbox("CARI NASABAH", df_s['no_rekening'] + " - " + df_s['nama'])
            rek = pilih_siswa.split(" - ")[0]
            
            col_in1, col_in2 = st.columns(2)
            tipe = col_in1.selectbox("AKSI", ["SETOR", "TARIK"])
            nominal = col_in2.number_input("NOMINAL (RP)", min_value=0, step=1000)
            
            if st.button("PROSES TRANSAKSI"):
                cursor = conn.cursor()
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("INSERT INTO transaksi (no_rekening, jenis, jumlah, tanggal) VALUES (?,?,?,?)", 
                               (rek, tipe, nominal, now))
                conn.commit()
                st.success("Transaksi Berhasil Dicatat!")

    with col_b:
        st.info("💡 Tips: Pastikan saldo mencukupi sebelum melakukan penarikan.")

elif menu == "BANK SOAL AI":
    st.subheader("🤖 Generator Soal Ujian Pro")
    os_api_key = "AIzaSyCsvfBo9HndeuVc3Mkbm6boCEERVIW5G-8"
    genai.configure(api_key=os_api_key)
    ai_model = genai.GenerativeModel('gemini-pro')
    
    with st.container(border=True):
        mapel = st.text_input("Mata Pelajaran & Materi")
        jml = st.select_slider("Jumlah Soal", options=[5, 10, 15, 20])
        if st.button("GENERATE"):
            with st.spinner("Menyusun database soal..."):
                res = ai_model.generate_content(f"Buat {jml} soal PG {mapel} untuk Madrasah Ibtidaiyah.")
                st.text_area("Hasil Soal:", res.text, height=400)

elif menu == "MASTER SISWA":
    st.subheader("👥 Database Nasabah")
    df_siswa = pd.read_sql("SELECT * FROM siswa", conn)
    # Filter pencarian pro
    cari = st.text_input("Cari Nama atau No Rekening")
    if cari:
        df_siswa = df_siswa[df_siswa['nama'].str.contains(cari, case=False) | df_siswa['no_rekening'].str.contains(cari)]
    st.dataframe(df_siswa, use_container_width=True, hide_index=True)
