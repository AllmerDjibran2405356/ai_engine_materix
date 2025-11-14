import os

# --- KONFIGURASI FILE OUTPUT ---
NAMA_FOLDER_OUTPUT = "engine_bim_and_ifc/data/processed"
NAMA_FILE_OUTPUT = "ifc_blender_data.ifc"
PATH_FILE_OUTPUT = os.path.join(NAMA_FOLDER_OUTPUT, NAMA_FILE_OUTPUT)
# -----------------------------

# Data IFC mentah yang Anda berikan dari Blender
RAW_IFC_DATA = """ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('ViewDefinition[DesignTransferView]'),'2;1');
FILE_NAME('test_files.ifc','2025-11-13T18:33:35+07:00',(''),(''),'IfcOpenShell 0.8.3-post1','Bonsai 0.8.3-post1','Nobody');
FILE_SCHEMA(('IFC4'));
ENDSEC;
DATA;
#1=IFCPROJECT('2ohSgr6qL8s8xv7Muy1hDW',$,'My Project',$,$,$,$,(#14,#26),#9);
#2=IFCSIUNIT(*,.LENGTHUNIT.,$,.METRE.);
#3=IFCSIUNIT(*,.AREAUNIT.,$,.SQUARE_METRE.);
#4=IFCSIUNIT(*,.VOLUMEUNIT.,$,.CUBIC_METRE.);
#5=IFCDIMENSIONALEXPONENTS(0,0,0,0,0,0,0);
#6=IFCSIUNIT(*,.PLANEANGLEUNIT.,$,.RADIAN.);
#7=IFCMEASUREWITHUNIT(IFCREAL(0.0174532925199433),#6);
#8=IFCCONVERSIONBASEDUNIT(#5,.PLANEANGLEUNIT.,'degree',#7);
#9=IFCUNITASSIGNMENT((#3,#4,#2,#8));
#10=IFCCARTESIANPOINT((0.,0.,0.));
#11=IFCDIRECTION((0.,0.,1.));
#12=IFCDIRECTION((1.,0.,0.));
#13=IFCAXIS2PLACEMENT3D(#10,#11,#12);
#14=IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.E-05,#13,$);
#15=IFCGEOMETRICREPRESENTATIONSUBCONTEXT('Body','Model',*,*,*,*,#14,$,.MODEL_VIEW.,$);
#16=IFCGEOMETRICREPRESENTATIONSUBCONTEXT('Axis','Model',*,*,*,*,#14,$,.GRAPH_VIEW.,$);
#17=IFCGEOMETRICREPRESENTATIONSUBCONTEXT('Box','Model',*,*,*,*,#14,$,.MODEL_VIEW.,$);
#18=IFCGEOMETRICREPRESENTATIONSUBCONTEXT('Annotation','Model',*,*,*,*,#14,$,.SECTION_VIEW.,$);
#19=IFCGEOMETRICREPRESENTATIONSUBCONTEXT('Annotation','Model',*,*,*,*,#14,$,.ELEVATION_VIEW.,$);
#20=IFCGEOMETRICREPRESENTATIONSUBCONTEXT('Annotation','Model',*,*,*,*,#14,$,.MODEL_VIEW.,$);
#21=IFCGEOMETRICREPRESENTATIONSUBCONTEXT('Annotation','Model',*,*,*,*,#14,$,.PLAN_VIEW.,$);
#22=IFCGEOMETRICREPRESENTATIONSUBCONTEXT('Profile','Model',*,*,*,*,#14,$,.ELEVATION_VIEW.,$);
#23=IFCCARTESIANPOINT((0.,0.));
#24=IFCDIRECTION((1.,0.));
#25=IFCAXIS2PLACEMENT2D(#23,#24);
#26=IFCGEOMETRICREPRESENTATIONCONTEXT($,'Plan',2,1.E-05,#25,$);
#27=IFCGEOMETRICREPRESENTATIONSUBCONTEXT('Axis','Plan',*,*,*,*,#26,$,.GRAPH_VIEW.,$);
#28=IFCGEOMETRICREPRESENTATIONSUBCONTEXT('Body','Plan',*,*,*,*,#26,$,.PLAN_VIEW.,$);
#29=IFCGEOMETRICREPRESENTATIONSUBCONTEXT('Annotation','Plan',*,*,*,*,#26,$,.PLAN_VIEW.,$);
#30=IFCGEOMETRICREPRESENTATIONSUBCONTEXT('Annotation','Plan',*,*,*,*,#26,$,.REFLECTED_PLAN_VIEW.,$);
#31=IFCSITE('0qH2i2MWT2axnh9sWarYxP',$,'My Site',$,$,#54,$,$,$,$,$,$,$,$);
#37=IFCBUILDING('05uPtiV6b819Rdnx5F8V1v',$,'My Building',$,$,#60,$,$,$,$,$,$);
#43=IFCBUILDINGSTOREY('2p$ZEhSB57EwUHVcyRM_Cm',$,'My Storey',$,$,#66,$,$,$,$);
#49=IFCRELAGGREGATES('2UEa9HTabBARPyMt_l4PQD',$,$,$,#1,(#31));
#50=IFCCARTESIANPOINT((0.,0.,0.));
#51=IFCDIRECTION((0.,0.,1.));
#52=IFCDIRECTION((1.,0.,0.));
#53=IFCAXIS2PLACEMENT3D(#50,#51,#52);
#54=IFCLOCALPLACEMENT($,#53);
#55=IFCRELAGGREGATES('1iUAnTvy9ELxKy5bvV3Gsw',$,$,$,#31,(#37));
#56=IFCCARTESIANPOINT((0.,0.,0.));
#57=IFCDIRECTION((0.,0.,1.));
#58=IFCDIRECTION((1.,0.,0.));
#59=IFCAXIS2PLACEMENT3D(#56,#57,#58);
#60=IFCLOCALPLACEMENT(#54,#59);
#61=IFCRELAGGREGATES('3DQzjX_6fEtgNFDMLmFHHR',$,$,$,#37,(#43));
#62=IFCCARTESIANPOINT((0.,0.,0.));
#63=IFCDIRECTION((0.,0.,1.));
#64=IFCDIRECTION((1.,0.,0.));
#65=IFCAXIS2PLACEMENT3D(#62,#63,#64);
#66=IFCLOCALPLACEMENT(#60,#65);
ENDSEC;
END-ISO-10303-21;
"""

def create_ifc_from_raw_data():
    """
    Menyimpan data IFC mentah ke file.
    """
    os.makedirs(NAMA_FOLDER_OUTPUT, exist_ok=True)
    
    try:
        with open(PATH_FILE_OUTPUT, 'w') as f:
            f.write(RAW_IFC_DATA)
        print("-" * 30)
        print(f"Sukses! File IFC Mentah telah dibuat di: {PATH_FILE_OUTPUT}")
        print("Anda sekarang dapat menggunakan file ini sebagai input untuk skrip parser.")
    except Exception as e:
        print(f"ERROR: Gagal menyimpan file {PATH_FILE_OUTPUT}: {e}")

if __name__ == "__main__":
    create_ifc_from_raw_data()