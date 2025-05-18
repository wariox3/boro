
from fastapi import FastAPI, UploadFile, HTTPException, File, Form
from fastapi.responses import Response
from PIL import Image
from io import BytesIO

app = FastAPI(
    title="Comprimir imagenes", 
    max_upload_size=50_000_000)

EXTENSIONES_PERMITIDAS = {'jpg', 'jpeg', 'png', 'webp'}
TAMANO_MAXIMO_MB = 50

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/comprimir")
async def comprimir_imagen(file: UploadFile = File(...), quality: int = Form(50), optimize=True):
    """Endpoint para comprimir y redimensionar imágenes"""

    try:                
        extension = file.filename.split('.')[-1].lower()
        if extension not in EXTENSIONES_PERMITIDAS:
            raise HTTPException(400, "Formato no soportado")
                
        contenido = await file.read()
        if len(contenido) > TAMANO_MAXIMO_MB * 1024 * 1024:
            raise HTTPException(413, f"Archivo muy grande (máx {TAMANO_MAXIMO_MB}MB)")
        
        with Image.open(BytesIO(contenido)) as img:
            salida_buffer = BytesIO()     
            if extension in ('jpg', 'jpeg'):
                output_format = 'JPEG'
                media_type = 'image/jpeg'
            elif extension == 'png':
                output_format = 'PNG'
                media_type = 'image/png'
            elif extension == 'webp':
                output_format = 'WEBP'
                media_type = 'image/webp'                 
            img.save(
                salida_buffer,
                format=output_format,
                quality=quality,
                optimize=optimize
            )    
            salida_buffer.seek(0)                        
            return Response(content=salida_buffer.getvalue(), media_type=media_type)            
    
    except Exception as e:
        raise HTTPException(500, f"Error al procesar: {str(e)}")