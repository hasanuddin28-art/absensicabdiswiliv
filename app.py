import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import face_recognition
import numpy as np
from PIL import Image
from streamlit_geolocation import streamlit_geolocation

# Pengaturan Halaman Streamlit
st.set_page_config(page_title="Absensi Area Makassar", page_icon="🏫", layout="centered")

# Zona Waktu Makassar (WITA)
makassar_tz = pytz.timezone('Asia/Makassar')

# Fungsi dummy untuk memuat foto wajah dari database (Simulasi)
# Pada praktiknya, ini dihubungkan ke database sesungguhnya
@st.cache_resource
def load_known_face():
    # Sistem pura-puranya sudah memiliki foto pegawai bernama Budi
    # Hapus try-except ini jika Anda sudah punya foto asli di folder proyek
    try:
        image = face_recognition.load_image_file("foto_db_budi.jpg")
        encoding = face_recognition.face_encodings(image)[0]
        return encoding
    except:
        return None

known_encoding = load_known_face()

st.title("Sistem Absensi Pendidik")
st.write("Silakan izinkan akses lokasi (GPS) dan kamera pada perangkat Anda.")

# 1. MENDAPATKAN LOKASI (GPS)
st.subheader("1. Titik Koordinat")
location = streamlit_geolocation()
lat_pegawai = None
long_pegawai = None

if location and location['latitude'] is not None:
    lat_pegawai = location['latitude']
    long_pegawai = location['longitude']
    st.success(f"Lokasi Ditemukan! Lat: {lat_pegawai}, Long: {long_pegawai}")
else:
    st.warning("Klik tombol di atas untuk mengambil lokasi Anda saat ini.")

# 2. MENDAPATKAN FOTO DARI KAMERA
st.subheader("2. Perekaman Wajah")
foto_kamera = st.camera_input("Ambil Foto Anda")

# 3. PROSES ABSENSI
if st.button("Kirim Absensi", type="primary"):
    if lat_pegawai is None or long_pegawai is None:
        st.error("Gagal: Lokasi belum ditemukan. Silakan izinkan GPS terlebih dahulu.")
    elif foto_kamera is None:
        st.error("Gagal: Anda belum mengambil foto wajah.")
    else:
        # Cek Jam WITA
        waktu_sekarang = datetime.now(makassar_tz)
        jam_sekarang = waktu_sekarang.strftime('%H:%M:%S')
        tanggal_sekarang = waktu_sekarang.strftime('%d-%m-%Y')
        
        # Proses Cek Wajah (diperketat dengan tolerance 0.4)
        image = Image.open(foto_kamera)
        img_array = np.array(image)
        face_locations = face_recognition.face_locations(img_array)
        
        if len(face_locations) == 0:
            st.error("Wajah tidak terdeteksi! Pastikan pencahayaan cukup dan wajah terlihat jelas.")
        else:
            # Jika menggunakan foto dari database, bandingkan di sini
            if known_encoding is not None:
                unknown_encoding = face_recognition.face_encodings(img_array)[0]
                hasil = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=0.4)
                if hasil[0]:
                    st.success(f"Absen Berhasil pada {tanggal_sekarang} jam {jam_sekarang} WITA")
                    st.balloons()
                else:
                    st.error("Wajah tidak dikenali dalam database. Silakan coba lagi.")
            else:
                # Mode Bypass (karena belum ada database foto yang sesungguhnya di tutorial ini)
                st.success(f"Absen Diterima! (Mode Simulasi) - {tanggal_sekarang} {jam_sekarang} WITA")
                st.balloons()