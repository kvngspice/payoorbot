import requests
import openai
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables
# Load .env file from the current directory
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ensure API keys are present
if not BOT_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Missing BOT_TOKEN or OPENAI_API_KEY. Please check your .env file.")

openai.api_key = OPENAI_API_KEY

def generate_openai_response(prompt, system_role):
    """Generate a response from OpenAI API with error handling."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": system_role},
                      {"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error generating response: {str(e)}"

def generate_nigerian_recipe(meal_name):
    prompt = f"Provide an authentic Nigerian recipe for {meal_name}, including ingredients and step-by-step instructions."
    return generate_openai_response(prompt, "You are a Nigerian chef providing traditional recipes.")

def generate_nigerian_meal_plan(region, calories, allergies, days, prioritized_class=None, budget=None):
    allergies_str = ", ".join(allergies) if allergies else "none"
    prompt = (f"Create a {days}-day meal plan with {calories} calories per day for someone in {region}. "
              f"Avoid foods containing {allergies_str}. Include traditional Nigerian dishes.")
    if prioritized_class:
        prompt += f" Prioritize meals rich in {prioritized_class}."
    if budget:
        prompt += f" Keep the budget under {budget} Naira."
    
    return generate_openai_response(prompt, "You are a meal planner specializing in Nigerian cuisine.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
    "Hello! 🇳🇬🍲 Welcome to the Payoor bot. Here’s what I can do:\n\n"
    "1️⃣ **/recipe [meal_name]** - Get a detailed Nigerian recipe.\n"
    "2️⃣ **/mealplan [region] [calories] [allergies] [days] [prioritized_class (optional)] [budget (optional)]**\n"
    "3️⃣ **/ask [question]** - Get answers to cooking-related questions.\n"
    "4️⃣ **/nutritional_value [meal_name]** - Get the nutritional breakdown of a Nigerian meal.\n"
    "5️⃣ **/help** - See available commands."
)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def recipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please specify a meal. Example: `/recipe Jollof Rice`")
        return
    meal_name = " ".join(context.args)
    ai_recipe = generate_nigerian_recipe(meal_name)
    await update.message.reply_text(ai_recipe)

async def meal_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 4:
        await update.message.reply_text("Usage: /mealplan [region] [calories] [allergies] [days] [prioritized_class (optional)] [budget (optional)]")
        return
    
    region = context.args[0]
    calories = int(context.args[1])
    allergies = context.args[2].split(",") if context.args[2].lower() != "none" else []
    days = int(context.args[3])
    prioritized_class = context.args[4] if len(context.args) > 4 else None
    budget = int(context.args[5]) if len(context.args) > 5 else None
    
    meal_plan = generate_nigerian_meal_plan(region, calories, allergies, days, prioritized_class, budget)
    await update.message.reply_text(f"Your {days}-day Nigerian meal plan:\n\n{meal_plan}")
async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please ask a cooking-related question. Example: `/ask How do I make puff puff?`")
        return
    
    question = " ".join(context.args)
    answer = generate_openai_response(question, "You are a Nigerian chef answering cooking questions.")
    await update.message.reply_text(answer)

async def nutritional_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please specify a food item. Example: `/nutritional_value Jollof Rice`")
        return
    
    meal_name = " ".join(context.args)
    prompt = f"Provide the nutritional value of {meal_name}, including calories, protein, fat, and relevant nutrients."
    nutritional_info = generate_openai_response(prompt, "You are a Nigerian nutrition expert.")
    await update.message.reply_text(nutritional_info)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")
    await update.message.reply_text("Oops, something went wrong. Please try again.")

if __name__ == "__main__":
    print("Starting bot...")
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("recipe", recipe))
    app.add_handler(CommandHandler("mealplan", meal_plan))
    app.add_handler(CommandHandler("ask", ask))
    app.add_handler(CommandHandler("nutritional_value", nutritional_value))
    app.add_error_handler(error)

    print("Polling...")
    app.run_polling(poll_interval=3)
