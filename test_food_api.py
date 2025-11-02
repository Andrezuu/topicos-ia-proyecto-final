"""
Script de prueba simple para verificar la API de Food Analyzer
"""
import requests
import sys
from pathlib import Path

def test_api(image_path: str, api_url: str = "http://localhost:8000"):
    """
    Prueba el endpoint de análisis de comida
    
    Args:
        image_path: Ruta a la imagen a analizar
        api_url: URL base de la API
    """
    # Verificar que la imagen existe
    if not Path(image_path).exists():
        print(f"❌ Error: No se encontró la imagen en {image_path}")
        return False
    
    print(f"📤 Enviando imagen: {image_path}")
    print(f"🌐 API URL: {api_url}/analyze_food")
    
    try:
        with open(image_path, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{api_url}/analyze_food", files=files, timeout=30)
        
        if response.status_code == 200:
            print("✅ Respuesta exitosa!\n")
            result = response.json()
            
            print(f"🍽️  Plato: {result['nombre_plato']}\n")
            
            print("📝 Ingredientes:")
            for ing in result['receta']['ingredientes']:
                print(f"   • {ing}")
            
            print("\n👨‍🍳 Pasos de preparación:")
            for i, paso in enumerate(result['receta']['pasos'], 1):
                print(f"   {i}. {paso}")
            
            print("\n💡 Datos curiosos:")
            for dato in result['datos_curiosos']:
                print(f"   • {dato}")
            
            return True
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar a la API")
        print("   Asegúrate de que el servidor esté corriendo en http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_food_api.py <ruta_a_imagen>")
        print("\nEjemplo:")
        print("  python test_food_api.py mi_comida.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    success = test_api(image_path)
    sys.exit(0 if success else 1)
