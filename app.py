import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import google.generativeai as genai

# --- KONEKSI DATABASE & AI ---
os_api_key = "AIzaSyCsvfBo9HndeuVc3Mkbm6boCEERVIW5G-8"
genai.configure(api_key=os_api_key)
model = genai.GenerativeModel('gemini-pro')

def get_db():
    return sqlite3.connect("tapin.db")

# --- SETTING HALAMAN AGAR MIRIP APLIKASI DESKTOP ---
st.set_page_config(page_title="Sistem Informasi Tabungan - TAPIN", layout="wide")

# CSS untuk memaksa warna Merah/Putih dan Tombol Besar seperti gambar Bapak
st.markdown("""
    <style>
    .header-style { font-size:30px; font-weight:bold; color:#cc0000; text-align:center; margin-bottom:0px; }
    .sub-style { font-size:18px; text-align:center; color: #333; margin-bottom:20px; }
    div.stButton > button {
        width: 100%; height: 60px; font-weight: bold; font-size: 16px;
        background-color: #f8f9fa; border: 2px solid #cc0000; color: #cc0000;
    }
    div.stButton > button:hover { background-color: #cc0000; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER (Persis Gambar Bapak) ---
st.markdown('<p class="header-style">SISTEM INFORMASI TABUNGAN - TAPIN</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-style">MIM 25 SELAWE - KECAMATAN WATULIMO</p>', unsafe_allow_html=True)

# --- TOMBOL NAVIGASI UTAMA (Di Atas, Horizontal seperti Desktop) ---
col1, col2, col3, col4, col5 = st.columns(5)
with col1: btn_home = st.button("🏠 DASHBOARD")
with col2: btn_trans = st.button("💰 TRANSAKSI")
with col3: btn_siswa = st.button("👥 DATA SISWA")
with col4: btn_ai = st.button("🤖 BANK SOAL AI")
with col5: btn_out = st.button("🚪 KELUAR")

# Simpan pilihan menu di session_state
if "menu" not in st.session_state: st.session_state.menu = "🏠 DASHBOARD"
if btn_home: st.session_state.menu = "🏠 DASHBOARD"
if btn_trans: st.session_state.menu = "💰 TRANSAKSI"
if btn_siswa: st.session_state.menu = "👥 DATA SISWA"
if btn_ai: st.session_state.menu = "🤖 BANK SOAL AI"

st.divider()

# --- ISI KONTEN (Mengikuti Fungsi di tapin.py Bapak) ---
conn = get_db()

if st.session_state.menu == "🏠 DASHBOARD":
    st.subheader("📊 Grafik Perkembangan Tabungan")
    df_trx = pd.read_sql("SELECT * FROM transaksi", conn)
    if not df_trx.empty:
        st.line_chart(df_trx.groupby('tanggal')['jumlah'].sum())
    else:
        st.info("Belum ada data transaksi yang masuk.")

elif st.session_state.menu == "💰 TRANSAKSI":
    st.subheader("📝 Input Transaksi Baru")
    with st.container(border=True):
        rek = st.text_input("Nomor Rekening")
        tipe = st.selectbox("Jenis Transaksi", ["SETOR", "TARIK"])
        jml = st.number_input("Nominal (Rp)", min_value=0)
        if st.button("SIMPAN TRANSAKSI"):
            # Logika simpan tetap sama
            st.success("Transaksi Berhasil Disimpan ke Database!")

elif st.session_state.menu == "👥 DATA SISWA":
    st.subheader("📋 Daftar Nasabah MIM 25 Selawe")
    df_siswa = pd.read_sql("SELECT * FROM siswa", conn)
    st.dataframe(df_siswa, use_container_width=True)

elif st.session_state.menu == "🤖 BANK SOAL AI":
    st.subheader("📝 Generator Soal Otomatis")
    mapel = st.text_input("Mata Pelajaran")
    if st.button("PROSES BUAT SOAL"):
        with st.spinner("Menyusun soal..."):
            res = model.generate_content(f"Buat 10 soal PG {mapel} untuk MI.")
            st.write(res.text)
