import os
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

# Obtiene la ruta de la carpeta 'reports' dentro de 'media'
reports_dir = os.path.join(settings.MEDIA_ROOT, 'reports')

# Número máximo de archivos que un usuario puede guardar (2 archivos como máximo)
MAX_FILES_PER_USER = 2

# Nombre del archivo, que puede ser único por ID de comparación
def get_pdf_filename(user_id, comparison_id):
    # Aquí generamos un nombre único para el PDF
    return f"{user_id}_{comparison_id}_comparison_report.pdf"

# Función para guardar el archivo PDF temporalmente
def save_pdf_temporarily(pdf_data, user_id, comparison_id):
    filename = get_pdf_filename(user_id, comparison_id)
    file_path = os.path.join(reports_dir, filename)

    # Guardar el archivo PDF
    with open(file_path, 'wb') as f:
        f.write(pdf_data)

    # Limpiar archivos antiguos si se excede el límite
    cleanup_old_pdfs(user_id)

    return file_path

# Función para comprobar si el PDF existe y si no ha expirado
def get_existing_pdf(user_id, comparison_id):
    filename = get_pdf_filename(user_id, comparison_id)
    file_path = os.path.join(reports_dir, filename)

    # Comprobar si el archivo existe
    if os.path.exists(file_path):
        # Verificar si el archivo ha expirado (por ejemplo, si tiene más de 1 día)
        file_creation_time = os.path.getctime(file_path)
        if timezone.now().timestamp() - file_creation_time < timedelta(days=1).total_seconds():
            return file_path
        else:
            # El archivo ha expirado, lo eliminamos
            os.remove(file_path)
    return None

# Función para eliminar archivos antiguos (por ejemplo, más de X días)
def cleanup_old_pdfs(user_id, retention_days=1, max_files=MAX_FILES_PER_USER):
    user_reports_dir = os.path.join(reports_dir, str(user_id))

    if not os.path.exists(user_reports_dir):
        return

    # Obtenemos todos los archivos PDF en la carpeta del usuario
    files = []
    for filename in os.listdir(user_reports_dir):
        file_path = os.path.join(user_reports_dir, filename)
        if os.path.exists(file_path):
            files.append(file_path)

    # Ordenamos los archivos por fecha de creación (el más antiguo primero)
    files.sort(key=lambda x: os.path.getctime(x))

    # Eliminamos archivos si el número de archivos excede el límite (2 archivos como máximo)
    while len(files) > max_files:
        oldest_file = files.pop(0)  # El archivo más antiguo
        os.remove(oldest_file)

    # Ahora limpiamos los archivos que han expirado (más de 1 día)
    now = timezone.now()
    for file_path in files:
        file_creation_time = os.path.getctime(file_path)
        if now.timestamp() - file_creation_time > timedelta(days=retention_days).total_seconds():
            os.remove(file_path)
