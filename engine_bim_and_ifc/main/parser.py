import ifcopenshell
import ifcopenshell.api
import os
import json
from tkinter import Tk, filedialog

# --- Konfigurasi ---
FOLDER_OUTPUT = "engine_bim_and_ifc/data/processed"

# =====================================================================
# INI ADALAH "OTAK" PARSER BIM (HELPER FUNCTION)
# (Tidak ada perubahan di fungsi ini, sudah bagus)
# =====================================================================
def get_ifc_attribute(element, set_name, attr_name):
    """
    Fungsi helper untuk mengambil satu nilai Properti (Pset) atau
    Kuantitas (Qset) dari sebuah elemen IFC (seperti IfcWall).
    """
    try:
        # 1. Loop melalui semua relasi properti/kuantitas elemen
        for rel in element.IsDefinedBy:
            # 2. Pastikan itu adalah relasi yang mendefinisikan properti/kuantitas
            if rel.is_a("IfcRelDefinesByProperties"):
                pset = rel.RelatingPropertyDefinition
                
                # Cek apakah ini Property Set atau Quantity Set
                is_pset = pset.is_a("IfcPropertySet")
                is_qset = pset.is_a("IfcElementQuantity")
                
                # 3. Cek apakah nama Set-nya cocok (misal: "Pset_WallCommon" atau "BaseQuantities")
                if pset.Name == set_name:
                    
                    # Kasus A: Jika IfcPropertySet (Pset)
                    if is_pset:
                        for prop in pset.HasProperties:
                            if prop.Name == attr_name and prop.is_a("IfcPropertySingleValue"):
                                # Untuk Pset, nilainya ada di NominalValue
                                return prop.NominalValue.wrappedValue

                    # Kasus B: Jika IfcElementQuantity (Qset)
                    elif is_qset:
                        for quantity in pset.Quantities:
                            if quantity.Name == attr_name:
                                
                                # --- Logika IFC2x3 (Sudah Benar) ---
                                if quantity.is_a("IfcQuantityLength"):
                                    return quantity.LengthValue    # <-- Atribut spesifik
                                elif quantity.is_a("IfcQuantityArea"):
                                    return quantity.AreaValue      # <-- Atribut spesifik
                                elif quantity.is_a("IfcQuantityVolume"):
                                    return quantity.VolumeValue    # <-- Atribut spesifik
                                # Fallback untuk IFC4 (jika ada)
                                elif hasattr(quantity, 'NominalValue'):
                                    return quantity.NominalValue.wrappedValue
                                
    except Exception as e:
        # Gunakan ID elemen untuk debug yang lebih mudah
        print(f"  [Peringatan] Gagal mengambil atribut {attr_name} dari {element.is_a()} ID:{element.id()}: {e}")
        
    return None # Kembalikan None jika tidak ditemukan

# =====================================================================
# FUNGSI PARSER UTAMA (TELAH DIMODIFIKASI)
# =====================================================================
def parse_ifc_file(ifc_path):
    """
    Membaca file IFC dan mengekstrak semua data Dinding (IfcWall)
    ke dalam format JSON yang bersih, dengan Quantity Set sebagai prioritas.
    """
    print(f"Fase 1 (BIM): Membuka file '{ifc_path}'...")
    try:
        f = ifcopenshell.open(ifc_path)
    except Exception as e:
        print(f"ERROR: Gagal membuka file IFC. {e}")
        return None

    # Siapkan list untuk menampung hasil
    data_terekstrak = []
    
    # 1. Dapatkan semua DINDING (IfcWall) di dalam file
    dinding_dinding = f.by_type("IfcWall")
    print(f"Ditemukan {len(dinding_dinding)} Dinding (IfcWall). Memproses...")

    # 2. Loop melalui setiap dinding
    for dinding in dinding_dinding:
        
        # --- Ekstraksi Kuantitas ---
        # Prioritaskan "BaseQuantities" (dari Revit/Archicad)
        
        # Dimensi Dasar (untuk fallback)
        panjang = get_ifc_attribute(dinding, "BaseQuantities", "Length")
        tinggi = get_ifc_attribute(dinding, "BaseQuantities", "Height")
        tebal = get_ifc_attribute(dinding, "BaseQuantities", "Width") 
        
        # Kuantitas Kalkulasi (LEBIH PENTING)
        # Seringkali Area ini "NetArea" atau "NetSideArea"
        area = get_ifc_attribute(dinding, "BaseQuantities", "NetArea")
        volume = get_ifc_attribute(dinding, "BaseQuantities", "NetVolume")

        # Fallback (jika BaseQuantities tidak ada/kosong)
        if area is None:
            area = get_ifc_attribute(dinding, "BaseQuantities", "NetSideArea")
        
        # Fallback Kalkulasi Manual (JIKA GAGAL TOTAL)
        if area is None and panjang is not None and tinggi is not None:
            area = panjang * tinggi
            print(f"  [Info] Dinding '{dinding.Tag}': Area dihitung manual ({panjang} * {tinggi})")

        if volume is None and area is not None and tebal is not None:
            volume = area * tebal
            print(f"  [Info] Dinding '{dinding.Tag}': Volume dihitung manual ({area} * {tebal})")
            
        
        # --- PERUBAHAN UTAMA: Membuat Objek JSON ---
        objek_dinding = {
            "guid": dinding.GlobalId,
            "tipe_ifc": dinding.is_a(), # Hasil: "IfcWallStandardCase"
            "nama": dinding.Name if dinding.Name else "N/A",
            "label_cad": dinding.Tag,
            
            # --- TAMBAHAN: Satuan Hitung Utama ---
            # Ini adalah 'petunjuk' untuk UI Anda agar memfilter resep.
            # Untuk Dinding, hampir selalu m²
            "satuan_utama_hitung": "m2",
            "satuan_sumber": "METER", # Menandakan data sumber dalam METER
            
            # --- TAMBAHAN: Kamus Kuantitas ---
            # Mengelompokkan semua data terukur agar rapi
            "kuantitas": {
                "panjang": round(panjang, 3) if panjang is not None else None,
                "tinggi": round(tinggi, 3) if tinggi is not None else None,
                "tebal": round(tebal, 3) if tebal is not None else None,
                "area_m2": round(area, 3) if area is not None else None,
                "volume_m3": round(volume, 3) if volume is not None else None
            }
        }
        
        data_terekstrak.append(objek_dinding)
        status = "BERHASIL" if area is not None else "HAMPIR KOSONG (Cek File Anda)"
        print(f"  + Dinding '{dinding.Tag}' (ID:{dinding.id()}) diproses. Status Kuantitas: {status}")

    # --- Tambahan: Memproses Pintu (IfcDoor) ---
    pintu_pintu = f.by_type("IfcDoor")
    print(f"Ditemukan {len(pintu_pintu)} Pintu (IfcDoor). Memproses...")
    
    for pintu in pintu_pintu:
        # Pintu: Gunakan BaseQuantities
        lebar_pintu = get_ifc_attribute(pintu, "BaseQuantities", "Width")
        tinggi_pintu = get_ifc_attribute(pintu, "BaseQuantities", "Height")
        area_pintu = get_ifc_attribute(pintu, "BaseQuantities", "Area")
        
        # Fallback ke Pset_DoorCommon
        if not lebar_pintu:
            lebar_pintu = get_ifc_attribute(pintu, "Pset_DoorCommon", "OverallWidth")
        if not tinggi_pintu:
            tinggi_pintu = get_ifc_attribute(pintu, "Pset_DoorCommon", "OverallHeight")
            
        # Fallback Kalkulasi Area
        if area_pintu is None and lebar_pintu is not None and tinggi_pintu is not None:
            area_pintu = lebar_pintu * tinggi_pintu
            
        # --- PERUBAHAN UTAMA: Membuat Objek JSON Pintu ---
        objek_pintu = {
            "guid": pintu.GlobalId,
            "tipe_ifc": pintu.is_a(), 
            "nama": pintu.Name if pintu.Name else "N/A",
            "label_cad": pintu.Tag,
            
            # --- TAMBAHAN: Satuan Hitung Utama ---
            # Sesuai resep Anda (A-203, A-204), Pintu dihitung per m²
            "satuan_utama_hitung": "m²", 
            "satuan_sumber": "METER",

            # --- TAMBAHAN: Kamus Kuantitas ---
            "kuantitas": {
                "lebar": round(lebar_pintu, 3) if lebar_pintu is not None else None,
                "tinggi": round(tinggi_pintu, 3) if tinggi_pintu is not None else None,
                "area_m2": round(area_pintu, 3) if area_pintu is not None else None,
                "jumlah_buah": 1 # Setiap objek adalah 1 buah
            }
        }
        data_terekstrak.append(objek_pintu)
        status = "BERHASIL" if (area_pintu is not None) else "HAMPIR KOSONG (Cek File Anda)"
        print(f"  + Pintu '{pintu.Tag}' (ID:{pintu.id()}) diproses. Status Kuantitas: {status}")


    print(f"Fase 1 (BIM) selesai. {len(data_terekstrak)} objek diekstrak.")
    return data_terekstrak

# =====================================================================
# EKSEKUSI UTAMA (Tidak Berubah)
# =====================================================================

if __name__ == "__main__":
    
    # 1. Minta user memilih file IFC
    print("Memulai Parser BIM... Silakan pilih file IFC.")
    root = Tk()
    root.withdraw()
    
    path_file_input = filedialog.askopenfilename(
        title="Pilih file IFC (.ifc) untuk diproses",
        filetypes=[("Industry Foundation Classes", "*.ifc"), ("Semua File", "*.*")]
    )

    if not path_file_input:
        print("Batal. Tidak ada file yang dipilih.")
    else:
        # 2. Tentukan nama file output
        os.makedirs(FOLDER_OUTPUT, exist_ok=True)
        nama_dasar_file = os.path.splitext(os.path.basename(path_file_input))[0]
        nama_file_output_baru = f"{nama_dasar_file}_ifc_data.json"
        path_file_output = os.path.join(FOLDER_OUTPUT, nama_file_output_baru)
        
        print(f"\n--- ALUR KERJA BIM DIMULAI ---")
        print(f"File Input: {path_file_input}")
        print(f"File Output: {path_file_output}")
        print("-" * 30)

        # 3. Jalankan Parser
        data_final_json = parse_ifc_file(path_file_input)
        
        if data_final_json:
            # 4. Simpan hasil
            print("-" * 30)
            print(f"Menyimpan hasil akhir ke {path_file_output}...")
            try:
                with open(path_file_output, 'w') as f:
                    json.dump(data_final_json, f, indent=2)
                
                print(f"\n--- SUKSES! ---")
                print(f"File output telah disimpan di: {path_file_output}")
                
            except IOError as e:
                print(f"\n--- ERROR SAAT MENYIMPAN: {e}")
        else:
            print(f"--- ERROR ---")
            print("Gagal mem-parsing data dari file IFC.")