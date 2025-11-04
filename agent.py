from openai import OpenAI
import dspy
from typing import List, Dict, Any, Optional
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# SIGNATURES

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
    
    def __init__(self):
        super().__init__()
        
        self.analyze_food = dspy.ChainOfThought(AnalyzeFoodImageSignature)
        self.calculate_nutrition = dspy.ChainOfThought(CalculateNutritionSignature)
        self.compare_dishes = dspy.ChainOfThought(CompareDishesSignature)
    
    def analyze_image(self, image_base64: str, context: str = "") -> Dict[str, Any]:
        try:
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
            
            # Parse vision response
            content = vision_response.choices[0].message.content
            
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()
            
            vision_result = json.loads(json_str)
            
            # Now use DSPy agent to add reasoning and structure
            image_description = f"Analyzed dish: {vision_result.get('dish_name', 'unknown')}"
            if context:
                image_description += f". Context: {context}"
            
            prediction = self.analyze_food(image_description=image_description)
            
            return {
                "success": True,
                "dish_name": vision_result["dish_name"],
                "ingredients": vision_result["ingredients"],
                "recipe_steps": vision_result["recipe_steps"],
                "fun_facts": vision_result["fun_facts"],
                "agent_reasoning": prediction.rationale if hasattr(prediction, 'rationale') else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    
    
    def get_nutrition(self, dish_name: str, ingredients: List[str] = None) -> Dict[str, Any]:
        try:
            ingredients_str = ", ".join(ingredients) if ingredients else "standard ingredients"
            
            prediction = self.calculate_nutrition(
                dish_name=dish_name,
                ingredients=ingredients_str
            )
            
            # Parse nutrition data
            if hasattr(prediction, 'nutrition'):
                if isinstance(prediction.nutrition, dict):
                    nutrition = prediction.nutrition
                else:
                    try:
                        nutrition = json.loads(prediction.nutrition)
                    except:
                        nutrition = {}
            else:
                nutrition = {}
            
            return {
                "success": True,
                "dish_name": dish_name,
                "nutrition": nutrition,
                "agent_reasoning": prediction.rationale if hasattr(prediction, 'rationale') else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def compare(self, dish1_name: str, dish1_ingredients: List[str],
                dish2_name: str, dish2_ingredients: List[str]) -> Dict[str, Any]:
        try:
            prediction = self.compare_dishes(
                dish1_name=dish1_name,
                dish1_ingredients=", ".join(dish1_ingredients),
                dish2_name=dish2_name,
                dish2_ingredients=", ".join(dish2_ingredients)
            )
            
            if hasattr(prediction, 'comparison'):
                if isinstance(prediction.comparison, dict):
                    comparison = prediction.comparison
                else:
                    try:
                        comparison = json.loads(prediction.comparison)
                    except:
                        comparison = {}
            else:
                comparison = {}
            
            return {
                "success": True,
                "comparison": comparison,
                "agent_reasoning": prediction.rationale if hasattr(prediction, 'rationale') else None
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
    
