from google import genai
from google.genai import types
from PIL import Image
from pydantic import BaseModel, Field

client = genai.Client()

class FoodItem(BaseModel):
    name: str = Field(description="Название продукта или блюда")
    weight_grams: int = Field(description="Примерный вес порции в граммах")
    calories: int = Field(description="Количество калорий (ккал)")
    protein: float = Field(description="Белки в граммах")
    fat: float = Field(description="Жиры в граммах")
    carbs: float = Field(description="Углеводы в граммах")

class MealAnalysis(BaseModel):
    items: list[FoodItem] = Field(description="Список распознанных продуктов на тарелке")
    total_calories: int = Field(description="Общая калорийность приема пищи")

def analyze_food_image(image_path: str):
    image = Image.open(image_path)
    
    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=[
            image,
            "Ты профессиональный нутрициолог. Проанализируй фото еды, определи составляющие, вес и КБЖУ."
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=MealAnalysis,
        ),
    )
    return response.text

if __name__ == "__main__":
    result = analyze_food_image("food.jpg")
    print(result)