import pandas as pd
import json
import os
import google.generativeai as genai
from sklearn.metrics import accuracy_score, confusion_matrix
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("WARNING: GEMINI_API_KEY not found in environment variables. Calls will fail.")
else:
    genai.configure(api_key=api_key)

def get_gemini_response(prompt, model_name="gemini-2.0-flash"):
    """
    Helper to call Gemini API.
    """
    if not api_key:
        # Return dummy response for testing without key
        return "{\n  \"predicted_stars\": 3,\n  \"explanation\": \"API Key missing, dummy response.\"\n}"
    
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return None

# --- Prompt Designs ---

def prompt_zero_shot(review_text):
    return f"""
    Classify the following Yelp review into a 1-5 star rating.
    Return the result as a valid JSON object with keys "predicted_stars" (integer) and "explanation" (string).
    
    Review: "{review_text}"
    """

def prompt_chain_of_thought(review_text):
    return f"""
    Analyze the sentiment of this Yelp review step-by-step to determine the star rating (1-5).
    First, identify the positive and negative aspects mentioned.
    Then, weigh them to decide the final rating.
    Finally, format your output as a valid JSON object with the keys:
    - "predicted_stars": (integer)
    - "explanation": (string, your reasoning)
    
    Review: "{review_text}"
    """

def prompt_structured_few_shot(review_text):
    # Including a few examples to guide the model
    return f"""
    You are an expert sentiment analyzer. Rate the following Yelp review from 1 to 5 stars.
    
    Examples:
    Review: "The food was disgusting and cold." -> {{"predicted_stars": 1, "explanation": "Strong negative sentiment about food quality."}}
    Review: "Amazing experience, will definitely come back!" -> {{"predicted_stars": 5, "explanation": "Strong positive enthusiasm and loyalty."}}
    Review: "It was okay, but a bit pricey." -> {{"predicted_stars": 3, "explanation": "Mixed sentiment: quality acceptable but value mismatch."}}
    
    Task:
    Review: "{review_text}"
    
    Return ONLY the valid JSON object.
    """

# --- Evaluation Logic ---

def parse_response(response_text):
    try:
        # Clean up markdown code blocks if present
        cleaned_text = response_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        
        data = json.loads(cleaned_text)
        return data.get("predicted_stars"), data.get("explanation"), True
    except Exception:
        return None, None, False

def run_experiment(df, prompt_func, prompt_name):
    print(f"Running experiment: {prompt_name}")
    results = []
    valid_json_count = 0
    
    # Process a subset for testing if needed, or full df
    # Using first 10 for quick test if df is large, but user wants ~200.
    # We will use the full df provided (mock is small, real is large)
    # If df > 200, sample 200
    target_df = df if len(df) <= 200 else df.sample(200, random_state=42)
    
    for i, row in target_df.iterrows():
        text = row['text']
        original_stars = row['stars']
        
        prompt = prompt_func(text)
        response_text = get_gemini_response(prompt)
        
        predicted_stars, explanation, is_valid = parse_response(response_text if response_text else "")
        
        if is_valid:
            valid_json_count += 1
        else:
            predicted_stars = 0 # Invalid
            
        results.append({
            "original_stars": original_stars,
            "predicted_stars": predicted_stars,
            "explanation": explanation,
            "is_valid_json": is_valid,
            "prompt_version": prompt_name
        })
        
        # Rate limit protection
        time.sleep(1)

    results_df = pd.DataFrame(results)
    
    # Calculate Metrics
    valid_results = results_df[results_df["is_valid_json"] == True]
    accuracy = 0
    if not valid_results.empty:
        accuracy = accuracy_score(valid_results["original_stars"].astype(int), valid_results["predicted_stars"].astype(int))
    
    print(f"Results for {prompt_name}:")
    print(f"Accuracy: {accuracy:.2f}")
    print(f"JSON Validity Rate: {valid_json_count/len(target_df):.2f}")
    print("-" * 30)
    
    return results_df

def main():
    try:
        df = pd.read_csv("task1/yelp.csv")
    except FileNotFoundError:
        print("Error: task1/yelp.csv not found. Please place the dataset file.")
        return

    # Basic cleanup
    # Ensure stars and text columns exist
    # The kaggle dataset might represent stars as 'stars' and text as 'text'
    if 'stars' not in df.columns or 'text' not in df.columns:
        print("Error: Dataset must contain 'stars' and 'text' columns.")
        # print(df.columns)
        return

    all_results = []
    
    # 1. Zero Shot
    res_v1 = run_experiment(df, prompt_zero_shot, "Zero-Shot")
    all_results.append(res_v1)
    
    # 2. Chain of Thought
    res_v2 = run_experiment(df, prompt_chain_of_thought, "Chain-of-Thought")
    all_results.append(res_v2)
    
    # 3. Few Shot Structured
    res_v3 = run_experiment(df, prompt_structured_few_shot, "Few-Shot-Structured")
    all_results.append(res_v3)
    
    # Save Combined Results
    final_df = pd.concat(all_results)
    final_df.to_csv("task1/evaluation_results.csv", index=False)
    print("Evaluation Complete. Results saved to task1/evaluation_results.csv")

if __name__ == "__main__":
    main()
