import ifcopenshell
import ifcopenshell.api
import uuid
import os

# --- KONFIGURASI DENAH (GANTI ANGKA DI SINI) ---
# (Semua angka dalam METER)
# Buka 'contoh.dxf' di viewer, ukur, dan masukkan angkanya di bawah ini.

DENAH_TOTAL_PANJANG_X = 12.0  # GANTI INI: Total panjang dari dinding kiri ke kanan (Sumbu X)
DENAH_TOTAL_LEBAR_Y = 6.0     # GANTI INI: Total lebar dari dinding bawah ke atas (Sumbu Y)
POSISI_DINDING_TENGAH_X = 5.0 # GANTI INI: Posisi X dinding pemisah (ukur dari kiri)

POSISI_PINTU_KIRI_Y = 2.5     # GANTI INI: Posisi Y pintu kiri (ukur dari bawah)
POSISI_PINTU_TENGAH_Y = 3.0   # GANTI INI: Posisi Y pintu tengah (ukur dari bawah)

LEBAR_PINTU = 0.9             # Lebar bukaan pintu
TINGGI_PINTU = 2.1            # Tinggi bukaan pintu
TINGGI_DINDING = 3.5          # Tinggi total semua dinding
TEBAL_DINDING = 0.15          # Tebal total semua dinding
# --------------------------------------------------


# Konfigurasi File Output
NAMA_FOLDER_OUTPUT = "engine_bim_and_ifc/data/ifc"
NAMA_FILE = "denah_TES_TANPA_ROTASI.ifc" # <-- NAMA FILE TES BARU
# Membuat folder jika belum ada
if not os.path.exists(NAMA_FOLDER_OUTPUT):
    os.makedirs(NAMA_FOLDER_OUTPUT)
NAMA_FILE_OUTPUT = os.path.join(NAMA_FOLDER_OUTPUT, NAMA_FILE)

# Utility
UUID_GENERATOR = lambda: ifcopenshell.guid.compress(uuid.uuid4().hex)


# --- FUNGSI HELPER (PEMBUAT OBJEK) ---

def buat_hierarki(f):
    """
    Membuat Proyek -> Situs -> Gedung -> Lantai DARI NOL.
    """
    print("Membuat hierarki Proyek, Situs, Gedung, Lantai (dari nol)...")

    # 1. Buat OwnerHistory
    person = f.create_entity("IfcPerson")
    organization = f.create_entity("IfcOrganization", Name="MyOrg")
    person_and_org = f.create_entity("IfcPersonAndOrganization", ThePerson=person, TheOrganization=organization)
    application = f.create_entity("IfcApplication", 
        ApplicationDeveloper=organization, 
        Version="0.8.3", 
        ApplicationFullName="IfcOpenShell Script", 
        ApplicationIdentifier="ID_App")
    
    owner_history = f.create_entity("IfcOwnerHistory", 
        OwningUser=person_and_org, 
        OwningApplication=application, 
        ChangeAction="ADDED")

    # 2. Buat Project
    project = f.create_entity("IfcProject", 
        GlobalId=UUID_GENERATOR(), 
        OwnerHistory=owner_history, 
        Name="Proyek Denah 2 Ruangan")

    # 3. Tentukan Satuan (METER)
    length_unit = f.create_entity("IfcSIUnit", UnitType="LENGTHUNIT", Name="METRE")
    ifc_unit_assignment = f.create_entity("IfcUnitAssignment", Units=[length_unit])
    project.UnitsInContext = ifc_unit_assignment

    # 4. Buat Context
    context = f.create_entity("IfcGeometricRepresentationContext",
        ContextIdentifier="Model",
        ContextType="Model",
        CoordinateSpaceDimension=3,
        Precision=0.00001,
        WorldCoordinateSystem=f.create_entity("IfcAxis2Placement3D", Location=f.create_entity("IfcCartesianPoint", (0.0, 0.0, 0.0))),
        TrueNorth=f.create_entity("IfcDirection", (0.0, 1.0, 0.0))
    )
    project.RepresentationContexts = [context]

    # 5. Buat Hierarki Spasial
    site = f.create_entity("IfcSite", GlobalId=UUID_GENERATOR(), OwnerHistory=owner_history, Name="Situs Default")
    building = f.create_entity("IfcBuilding", GlobalId=UUID_GENERATOR(), OwnerHistory=owner_history, Name="Gedung Default")
    storey = f.create_entity("IfcBuildingStorey", GlobalId=UUID_GENERATOR(), OwnerHistory=owner_history, Name="Lantai 1", Elevation=0.0)

    # 6. "Jahit" hierarkinya
    f.create_entity("IfcRelAggregates", GlobalId=UUID_GENERATOR(), OwnerHistory=owner_history, RelatingObject=project, RelatedObjects=[site])
    f.create_entity("IfcRelAggregates", GlobalId=UUID_GENERATOR(), OwnerHistory=owner_history, RelatingObject=site, RelatedObjects=[building])
    f.create_entity("IfcRelAggregates", GlobalId=UUID_GENERATOR(), OwnerHistory=owner_history, RelatingObject=building, RelatedObjects=[storey])
    
    return context, owner_history, storey

def buat_dinding(f, context, owner_history, storey, pset_x, pset_y, panjang, tebal, tinggi, tag):
    """Membuat 1 objek IfcWall lengkap dengan geometri 3D."""
    
    dinding = f.create_entity("IfcWall", GlobalId=UUID_GENERATOR(), OwnerHistory=owner_history, Name="Dinding Bata", Tag=tag)
    print(f"  - Membuat Dinding: {tag} (Center: {pset_x:.2f}, {pset_y:.2f}, Panjang: {panjang}m)")

    placement_3d = f.create_entity("IfcAxis2Placement3D", 
        Location=f.create_entity("IfcCartesianPoint", (pset_x, pset_y, 0.0))
    )
    local_placement = f.create_entity("IfcLocalPlacement", PlacementRelTo=storey.ObjectPlacement, RelativePlacement=placement_3d)
    
    profile = f.create_entity("IfcRectangleProfileDef", ProfileType="AREA", XDim=panjang, YDim=tebal)
    extrusion_dir = f.create_entity("IfcDirection", (0.0, 0.0, 1.0))
    body = f.create_entity("IfcExtrudedAreaSolid", SweptArea=profile, ExtrudedDirection=extrusion_dir, Depth=tinggi)
    
    shape_rep = f.create_entity("IfcShapeRepresentation", ContextOfItems=context, RepresentationIdentifier="Body", RepresentationType="SweptSolid", Items=[body])
    product_def_shape = f.create_entity("IfcProductDefinitionShape", Representations=[shape_rep])
    
    dinding.ObjectPlacement = local_placement
    dinding.Representation = product_def_shape
    # Daftarkan dinding ini ke lantainya
    f.create_entity("IfcRelContainedInSpatialStructure", GlobalId=UUID_GENERATOR(), OwnerHistory=owner_history, RelatingStructure=storey, RelatedElements=[dinding])
    
    return dinding

def buat_lubang_pintu(f, context, owner_history, storey, dinding_induk, x_pos_lokal, lebar, tinggi, tebal):
    """Membuat lubang (Opening) dan menempelkannya ke Dinding."""
    print(f"    - Membuat lubang pintu di {dinding_induk.Tag} (Posisi: {x_pos_lokal}m)")
    
    opening = f.create_entity("IfcOpeningElement", GlobalId=UUID_GENERATOR(), OwnerHistory=owner_history, Name="Lubang Pintu")

    placement_3d = f.create_entity("IfcAxis2Placement3D", Location=f.create_entity("IfcCartesianPoint", (x_pos_lokal, 0.0, 0.0)))
    local_placement = f.create_entity("IfcLocalPlacement", PlacementRelTo=dinding_induk.ObjectPlacement, RelativePlacement=placement_3d)

    profile = f.create_entity("IfcRectangleProfileDef", 
        ProfileType="AREA", 
        XDim=lebar, 
        YDim=tebal + 0.01,
        Position=f.create_entity("IfcAxis2Placement2D", f.create_entity("IfcCartesianPoint", (0.0, -0.005)))
    ) 
    
    extrusion_dir = f.create_entity("IfcDirection", (0.0, 0.0, 1.0))
    body = f.create_entity("IfcExtrudedAreaSolid", SweptArea=profile, ExtrudedDirection=extrusion_dir, Depth=tinggi)

    shape_rep = f.create_entity("IfcShapeRepresentation", ContextOfItems=context, RepresentationIdentifier="Body", RepresentationType="SweptSolid", Items=[body])
    product_def_shape = f.create_entity("IfcProductDefinitionShape", Representations=[shape_rep])

    opening.ObjectPlacement = local_placement
    opening.Representation = product_def_shape
    
    # "Jahit" lubang ke dinding
    f.create_entity("IfcRelVoidsElement", GlobalId=UUID_GENERATOR(), OwnerHistory=owner_history, RelatingBuildingElement=dinding_induk, RelatedOpeningElement=opening)
    
    # Daftarkan lubang ini ke lantainya juga (agar BlenderBIM senang)
    f.create_entity("IfcRelContainedInSpatialStructure", GlobalId=UUID_GENERATOR(), OwnerHistory=owner_history, RelatingStructure=storey, RelatedElements=[opening])
    
    return opening

def putar_dinding_vertikal(f, dinding):
    """Memutar dinding agar membentang sepanjang sumbu Y."""
    placement = dinding.ObjectPlacement.RelativePlacement
    
    placement.Axis = f.create_entity("IfcDirection", (0.0, 0.0, 1.0)) 
    placement.RefDirection = f.create_entity("IfcDirection", (0.0, 1.0, 0.0))

# --- FUNGSI UTAMA ---

def buat_ifc_denah_tes():
    print(f"*** TES BARU: MEMBUAT FILE: {NAMA_FILE_OUTPUT} ***")
    
    f = ifcopenshell.file(schema="IFC2X3")
    context, owner_history, storey = buat_hierarki(f)

    print("Membuat model 3D dan properti berdasarkan konfigurasi...")
    
    setengah_tebal = TEBAL_DINDING / 2.0

    # 2. Buat 5 Dinding
    
    # Dinding Bawah (Horizontal)
    dinding_bawah = buat_dinding(f, context, owner_history, storey, 
        pset_x=0.0, pset_y=setengah_tebal,
        panjang=DENAH_TOTAL_PANJANG_X, tebal=TEBAL_DINDING, tinggi=TINGGI_DINDING, 
        tag="W-BAWAH")
    
    # Dinding Atas (Horizontal)
    dinding_atas = buat_dinding(f, context, owner_history, storey, 
        pset_x=0.0, pset_y=DENAH_TOTAL_LEBAR_Y - setengah_tebal,
        panjang=DENAH_TOTAL_PANJANG_X, tebal=TEBAL_DINDING, tinggi=TINGGI_DINDING, 
        tag="W-ATAS")

    # Dinding Kiri (Vertikal)
    dinding_kiri = buat_dinding(f, context, owner_history, storey, 
        pset_x=setengah_tebal, pset_y=0.0,
        panjang=DENAH_TOTAL_LEBAR_Y, tebal=TEBAL_DINDING, tinggi=TINGGI_DINDING, 
        tag="W-KIRI")
    
    # Dinding Kanan (Vertikal)
    dinding_kanan = buat_dinding(f, context, owner_history, storey, 
        pset_x=DENAH_TOTAL_PANJANG_X - setengah_tebal, pset_y=0.0,
        panjang=DENAH_TOTAL_LEBAR_Y, tebal=TEBAL_DINDING, tinggi=TINGGI_DINDING, 
        tag="W-KANAN")
    
    # Dinding Tengah (Vertikal)
    dinding_tengah = buat_dinding(f, context, owner_history, storey, 
        pset_x=POSISI_DINDING_TENGAH_X, pset_y=0.0, 
        panjang=DENAH_TOTAL_LEBAR_Y, tebal=TEBAL_DINDING, tinggi=TINGGI_DINDING, 
        tag="W-TENGAH")

    # 3. Putar Dinding Vertikal
    # (Kode ini memutar dinding Kiri, Kanan, dan Tengah)
    
    # --- SESUAI PERMINTAAN ANDA: ROTASI DIMATIKAN ---
    # putar_dinding_vertikal(f, dinding_kiri)
    # putar_dinding_vertikal(f, dinding_kanan)
    # putar_dinding_vertikal(f, dinding_tengah)
    print("\n*** PERINGATAN: ROTASI DINDING VERTIKAL SENGAJA DIMATIKAN UNTUK TES ***\n")


    # 4. Buat 2 Lubang Pintu
    # Lubang-lubang ini mungkin tidak akan menempel dengan benar
    # karena dindingnya tidak berada di posisi yang seharusnya.
    try:
        buat_lubang_pintu(f, context, owner_history, storey, dinding_kiri, 
            x_pos_lokal=POSISI_PINTU_KIRI_Y, lebar=LEBAR_PINTU, tinggi=TINGGI_PINTU, tebal=TEBAL_DINDING)

        buat_lubang_pintu(f, context, owner_history, storey, dinding_tengah, 
            x_pos_lokal=POSISI_PINTU_TENGAH_Y, lebar=LEBAR_PINTU, tinggi=TINGGI_PINTU, tebal=TEBAL_DINDING)
    except Exception as e:
        print(f"Gagal membuat lubang pintu (ini wajar karena dinding tidak diputar): {e}")

    # 5. Simpan File IFC
    try:
        f.write(NAMA_FILE_OUTPUT)
        print("-" * 30)
        print(f"Sukses! File '{NAMA_FILE_OUTPUT}' telah dibuat.")
        print(f"Lokasi: {os.path.abspath(NAMA_FILE_OUTPUT)}")
        print("Buka file ini di FZKViewer, BIM Vision, atau viewer IFC lainnya.")
    except Exception as e:
        print(f"ERROR saat menyimpan file IFC: {e}")

# --- Eksekusi Skrip ---
if __name__ == "__main__":
    buat_ifc_denah_tes()