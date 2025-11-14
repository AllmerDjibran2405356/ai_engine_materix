import ezdxf

# --- Mulai ---
print("Membuat file tes DXF...")
try:
    doc = ezdxf.new(dxfversion='R2018')  # Buat dokumen DXF baru
except ezdxf.LicenseError:
    print("Peringatan: Gagal menggunakan 'r12writer' (mungkin perlu add-on).")
    # Tetap lanjut, ezdxf akan otomatis mencari fallback.
    
msp = doc.modelspace()  # msp = "Modelspace", tempat kita menggambar

# --- 1. Buat Layer (Paling PentING untuk AI Anda) ---
# Ini adalah "standar" yang akan dibaca parser Anda
doc.layers.new("A-WALL", dxfattribs={'color': 1})  # Merah
doc.layers.new("A-DOOR", dxfattribs={'color': 3})  # Hijau
doc.layers.new("A-ANNO", dxfattribs={'color': 5})  # Biru

# --- 2. Ruangan 1 (Kotak, ukuran 20x20) ---
# Asumsi "ukuran 20" maksudnya 20x20 unit (misal, 20m x 20m)
# Posisi: dari (0,0) sampai (20,20)
# Kita gambar 4 dinding sebagai 4 garis di layer A-WALL
msp.add_line((0, 0), (20, 0), dxfattribs={'layer': 'A-WALL'})    # Dinding bawah
msp.add_line((20, 0), (20, 20), dxfattribs={'layer': 'A-WALL'})  # Dinding kanan
msp.add_line((20, 20), (0, 20), dxfattribs={'layer': 'A-WALL'})  # Dinding atas
msp.add_line((0, 20), (0, 0), dxfattribs={'layer': 'A-WALL'})    # Dinding kiri

# Tambah anotasi
# --- PERBAIKAN DI SINI ---
# Posisi (insert) dimasukkan ke dalam dxfattribs
msp.add_text(
    "D-01",
    dxfattribs={
        'layer': 'A-ANNO',
        'height': 0.8,
        'insert': (8, 10)  # Posisi teks di dalam ruangan
    }
)

# --- 3. Ruangan 2 (Kotak, misal 15x20) ---
# Kita buat nempel di sebelah kanan Ruangan 1
# Posisi: dari (20,0) sampai (35,20)
# Kita hanya perlu gambar 3 dinding, karena 1 dinding sudah ada (shared wall)
msp.add_line((20, 0), (35, 0), dxfattribs={'layer': 'A-WALL'})    # Dinding bawah
msp.add_line((35, 0), (35, 20), dxfattribs={'layer': 'A-WALL'})  # Dinding kanan
msp.add_line((35, 20), (20, 20), dxfattribs={'layer': 'A-WALL'})  # Dinding atas

# Tambah anotasi
# --- PERBAIKAN DI SINI ---
msp.add_text(
    "D-02",
    dxfattribs={
        'layer': 'A-ANNO',
        'height': 0.8,
        'insert': (26, 10) # Posisi teks di dalam ruangan
    }
)

# --- 4. Buat 3 Pintu (dan "Lubangi" Dinding) ---
# Ini adalah bagian "sulit" yang akan diuji AI Anda

# Pintu 1 (di dinding bawah Room 1)
# Kita "lubangi" dinding (0,0)-(20,0)
msp.add_line((0, 0), (4, 0), dxfattribs={'layer': 'A-WALL'})      # Dinding (bagian 1)
msp.add_line((5, 0), (20, 0), dxfattribs={'layer': 'A-WALL'})     # Dinding (bagian 2)
# Gambar pintunya (cukup garis)
msp.add_line((4, 0), (5, 0), dxfattribs={'layer': 'A-DOOR'})

# Pintu 2 (di dinding bawah Room 2)
# Kita "lubangi" dinding (20,0)-(35,0)
msp.add_line((20, 0), (24, 0), dxfattribs={'layer': 'A-WALL'})    # Dinding (bagian 1)
msp.add_line((25, 0), (35, 0), dxfattribs={'layer': 'A-WALL'})    # Dinding (bagian 2)
# Gambar pintunya
msp.add_line((24, 0), (25, 0), dxfattribs={'layer': 'A-DOOR'})

# Pintu 3 (di dinding penghubung)
# Kita "lubangi" dinding (20,0)-(20,20)
msp.add_line((20, 0), (20, 8), dxfattribs={'layer': 'A-WALL'})     # Dinding (bagian 1)
msp.add_line((20, 9), (20, 20), dxfattribs={'layer': 'A-WALL'})    # Dinding (bagian 2)
# Gambar pintunya
msp.add_line((20, 8), (20, 9), dxfattribs={'layer': 'A-DOOR'})

# --- 5. Simpan File ---
NAMA_FILE_TES = "tes_denah_2ruang.dxf"
try:
    doc.saveas(NAMA_FILE_TES)
    print(f"\nSukses! File tes '{NAMA_FILE_TES}' telah dibuat.")
    print("File ini berisi denah 2D dengan layer dan anotasi, SIAP untuk parser.py Anda.")
except Exception as e:
    print(f"Error saat menyimpan: {e}")