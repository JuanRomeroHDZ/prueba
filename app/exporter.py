import os
import pandas as pd
from database import get_connection

EXPORTS_DIR = os.path.join(os.path.dirname(__file__), '../exports')

def export_jobs_to_excel(filename="reports.xlsx"):
    """
    Exporta todas las vacantes almacenadas en la base de datos a un archivo Excel formateado.
    """
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    file_path = os.path.join(EXPORTS_DIR, filename)
    
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM jobs", conn)
    conn.close()
    
    if df.empty:
        print("⚠️ No hay datos para exportar en jobs.db")
        return None
        
    # Guardar en Excel usando openpyxl
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name="Vacantes TI", index=False)
        
    print(f"📄 Reporte generado exitosamente en: {file_path}")
    return file_path

if __name__ == "__main__":
    export_jobs_to_excel()
