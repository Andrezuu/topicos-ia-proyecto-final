import io
import base64
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image, UnidentifiedImageError
from openai import OpenAI
from dotenv import load_dotenv

# Cargar variables de entorno (.env)
load_dotenv()

app = FastAPI(title="Food Analyzer API")

# Configurar CORS para permitir cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los headers
)

# Inicializar cliente OpenAI (lee OPENAI_API_KEY del .env)
client = OpenAI()


class Recipe(BaseModel):
    """Modelo para la receta"""
    ingredientes: list[str]
    pasos: list[str]


class FoodAnalysisResponse(BaseModel):
    """Respuesta del análisis de comida"""
    nombre_plato: str
    receta: Recipe
    datos_curiosos: list[str]


@app.post("/analyze_food", response_model=FoodAnalysisResponse)
async def analyze_food(file: UploadFile = File(...)):
    """
    Endpoint que recibe una imagen de comida y devuelve:
    - Nombre del plato
    - Receta (ingredientes y pasos)
    - Datos curiosos
    """
    # Validar que sea una imagen
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=415, 
            detail="El archivo debe ser una imagen"
        )
    
    try:
        # Leer la imagen
        img_bytes = await file.read()
        img_stream = io.BytesIO(img_bytes)
        img_obj = Image.open(img_stream)
        
        # Validar que se pueda abrir como imagen
        img_obj.verify()
        
    except UnidentifiedImageError:
        raise HTTPException(
            status_code=415, 
            detail="No se pudo procesar la imagen"
        )
    
    # Convertir imagen a base64 para enviar a OpenAI
    img_stream.seek(0)
    base64_image = base64.b64encode(img_stream.read()).decode('utf-8')
    
    # Construir el prompt para OpenAI
    prompt = """
    Analiza esta imagen de comida y proporciona la siguiente información en formato JSON:
    Muchas de las imagenes seran sobre comida tradicional de diferentes culturas.
    
    {
        "nombre_plato": "nombre del plato identificado",
        "receta": {
            "ingredientes": ["ingrediente 1", "ingrediente 2", ...],
            "pasos": ["paso 1", "paso 2", ...]
        },
        "datos_curiosos": ["dato curioso 1", "dato curioso 2", "dato curioso 3"]
    }
    
    Si no puedes identificar el plato exacto, da tu mejor estimación basada en lo que ves.
    Proporciona al menos 3 datos curiosos sobre el plato o sus ingredientes.
    Responde ÚNICAMENTE con el JSON, sin texto adicional.
    """
    
    try:
        # Llamar a la API de OpenAI con visión
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extraer la respuesta
        content = response.choices[0].message.content
        
        # Intentar parsear el JSON de la respuesta
        import json
        # Limpiar la respuesta si viene con markdown
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        result = json.loads(content)
        
        # Validar y retornar usando el modelo Pydantic
        return FoodAnalysisResponse(
            nombre_plato=result["nombre_plato"],
            receta=Recipe(
                ingredientes=result["receta"]["ingredientes"],
                pasos=result["receta"]["pasos"]
            ),
            datos_curiosos=result["datos_curiosos"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al analizar la imagen con OpenAI: {str(e)}"
        )


@app.get("/")
def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "Food Analyzer API",
        "version": "1.0",
        "endpoints": {
            "POST /analyze_food": "Analiza una imagen de comida y devuelve receta y datos curiosos"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("food_analyzer_api:app", host="0.0.0.0", port=8000, reload=True)
