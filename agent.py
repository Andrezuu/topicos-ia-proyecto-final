from openai import OpenAI
import dspy
from typing import List, Dict, Any, Optional
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# ============= TOOLS =============

class AnalyzeFoodTool:
    name = "analyze_food_image"
    description = "Analiza una imagen de comida para identificar el plato, ingredientes, receta y datos curiosos"
    
    def __call__(self, image_base64: str, context: str = "") -> Dict[str, Any]:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        vision_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analiza esta imagen de comida y proporciona:
1. Nombre del plato
2. Lista de ingredientes principales (como lista de strings)
3. Pasos de la receta (como lista de strings)
4. 3-5 datos curiosos sobre el plato (como lista de strings)

Responde en formato JSON con esta estructura exacta:
{
    "dish_name": "nombre del plato",
    "ingredients": ["ingrediente1", "ingrediente2", ...],
    "recipe_steps": ["paso1", "paso2", ...],
    "fun_facts": ["dato1", "dato2", ...]
}"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )
        
        content = vision_response.choices[0].message.content
        
        # Extract JSON from response (handle markdown code blocks)
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0].strip()
        else:
            json_str = content.strip()
        
        return json.loads(json_str)


class NutritionCalculatorTool:
    
    name = "calculate_nutrition"
    description = "Calcula información nutricional de un plato basándose en sus ingredientes"
    
    def __call__(self, dish_name: str, ingredients: List[str]) -> Dict[str, Any]:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        ingredients_str = ", ".join(ingredients) if ingredients else "ingredientes estándar"
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un experto nutricionista. Proporciona estimaciones nutricionales precisas y realistas."
                },
                {
                    "role": "user",
                    "content": f"""Calcula la información nutricional para una porción estándar de:

Plato: {dish_name}
Ingredientes: {ingredients_str}

Responde en formato JSON con esta estructura:
{{
    "serving_size": "tamaño de la porción (ej: 1 plato, 200g)",
    "calories": número_de_calorías,
    "proteins": gramos_de_proteína,
    "carbs": gramos_de_carbohidratos,
    "fats": gramos_de_grasas,
    "fiber": gramos_de_fibra,
    "notes": "notas adicionales relevantes"
}}"""
                }
            ],
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0].strip()
        else:
            json_str = content.strip()
        
        return json.loads(json_str)


class DishComparisonTool:
    
    name = "compare_dishes"
    description = "Compara dos platos cultural, nutricional y culinariamente"
    
    def __call__(self, dish1: Dict[str, Any], dish2: Dict[str, Any]) -> Dict[str, Any]:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        dish1_ingredients = ", ".join(dish1['ingredients']) if isinstance(dish1['ingredients'], list) else dish1['ingredients']
        dish2_ingredients = ", ".join(dish2['ingredients']) if isinstance(dish2['ingredients'], list) else dish2['ingredients']
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un experto en gastronomía comparativa y análisis culinario transcultural."
                },
                {
                    "role": "user",
                    "content": f"""Compara estos dos platos en detalle:

Plato 1: {dish1['name']}
Ingredientes: {dish1_ingredients}

Plato 2: {dish2['name']}
Ingredientes: {dish2_ingredients}

Responde en formato JSON:
{{
    "similarity_score": número_del_0_al_100,
    "common_ingredients": ["ingrediente1", "ingrediente2"],
    "unique_to_dish1": ["ingrediente_exclusivo_1"],
    "unique_to_dish2": ["ingrediente_exclusivo_1"],
    "culinary_relationship": "descripción de la relación culinaria entre ambos platos",
    "cultural_context": "contexto cultural y origen de cada plato",
    "key_differences": ["diferencia1", "diferencia2", "diferencia3"]
}}"""
                }
            ],
            max_tokens=800
        )
        
        content = response.choices[0].message.content
        
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0].strip()
        else:
            json_str = content.strip()
        
        return json.loads(json_str)


# ============= SIGNATURES =============

class AnalyzeFoodImageSignature(dspy.Signature):
    """
    Analiza una imagen de comida para identificar el plato, ingredientes, receta y datos curiosos.
    Usa capacidades de visión para entender el contenido visual.
    """
    image_description: str = dspy.InputField(desc="Descripción o contexto sobre la imagen de comida")
    dish_name: str = dspy.OutputField(desc="Nombre del plato identificado en la imagen")
    ingredients: List[str] = dspy.OutputField(desc="Lista de ingredientes principales del plato")
    recipe_steps: List[str] = dspy.OutputField(desc="Pasos de la receta paso a paso")
    fun_facts: List[str] = dspy.OutputField(desc="3-5 datos curiosos sobre el plato")


class CalculateNutritionSignature(dspy.Signature):
    """
    Calcula información nutricional para un plato basándose en sus ingredientes.
    Proporciona estimaciones de calorías, macronutrientes y otros datos nutricionales.
    """
    dish_name: str = dspy.InputField(desc="Nombre del plato")
    ingredients: str = dspy.InputField(desc="Lista de ingredientes separados por comas")
    nutrition: Dict[str, Any] = dspy.OutputField(
        desc="Datos nutricionales incluyendo calorías, proteínas, carbohidratos, grasas, fibra y tamaño de porción"
    )


class CompareDishesSignature(dspy.Signature):
    """
    Compara dos platos cultural, nutricional y culinariamente para encontrar similitudes
    y diferencias.
    """
    dish1_name: str = dspy.InputField(desc="Nombre del primer plato")
    dish1_ingredients: str = dspy.InputField(desc="Ingredientes del primer plato")
    dish2_name: str = dspy.InputField(desc="Nombre del segundo plato")
    dish2_ingredients: str = dspy.InputField(desc="Ingredientes del segundo plato")
    comparison: Dict[str, Any] = dspy.OutputField(
        desc="Comparación incluyendo similarity_score, culinary_relationship, cultural_context y key_differences"
    )


# ============= AGENT MODULE =============

class FoodAnalyzerAgent(dspy.Module):
    """
    Agente principal para análisis de comida usando DSPy.
    Combina Tools (ejecución) con Signatures (razonamiento) para proporcionar
    análisis inteligentes de comida, nutrición y comparaciones.
    """
    
    def __init__(self):
        super().__init__()
        
        # Inicializar Tools
        self.analyze_tool = AnalyzeFoodTool()
        self.nutrition_tool = NutritionCalculatorTool()
        self.comparison_tool = DishComparisonTool()
        
        # Inicializar Signatures para razonamiento DSPy
        self.analyze_food = dspy.ChainOfThought(AnalyzeFoodImageSignature)
        self.calculate_nutrition = dspy.ChainOfThought(CalculateNutritionSignature)
        self.compare_dishes = dspy.ChainOfThought(CompareDishesSignature)
    
    def analyze_image(self, image_base64: str, context: str = "") -> Dict[str, Any]:
        try:
            # 1. Ejecutar tool para obtener análisis crudo
            raw_result = self.analyze_tool(image_base64, context)
            
            # 2. Usar DSPy ChainOfThought para añadir razonamiento estructurado
            image_description = f"Plato analizado: {raw_result['dish_name']}"
            if context:
                image_description += f". Contexto: {context}"
            
            prediction = self.analyze_food(image_description=image_description)
            
            return {
                "success": True,
                "dish_name": raw_result["dish_name"],
                "ingredients": raw_result["ingredients"],
                "recipe_steps": raw_result["recipe_steps"],
                "fun_facts": raw_result["fun_facts"],
                "agent_reasoning": prediction.rationale if hasattr(prediction, 'rationale') else None,
                "tool_used": self.analyze_tool.name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    
    def get_nutrition(self, dish_name: str, ingredients: List[str] = None) -> Dict[str, Any]:
        try:
            # 1. Ejecutar tool para calcular nutrición
            if not ingredients:
                ingredients = ["ingredientes estándar"]
            
            nutrition_data = self.nutrition_tool(dish_name, ingredients)
            
            # 2. Usar DSPy ChainOfThought para añadir contexto y razonamiento
            ingredients_str = ", ".join(ingredients)
            prediction = self.calculate_nutrition(
                dish_name=dish_name,
                ingredients=ingredients_str
            )
            
            return {
                "success": True,
                "dish_name": dish_name,
                "nutrition": nutrition_data,
                "agent_reasoning": prediction.rationale if hasattr(prediction, 'rationale') else None,
                "tool_used": self.nutrition_tool.name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def compare(self, dish1_name: str, dish1_ingredients: List[str],
                dish2_name: str, dish2_ingredients: List[str]) -> Dict[str, Any]:
        try:
            # 1. Ejecutar tool para comparar platos
            dish1 = {"name": dish1_name, "ingredients": dish1_ingredients}
            dish2 = {"name": dish2_name, "ingredients": dish2_ingredients}
            
            comparison_data = self.comparison_tool(dish1, dish2)
            
            # 2. Usar DSPy ChainOfThought para añadir análisis profundo
            prediction = self.compare_dishes(
                dish1_name=dish1_name,
                dish1_ingredients=", ".join(dish1_ingredients),
                dish2_name=dish2_name,
                dish2_ingredients=", ".join(dish2_ingredients)
            )
            
            return {
                "success": True,
                "comparison": comparison_data,
                "agent_reasoning": prediction.rationale if hasattr(prediction, 'rationale') else None,
                "tool_used": self.comparison_tool.name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


#SINGLETON
_agent_instance = None

def get_agent() -> FoodAnalyzerAgent:
    global _agent_instance
    
    if _agent_instance is None:
        # Configure DSPy with OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        lm = dspy.LM('openai/gpt-4o-mini', api_key=api_key)
        dspy.configure(lm=lm)
        
        # Create agent instance
        _agent_instance = FoodAnalyzerAgent()
    
    return _agent_instance


if __name__ == "__main__":
    print("🧠 Food Analyzer Agent - DSPy")
    agent = get_agent()
    
