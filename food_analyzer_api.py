import io
import base64
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image, UnidentifiedImageError
from dotenv import load_dotenv
from agent import get_agent
from tools import get_ingredient_substitutes, calculate_nutrition, compare_dishes

load_dotenv()

app = FastAPI(
    title="Food Analyzer Agent API",
    version="3.0.0",
    description="API con agente inteligente DSPy para análisis de comida"
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
async def compare_two_dishes(
    dish1_name: str,
    dish1_ingredients: str,
    dish2_name: str,
    dish2_ingredients: str
):
    """
    Compara dos platos usando el agente.
    
    Args:
        dish1_name: Nombre del primer plato
        dish1_ingredients: Ingredientes del primer plato (separados por coma)
        dish2_name: Nombre del segundo plato
        dish2_ingredients: Ingredientes del segundo plato (separados por coma)
    """
    try:
        dish1_ing_list = [i.strip() for i in dish1_ingredients.split(",")]
        dish2_ing_list = [i.strip() for i in dish2_ingredients.split(",")]
        
        result = compare_dishes(
            dish1_name, dish1_ing_list,
            dish2_name, dish2_ing_list
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al comparar platos: {str(e)}"
        )


@app.get("/")
def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "Food Analyzer Agent API",
        "version": "3.0.0",
        "description": "API con agente inteligente DSPy",
        "endpoints": {
            "POST /analyze_food": "Analiza una imagen de comida",
            "GET /substitutes": "Obtiene sustitutos para ingredientes",
            "GET /nutrition/{dish_name}": "Calcula información nutricional",
            "GET /compare": "Compara dos platos"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("food_analyzer_api:app", host="0.0.0.0", port=8000, reload=True)
