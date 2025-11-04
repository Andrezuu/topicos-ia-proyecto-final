import io
import base64
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image, UnidentifiedImageError
from dotenv import load_dotenv
from agent import get_agent
from tools import get_ingredient_substitutes, calculate_nutrition, compare_dishes_from_db
import database as db

load_dotenv()

# Initialize database
db_conn = db.setup_database()

app = FastAPI(
    title="Food Analyzer Agent API",
    version="3.0.0",
    description="API con agente inteligente DSPy para análisis de comida con base de datos SQLite"
)

# Configurar CORS para permitir cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)


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
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=415, 
            detail="El archivo debe ser una imagen"
        )
    
    try:
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
    
    # Convertir imagen a base64
    img_stream.seek(0)
    base64_image = base64.b64encode(img_stream.read()).decode('utf-8')
    
    try:
        # Usar el agente DSPy para análisis inteligente
        agent = get_agent()
        context = "Analiza esta imagen de comida. Muchas imágenes serán sobre comida tradicional de diferentes culturas."
        
        agent_result = agent.analyze_image(base64_image, context=context)
        
        if not agent_result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Error del agente: {agent_result.get('error', 'Unknown error')}"
            )
        
        # Guardar en base de datos
        analysis_id = db.save_analysis(
            db_conn,
            dish_name=agent_result["dish_name"],
            ingredients=agent_result["ingredients"],
            recipe_steps=agent_result["recipe_steps"],
            fun_facts=agent_result["fun_facts"]
        )
        
        # Retornar resultado estructurado
        return FoodAnalysisResponse(
            nombre_plato=agent_result["dish_name"],
            receta=Recipe(
                ingredientes=agent_result["ingredients"],
                pasos=agent_result["recipe_steps"]
            ),
            datos_curiosos=agent_result["fun_facts"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al analizar la imagen: {str(e)}"
        )


@app.get("/substitutes")
async def get_substitutes(ingredient: str, context: str = ""):
    """
    Obtiene sustitutos para un ingrediente usando el agente.
    
    Args:
        ingredient: Ingrediente a sustituir
        context: Contexto adicional (vegano, sin gluten, etc.)
    """
    try:
        result = get_ingredient_substitutes(ingredient, context)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al buscar sustitutos: {str(e)}"
        )


@app.get("/nutrition/{dish_name}")
async def get_nutrition(dish_name: str, ingredients: str = None):
    """
    Calcula información nutricional para un plato usando el agente.
    
    Args:
        dish_name: Nombre del plato
        ingredients: Lista de ingredientes separados por coma (opcional)
    """
    try:
        ingredient_list = ingredients.split(",") if ingredients else None
        result = calculate_nutrition(dish_name, ingredient_list)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al calcular nutrición: {str(e)}"
        )


@app.get("/compare")
async def compare_two_dishes(analysis_id1: int, analysis_id2: int):
    """
    Compara dos platos de la base de datos usando el agente.
    
    Args:
        analysis_id1: ID del primer análisis guardado
        analysis_id2: ID del segundo análisis guardado
    """
    try:
        result = compare_dishes_from_db(analysis_id1, analysis_id2, db_conn)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al comparar platos: {str(e)}"
        )


@app.get("/history")
async def get_history(limit: int = 10):
    """
    Obtiene el historial de análisis de comida.
    
    Args:
        limit: Número máximo de registros a retornar (default: 10)
    """
    try:
        history = db.get_analysis_history(db_conn, limit=limit)
        return {"history": history, "count": len(history)}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener historial: {str(e)}"
        )


@app.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: int):
    """
    Obtiene un análisis específico por ID.
    
    Args:
        analysis_id: ID del análisis
    """
    try:
        analysis = db.get_analysis_by_id(db_conn, analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Análisis no encontrado")
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener análisis: {str(e)}"
        )


@app.get("/")
def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "Food Analyzer Agent API",
        "version": "3.0.0",
        "description": "API con agente inteligente DSPy + Base de datos SQLite",
        "endpoints": {
            "POST /analyze_food": "Analiza una imagen de comida y la guarda en BD",
            "GET /substitutes": "Obtiene sustitutos para ingredientes",
            "GET /nutrition/{dish_name}": "Calcula información nutricional",
            "GET /compare?analysis_id1=X&analysis_id2=Y": "Compara dos platos guardados en BD",
            "GET /history": "Obtiene historial de análisis guardados",
            "GET /analysis/{id}": "Obtiene un análisis específico por ID"
        },
        "database": "food_analyzer.db",
        "storage": "Solo análisis de comida"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("food_analyzer_api:app", host="0.0.0.0", port=8000, reload=True)
