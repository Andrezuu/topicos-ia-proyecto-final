"""
Tools module for Food Analyzer Agent
Contains utility functions that the agent uses
"""

from typing import Dict, Any, List
from agent import get_agent
import database as db


def get_ingredient_substitutes(ingredient: str, context: str = "") -> Dict[str, Any]:
    """
    Get substitutes for an ingredient using the agent (no cache).
    
    Args:
        ingredient: The ingredient to find substitutes for
        context: Optional context (dietary restrictions, cuisine, etc.)
    
    Returns:
        Dictionary with substitutes and agent reasoning
    """
    agent = get_agent()
    result = agent.get_substitutes(ingredient, context)
    
    if result["success"]:
        return {
            "ingredient": result["ingredient"],
            "category": result.get("category", "general"),
            "substitutes": result["substitutes"],
            "agent_reasoning": result.get("agent_reasoning"),
            "source": "agent"
        }
    else:
        raise Exception(f"Agent error: {result.get('error', 'Unknown error')}")


def calculate_nutrition(dish_name: str, ingredients: List[str] = None) -> Dict[str, Any]:
    """
    Calculate nutritional information for a dish using the agent (no cache).
    
    Args:
        dish_name: Name of the dish
        ingredients: Optional list of ingredients
    
    Returns:
        Dictionary with nutrition data and agent reasoning
    """
    agent = get_agent()
    result = agent.get_nutrition(dish_name, ingredients)
    
    if result["success"]:
        return {
            "dish_name": result["dish_name"],
            "nutrition": result["nutrition"],
            "agent_reasoning": result.get("agent_reasoning"),
            "source": "agent"
        }
    else:
        raise Exception(f"Agent error: {result.get('error', 'Unknown error')}")


def compare_dishes_from_db(analysis_id1: int, analysis_id2: int, conn) -> Dict[str, Any]:
    """
    Compare two dishes from the database using the agent.
    
    Args:
        analysis_id1: ID of first analysis
        analysis_id2: ID of second analysis
        conn: Database connection
    
    Returns:
        Dictionary with comparison and agent reasoning
    """
    # Get both analyses from database
    analysis1 = db.get_analysis_by_id(conn, analysis_id1)
    analysis2 = db.get_analysis_by_id(conn, analysis_id2)
    
    if not analysis1:
        raise Exception(f"Análisis con ID {analysis_id1} no encontrado")
    if not analysis2:
        raise Exception(f"Análisis con ID {analysis_id2} no encontrado")
    
    # Use agent to compare
    agent = get_agent()
    result = agent.compare(
        analysis1["dish_name"],
        analysis1["ingredients"],
        analysis2["dish_name"],
        analysis2["ingredients"]
    )
    
    if result["success"]:
        return {
            "dish1": {
                "id": analysis1["id"],
                "name": analysis1["dish_name"],
                "ingredients": analysis1["ingredients"]
            },
            "dish2": {
                "id": analysis2["id"],
                "name": analysis2["dish_name"],
                "ingredients": analysis2["ingredients"]
            },
            "comparison": result["comparison"],
            "agent_reasoning": result.get("agent_reasoning"),
            "source": "database"
        }
    else:
        raise Exception(f"Agent error: {result.get('error', 'Unknown error')}")


# Test functions
if __name__ == "__main__":
    print("🔧 Testing Food Analyzer Tools")
    print("=" * 50)
    
    # Test substitutes
    print("\n1. Testing substitutes...")
    result = get_ingredient_substitutes("huevo", context="vegano")
    print(f"Ingredient: {result['ingredient']}")
    print(f"Category: {result['category']}")
    print(f"Substitutes: {len(result['substitutes'])} found")
    
    # Test nutrition
    print("\n2. Testing nutrition...")
    result = calculate_nutrition("sopa de quinua", ["quinua", "papa", "zanahoria"])
    print(f"Dish: {result['dish_name']}")
    print(f"Nutrition data: {result['nutrition']}")
