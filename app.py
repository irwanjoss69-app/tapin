import streamlit as st
import sqlite3
import pandas as pd
import datetime
from google import genai

# --- 1. KONFIGURASI AI (Pakai API Key Bapak) ---
client = genai.Client(api_key="AIzaSyCsvfBo9HndeuVc3Mkbm6boCEERVIW5G-8")

# --- 2. FUNGSI DATABASE (Diambil dari Rumus Bapak) ---
def init_db():
    conn = sqlite3.connect("tapin_online.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS siswa(no_rekening TEXT PRIMARY KEY, nama TEXT, alamat TEXT, no_hp TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS transaksi(no_trx TEXT PRIMARY KEY, no_rekening TEXT, jenis TEXT, jumlah INTEGER, tanggal TEXT, petugas TEXT)")
    conn.commit()
    return conn

def format_rp(angka):
    return f"Rp {angka:,.0f}".replace(",", ".")

# --- 3. TAMPILAN WEB (STREAMLIT) ---
st.set_page_config(page_title="TAPIN Online", layout="wide")

# Menu Samping (Sidebar)
with st.sidebar:
    st.title("💰 TAPIN ONLINE")
    st.write("MIM 25 SELAWE")
    menu = st.radio("Menu Utama:", ["Dashboard & Grafik", "Input Transaksi", "Bank Soal AI", "Data Siswa"])

conn = init_db()

# --- HALAMAN 1: DASHBOARD ---
if menu == "Dashboard & Grafik":
    st.header("📊 Ringkasan Tabungan")
    df_trx = pd.read_sql("SELECT * FROM transaksi", conn)
    
    if not df_trx.empty:
        total_saldo = df_trx[df_trx['jenis'] == 'SETOR']['jumlah'].sum() - df_trx[df_trx['jenis'] == 'TARIK']['jumlah'].sum()
        st.metric("Total Saldo Sekolah", format_rp(total_saldo))
        
        # Grafik Perjalanan Tabungan (Render Polygon Data)
        st.subheader("📈 Tren Setoran")
        df_trx['tanggal'] = pd.to_datetime(df_trx['tanggal'])
        chart_data = df_trx.groupby('tanggal')['jumlah'].sum()
        st.line_chart(chart_data)
    else:
        st.info("Belum ada data transaksi.")

# --- HALAMAN 2: INPUT TRANSAKSI (Bisa dari HP) ---
elif menu == "Input Transaksi":
    st.header("📝 Input Setor/Tarik")
    df_siswa = pd.read_sql("SELECT no_rekening, nama FROM siswa", conn)
    
    if not df_siswa.empty:
        opsi_siswa = df_siswa.apply(lambda x: f"{x['no_rekening']} - {x['nama']}", axis=1)
        pilihan = st.selectbox("Pilih Siswa:", opsi_siswa)
        rek = pilihan.split(" - ")[0]
        
        jenis = st.selectbox("Jenis Transaksi:", ["SETOR", "TARIK"])
        nominal = st.number_input("Nominal (Rp):", min_value=0, step=1000)
        
        if st.button("Simpan Transaksi"):
            tgl = datetime.datetime.now().strftime('%Y-%m-%d')
            no_nota = f"TRX-{datetime.datetime.now().strftime('%H%M%S')}"
            c = conn.cursor()
            c.execute("INSERT INTO transaksi VALUES (?,?,?,?,?,?)", 
                      (no_nota, rek, jenis, nominal, tgl, "Admin-HP"))
            conn.commit()
            st.success(f"Berhasil simpan {jenis} sebesar {format_rp(nominal)}")
    else:
        st.warning("Data siswa kosong. Silakan isi di menu Data Siswa.")

# --- HALAMAN 3: BANK SOAL AI (Rumus Bapak) ---
elif menu == "Bank Soal AI":
    st.header("📝 Bank Soal MIM Selawe")
    mapel = st.selectbox("Mata Pelajaran:", ["Matematika", "Bahasa Arab", "IPA", "Al-Islam"])
    kelas = st.selectbox("Kelas:", ["Kelas 1", "Kelas 2", "Kelas 3", "Kelas 4", "Kelas 5", "Kelas 6"])
    
    if st.button("🚀 Generate Soal via Gemini"):
        with st.spinner("Sedang meracik soal..."):
            prompt = f"Buatkan 5 soal pilihan ganda {mapel} untuk {kelas} MI beserta kunci jawabannya."
            response = client.models.generate_content(model="gemini-flash-lite-latest", contents=prompt)
            st.write(response.text)
            # Tombol Download sederhana
            st.download_button("Download Teks Soal", response.text, file_name=f"Soal_{mapel}.txt")

# --- HALAMAN 4: DATA SISWA ---
elif menu == "Data Siswa":
    st.header("👥 Manajemen Siswa")
    with st.expander("➕ Tambah Siswa Baru"):
        nama = st.text_input("Nama Lengkap:")
        rek_baru = st.text_input("No Rekening (Contoh: 01.001):")
        if st.button("Simpan Siswa"):
            c = conn.cursor()
            c.execute("INSERT INTO siswa (no_rekening, nama) VALUES (?,?)", (rek_baru, nama))
            conn.commit()
            st.rerun()
    
    st.subheader("Daftar Nasabah")
    st.dataframe(pd.read_sql("SELECT * FROM siswa", conn), use_container_width=True)