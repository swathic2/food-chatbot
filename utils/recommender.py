import pandas as pd

# Load your dataset
df = pd.read_csv("data/recipes.csv")

def recommend_recipes(user_ingredients):
    user_ingredients = [x.strip().lower() for x in user_ingredients]

    def matches(row):
        ingredients = row["ingredients"].lower()
        return all(item in ingredients for item in user_ingredients)

    matched = df[df.apply(matches, axis=1)]

    results = []
    for _, row in matched.iterrows():
        results.append({
            "title": row["title"],
            "image": row["image_name"],
            "ingredients": row["ingredients"],
            "instructions": row["instructions"]
        })
    return results
