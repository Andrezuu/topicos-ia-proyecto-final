"""
Tools module for Food Analyzer Agent
Contains utility functions that the agent uses
"""

from typing import Dict, Any, List
from agent import get_agent


def get_ingredient_substitutes(ingredient: str, context: str = "") -> Dict[str, Any]:
    """
    Get substitutes for an ingredient using the agent.
    
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
    Calculate nutritional information for a dish using the agent.
    
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


def compare_dishes(dish1_name: str, dish1_ingredients: List[str],
                   dish2_name: str, dish2_ingredients: List[str]) -> Dict[str, Any]:
    """
    Compare two dishes using the agent.
    
    Args:
        dish1_name: Name of first dish
        dish1_ingredients: Ingredients of first dish
        dish2_name: Name of second dish
        dish2_ingredients: Ingredients of second dish
    
    Returns:
        Dictionary with comparison and agent reasoning
    """
    agent = get_agent()
    result = agent.compare(dish1_name, dish1_ingredients, dish2_name, dish2_ingredients)
    
    if result["success"]:
        return {
            "comparison": result["comparison"],
            "agent_reasoning": result.get("agent_reasoning"),
            "source": "agent"
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
