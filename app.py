from google import genai
from google.genai import types
from PIL import Image
from pydantic import BaseModel, Field
import streamlit as st
import json

client = genai.Client()

st.set_page_config(page_title="AI Трекер Калорий", page_icon="🥗", layout="centered")

st.title("🥗 AI Трекер Калорий")
st.write("Загрузи фото еды, а ИИ посчитает калории и добавит их в дневник!")

if "daily_meals" not in st.session_state:
    st.session_state.daily_meals = []

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

uploaded_file = st.file_uploader("Загрузи фото еды (jpg, png)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Твое блюдо", use_column_width=True)
    
    if st.button("✨ Распознать и посчитать калории"):
        with st.spinner("ИИ анализирует тарелку..."):
            try:
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
                
                result_data = json.loads(response.text)
                st.session_state.daily_meals.append(result_data)
                st.success("Блюдо успешно добавлено в дневник!")
                
            except Exception as e:
                st.error(f"Произошла ошибка: {e}")

st.markdown("---")
st.subheader("📊 Дневник питания за сегодня")

if st.session_state.daily_meals:
    total_day_calories = sum(meal.get("total_calories", 0) for meal in st.session_state.daily_meals)
    
    st.metric(label="🔥 Всего калорий за день", value=f"{total_day_calories} ккал")
    
    for idx, meal in enumerate(st.session_state.daily_meals, 1):
        with st.expander(f"Прием пищи #{idx} — {meal.get('total_calories', 0)} ккал"):
            for item in meal.get("items", []):
                st.write(f"- **{item['name']}** ({item['weight_grams']} г): {item['calories']} ккал | Б: {item['protein']}г, Ж: {item['fat']}г, У: {item['carbs']}г")
    
    if st.button("🗑️ Очистить дневник"):
        st.session_state.daily_meals = []
        st.rerun()
else:
    st.info("Ты еще ничего не добавила за сегодня. Загрузи фото выше!")