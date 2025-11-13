import ezdxf
import json
import math
import os
from tkinter import Tk, filedialog

# =====================================================================
# BAGIAN 1: FUNGSI DARI PARSER.PY (EKSTRAKSI CAD)
# =====================================================================

def ekstrak_data_cad(path_file_dxf):
    """
    Membaca file DXF dan mengekstrak entitas penting.
    Ini adalah inti dari Fase 1.
    """
    print(f"Fase 1: Membaca file: '{path_file_dxf}'")
    try:
        doc = ezdxf.readfile(path_file_dxf)
    except IOError:
        print(f"Error: Tidak bisa membaca file '{path_file_dxf}'")
        return None
    except ezdxf.DXFStructureError:
        print(f"Error: File DXF rusak atau tidak valid.")
        return None

    msp = doc.modelspace()
    data_mentah_entitas = []

    # 1. Ekstrak LWPOLYLINE
    for entity in msp.query('LWPOLYLINE'):
        data_entitas = {
            "tipe": entity.dxftype(),
            "layer": entity.dxf.layer,
            "koordinat": [list(v) for v in entity.vertices_list()]
        }
        data_mentah_entitas.append(data_entitas)

    # 2. Ekstrak LINE
    for entity in msp.query('LINE'):
        data_entitas = {
            "tipe": entity.dxftype(),
            "layer": entity.dxf.layer,
            "koordinat": [list(entity.dxf.start), list(entity.dxf.end)]
        }
        data_mentah_entitas.append(data_entitas)

    # 3. Ekstrak Teks Anotasi
    for entity in msp.query('TEXT MTEXT'):
        if entity.dxf.hasattr('insert'):
            data_entitas = {
                "tipe": entity.dxftype(),
                "layer": entity.dxf.layer,
                "posisi": list(entity.dxf.insert),
                "isi_teks": entity.plain_text()
            }
            data_mentah_entitas.append(data_entitas)
            
    # 4. Ekstrak Blok (INSERT)
    for entity in msp.query('INSERT'):
        data_entitas = {
            "tipe": entity.dxftype(),
            "layer": entity.dxf.layer,
            "nama_blok": entity.dxf.name,
            "posisi": list(entity.dxf.insert)
        }
        data_mentah_entitas.append(data_entitas)

    print(f"Fase 1 selesai. {len(data_mentah_entitas)} entitas ditemukan.")
    return data_mentah_entitas

# =====================================================================
# BAGIAN 2: FUNGSI DARI PROSES_SST.PY (ANALISIS SPASIAL)
# =====================================================================

def int_to_alpha(n):
    """Mengubah 1, 2, 3 -> A, B, C"""
    result = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result

def hitung_jarak_euklides(p1, p2):
    """Menghitung jarak 2D (x, y)"""
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def cari_teks_terdekat(titik_tengah, list_teks):
    """Mencari teks terdekat ke sebuah titik tengah [x, y]"""
    jarak_terdekat = float('inf')
    teks_terpilih = None

    for teks in list_teks:
        koordinat_teks = teks['posisi'] 
        jarak = hitung_jarak_euklides(titik_tengah, koordinat_teks)
        
        if jarak < jarak_terdekat:
            jarak_terdekat = jarak
            teks_terpilih = teks['isi_teks']
            
    return teks_terpilih if teks_terpilih else "LABEL_TIDAK_DITEMUKAN"

def proses_data_spasial_bernama(data_mentah):
    """
    Mengambil data mentah dari Fase 1 dan melakukan Fase 2 (Analisis & Penamaan).
    """
    print("Memulai Fase 2: Analisis Spasial & Penamaan Objek...")
    
    list_dinding = []
    list_pintu = []
    list_teks = []

    # 1. Tugas 1: Klasifikasi Objek
    # Kita hanya proses 'LINE' untuk A-WALL dan A-DOOR
    for item in data_mentah:
        layer = item.get('layer')
        tipe = item.get('tipe')
        
        if layer == 'A-WALL' and tipe == 'LINE':
            list_dinding.append(item)
        elif layer == 'A-DOOR' and tipe == 'LINE':
            list_pintu.append(item)
        elif layer == 'A-ANNO':
            list_teks.append(item)

    print(f"Klasifikasi selesai: {len(list_dinding)} Dinding (LINE), {len(list_pintu)} Pintu (LINE), {len(list_teks)} Teks.")
    print("-" * 30)

    # 2. Tugas 2: Analisis Spasial (Menyimpan label sementara)
    print("Menghubungkan label ke objek...")
    for dinding in list_dinding:
        k = dinding['koordinat'] 
        titik_tengah = [(k[0][0] + k[1][0]) / 2, (k[0][1] + k[1][1]) / 2]
        dinding['label_cad_temp'] = cari_teks_terdekat(titik_tengah, list_teks)

    for pintu in list_pintu:
        k = pintu['koordinat']
        titik_tengah = [(k[0][0] + k[1][0]) / 2, (k[0][1] + k[1][1]) / 2]
        pintu['label_cad_temp'] = cari_teks_terdekat(titik_tengah, list_teks)

    # 3. Tugas 3: Kalkulasi & Pembuatan File Final
    print("Menghitung properti dan memberi nama unik...")
    data_final = []
    dinding_counter = 0
    pintu_counter = 0

    # Membuat objek DINDING
    for dinding in list_dinding:
        dinding_counter += 1
        nama_objek = f"DINDING {int_to_alpha(dinding_counter)}"
        k = dinding['koordinat']
        panjang = hitung_jarak_euklides(k[0], k[1])
        
        objek_dinding = {
            "nama": nama_objek,
            "panjang": round(panjang, 4),
            "Label_cad": dinding.get('label_cad_temp')
        }
        data_final.append(objek_dinding)

    # Membuat objek PINTU
    for pintu in list_pintu:
        pintu_counter += 1
        nama_objek = f"PINTU {int_to_alpha(pintu_counter)}"
        k = pintu['koordinat']
        lebar = hitung_jarak_euklides(k[0], k[1])
        
        objek_pintu = {
            "nama": nama_objek,
            "lebar": round(lebar, 4),
            "Label_cad": pintu.get('label_cad_temp')
        }
        data_final.append(objek_pintu)

    print(f"Proses Fase 2 selesai. {len(data_final)} objek siap disimpan.")
    return data_final

# =====================================================================
# BAGIAN 3: EKSEKUSI UTAMA (MAIN PROGRAM)
# =====================================================================

if __name__ == "__main__":
    
    # --- Tentukan folder output Anda di sini ---
    # Gunakan forward slash '/' agar aman di semua OS.
    FOLDER_OUTPUT = "data/processed"
    # -------------------------------------------

    # 1. Minta user memilih file DXF
    print("Memulai program... Silakan pilih file DXF.")
    root = Tk()
    root.withdraw() # Sembunyikan window utama Tkinter
    
    path_file_input = filedialog.askopenfilename(
        title="Pilih file DXF untuk diproses",
        filetypes=[("File DXF", "*.dxf"), ("Semua File", "*.*")]
    )

    if not path_file_input:
        print("Batal. Tidak ada file yang dipilih. Program berhenti.")
    else:
        
        # 2. Tentukan nama file output
        
        # 2a. Ambil HANYA nama filenya saja (misal: "gedung.dxf")
        nama_file_saja = os.path.basename(path_file_input) 
        
        # 2b. Pisahkan nama dasar dari ekstensinya (misal: "gedung")
        nama_dasar_file = os.path.splitext(nama_file_saja)[0]
        
        # 2c. Buat nama file output yang baru (misal: "gedung_processed.json")
        nama_file_output_baru = f"{nama_dasar_file}_processed.json"
        
        # 2d. Gabungkan FOLDER_OUTPUT dengan nama file baru
        path_file_output = os.path.join(FOLDER_OUTPUT, nama_file_output_baru)
        
        # 2e. Pastikan folder output-nya ada. Jika tidak, buatkan.
        os.makedirs(FOLDER_OUTPUT, exist_ok=True)
        
        print(f"\n--- ALUR KERJA DIMULAI ---")
        print(f"File Input: {path_file_input}")
        print(f"File Output: {path_file_output}") # Ini akan menunjukkan path baru
        print("-" * 30)

        # 3. Jalankan Fase 1: Ekstraksi
        data_hasil_ekstraksi = ekstrak_data_cad(path_file_input)
        
        if data_hasil_ekstraksi:
            # 4. Jika sukses, jalankan Fase 2: Pemrosesan
            data_final_untuk_json = proses_data_spasial_bernama(data_hasil_ekstraksi)
            
            # 5. Simpan hasil akhir (di lokasi baru)
            print("-" * 30)
            print(f"Menyimpan hasil akhir ke {path_file_output}...")
            try:
                with open(path_file_output, 'w') as f:
                    json.dump(data_final_untuk_json, f, indent=2)
                
                print(f"\n--- SUKSES! ---")
                print(f"File output telah disimpan di:")
                print(f"{path_file_output}")
                
            except IOError as e:
                print(f"\n--- ERROR SAAT MENYIMPAN ---")
                print(f"Gagal menyimpan file output. Pesan: {e}")
            except Exception as e:
                print(f"\n--- ERROR TIDAK DIKENAL ---")
                print(f"Terjadi error: {e}")
        else:
            print(f"--- ERROR ---")
            print("Gagal mengekstrak data dari file DXF. Program berhenti.")