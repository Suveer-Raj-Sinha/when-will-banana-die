"""
recipes.py  —  Recipe Suggestions & Storage Knowledge Base
===========================================================
Imported by main.py for the /recipes endpoint.
Also used by predict.py for detailed storage tips.
"""

# ─────────────────────────────────────────────
# DETAILED STORAGE KNOWLEDGE BASE
# ─────────────────────────────────────────────
STORAGE_TIPS = {
    "apples": {
        "short":       "Refrigerate to extend shelf life significantly.",
        "temperature": "Store at 0–4°C (32–40°F) in the refrigerator.",
        "humidity":    "Keep in a high-humidity drawer to prevent shriveling.",
        "avoid":       "Keep away from other fruits — apples release ethylene gas which speeds up ripening of nearby produce.",
        "signs":       "Soft spots, wrinkled skin, or a fermented smell indicate spoilage.",
        "tip":         "Wrap individually in newspaper if storing for longer periods.",
    },
    "banana": {
        "short":       "Keep at room temperature away from direct sunlight.",
        "temperature": "Best at 13–15°C (55–60°F). Never refrigerate unripe bananas.",
        "humidity":    "Normal room humidity is fine. Avoid very dry conditions.",
        "avoid":       "Do not store next to apples or avocados — ethylene gas will over-ripen them quickly.",
        "signs":       "Black skin with soft, mushy flesh means overripe. Small brown spots are fine and actually sweeter.",
        "tip":         "Once ripe, you can refrigerate — the skin turns black but the fruit inside stays good for 2–3 more days.",
    },
    "bittergroud": {
        "short":       "Refrigerate in a paper bag and use within a few days.",
        "temperature": "Store at 10–12°C (50–54°F).",
        "humidity":    "Wrap in a damp paper towel to maintain moisture.",
        "avoid":       "Do not wash before storing — moisture accelerates decay.",
        "signs":       "Yellowing skin, soft spots, or sliminess indicate it is past its best.",
        "tip":         "Best consumed when dark green. Once it starts turning orange-yellow it becomes very bitter.",
    },
    "capsicum": {
        "short":       "Store in the crisper drawer of the refrigerator.",
        "temperature": "Best at 7–10°C (45–50°F).",
        "humidity":    "High humidity drawer is ideal. Do not seal in an airtight bag.",
        "avoid":       "Keep away from ethylene-producing fruits like apples and bananas.",
        "signs":       "Wrinkled skin, soft spots, or mold around the stem signal spoilage.",
        "tip":         "Red and yellow capsicums spoil faster than green ones as they are more ripe when harvested.",
    },
    "cucumber": {
        "short":       "Refrigerate and consume quickly, especially once cut.",
        "temperature": "Store at 10–13°C (50–55°F). Cucumbers are sensitive to cold damage below 10°C.",
        "humidity":    "Wrap in a paper towel and place in a loose bag to absorb excess moisture.",
        "avoid":       "Keep away from tomatoes, bananas, and melons — very sensitive to ethylene gas.",
        "signs":       "Mushy ends, yellow skin, or a slimy surface mean it has gone bad.",
        "tip":         "Store with the cut end wrapped tightly in cling film to extend freshness.",
    },
    "okra": {
        "short":       "Store in a paper bag in the refrigerator.",
        "temperature": "Best at 7–10°C (45–50°F).",
        "humidity":    "Paper bag absorbs excess moisture which prevents sliminess.",
        "avoid":       "Do not store in plastic bags — trapped moisture causes rapid decay.",
        "signs":       "Sliminess, dark spots, or a dull color indicate it is no longer fresh.",
        "tip":         "Okra deteriorates very quickly — try to use within 2–3 days of purchase.",
    },
    "oranges": {
        "short":       "Room temperature for a week, refrigerator for longer.",
        "temperature": "Refrigerate at 4–7°C (40–45°F) for up to 3 weeks.",
        "humidity":    "Store loosely — good air circulation prevents mold.",
        "avoid":       "Do not store in sealed plastic bags at room temperature — mold develops quickly.",
        "signs":       "Soft spots, white or green mold, or a fermented smell indicate spoilage.",
        "tip":         "Oranges last much longer than most people think when refrigerated properly.",
    },
    "potato": {
        "short":       "Store in a cool, dark, well-ventilated place.",
        "temperature": "Best at 7–10°C (45–50°F). Do not refrigerate — cold converts starch to sugar.",
        "humidity":    "Moderate humidity. Too dry causes shriveling, too wet causes rot.",
        "avoid":       "Keep away from onions — they release gases that spoil each other. Keep out of light to prevent greening.",
        "signs":       "Green patches, sprouting, soft spots, or a bitter smell. Green areas contain solanine — cut away generously or discard.",
        "tip":         "A dark cupboard or paper bag works perfectly. Never store in the refrigerator.",
    },
    "tomato": {
        "short":       "Keep at room temperature — refrigeration kills the flavour.",
        "temperature": "Best at 18–22°C (65–72°F). Only refrigerate if already very ripe and you need 1–2 extra days.",
        "humidity":    "Normal room humidity. Store stem-side down to slow moisture loss.",
        "avoid":       "Never refrigerate unripe tomatoes — it permanently damages flavour and texture.",
        "signs":       "Mold, very soft flesh, cracked skin with liquid, or a fermented smell.",
        "tip":         "Store stem-side down on the counter. This slows moisture loss through the scar and extends freshness.",
    },
}


# ─────────────────────────────────────────────
# RECIPE DATABASE
# ─────────────────────────────────────────────
RECIPES = {
    "apples": [
        {
            "name":        "Apple Cinnamon Oatmeal",
            "time":        "10 mins",
            "difficulty":  "Easy",
            "ingredients": ["apples", "oats", "cinnamon", "honey", "milk"],
            "steps": [
                "Peel and dice the apple into small cubes.",
                "Cook oats in milk according to packet instructions.",
                "Stir in diced apple, cinnamon, and honey.",
                "Serve warm.",
            ],
            "why": "Great way to use apples that are getting soft.",
        },
        {
            "name":        "Simple Apple Salad",
            "time":        "10 mins",
            "difficulty":  "Easy",
            "ingredients": ["apples", "walnuts", "honey", "lemon juice", "yogurt"],
            "steps": [
                "Slice apples thinly and toss with lemon juice to prevent browning.",
                "Mix yogurt with honey.",
                "Combine apples, walnuts, and dressing.",
                "Serve immediately.",
            ],
            "why": "Uses apples quickly before they lose their crunch.",
        },
    ],
    "banana": [
        {
            "name":        "Banana Smoothie",
            "time":        "5 mins",
            "difficulty":  "Easy",
            "ingredients": ["banana", "milk", "honey", "ice"],
            "steps": [
                "Peel and slice the banana.",
                "Blend banana, milk, honey, and ice until smooth.",
                "Serve immediately.",
            ],
            "why": "Perfect for overripe bananas — the sweeter the better.",
        },
        {
            "name":        "Banana Pancakes",
            "time":        "15 mins",
            "difficulty":  "Easy",
            "ingredients": ["banana", "eggs", "flour", "baking powder", "butter"],
            "steps": [
                "Mash the banana in a bowl.",
                "Mix in eggs, flour, and baking powder until smooth.",
                "Heat butter in a pan and pour in small circles of batter.",
                "Cook until bubbles form, flip, and cook 1 more minute.",
            ],
            "why": "Overripe bananas make the sweetest pancakes.",
        },
        {
            "name":        "Banana Bread",
            "time":        "1 hour",
            "difficulty":  "Medium",
            "ingredients": ["bananas", "flour", "sugar", "eggs", "butter", "baking soda", "salt"],
            "steps": [
                "Preheat oven to 175°C (350°F).",
                "Mash 3 ripe bananas in a large bowl.",
                "Mix in melted butter, sugar, egg, and vanilla.",
                "Stir in flour, baking soda, and salt.",
                "Pour into a greased loaf pan and bake for 55–60 minutes.",
            ],
            "why": "The classic use for very ripe or nearly overripe bananas.",
        },
    ],
    "bittergroud": [
        {
            "name":        "Stir-Fried Bitter Gourd",
            "time":        "20 mins",
            "difficulty":  "Easy",
            "ingredients": ["bitter gourd", "garlic", "chili", "soy sauce", "oil"],
            "steps": [
                "Slice bitter gourd thinly and remove seeds.",
                "Salt the slices and leave for 10 minutes, then rinse to reduce bitterness.",
                "Heat oil in a pan, add garlic and chili.",
                "Add bitter gourd and stir-fry for 5–7 minutes.",
                "Season with soy sauce and serve.",
            ],
            "why": "Quick recipe to use bitter gourd while still firm.",
        },
    ],
    "capsicum": [
        {
            "name":        "Stuffed Capsicum",
            "time":        "40 mins",
            "difficulty":  "Medium",
            "ingredients": ["capsicum", "rice", "onion", "tomato", "cheese", "spices"],
            "steps": [
                "Preheat oven to 180°C (350°F).",
                "Cut tops off capsicums and remove seeds.",
                "Cook rice and mix with sauteed onion, tomato, and spices.",
                "Fill capsicums with the rice mixture and top with cheese.",
                "Bake for 25–30 minutes until tender.",
            ],
            "why": "Great for capsicums that are still firm but need using soon.",
        },
        {
            "name":        "Capsicum Stir Fry",
            "time":        "15 mins",
            "difficulty":  "Easy",
            "ingredients": ["capsicum", "onion", "garlic", "soy sauce", "oil"],
            "steps": [
                "Slice capsicum and onion into strips.",
                "Heat oil in a wok, add garlic.",
                "Add vegetables and stir-fry on high heat for 5 minutes.",
                "Season with soy sauce and serve with rice.",
            ],
            "why": "Fast way to use multiple capsicums at once.",
        },
    ],
    "cucumber": [
        {
            "name":        "Cucumber Raita",
            "time":        "10 mins",
            "difficulty":  "Easy",
            "ingredients": ["cucumber", "yogurt", "cumin", "salt", "mint"],
            "steps": [
                "Grate or finely chop the cucumber.",
                "Squeeze out excess water.",
                "Mix with yogurt, cumin, salt, and mint.",
                "Chill and serve as a side dish.",
            ],
            "why": "Best made with very fresh cucumber for maximum crunch.",
        },
        {
            "name":        "Cucumber Salad",
            "time":        "10 mins",
            "difficulty":  "Easy",
            "ingredients": ["cucumber", "onion", "vinegar", "sugar", "salt", "dill"],
            "steps": [
                "Slice cucumber and onion thinly.",
                "Mix vinegar, sugar, and salt to make dressing.",
                "Toss cucumber and onion in dressing.",
                "Refrigerate for 20 minutes and serve with dill.",
            ],
            "why": "Use cucumbers that are still firm before they go soft.",
        },
    ],
    "okra": [
        {
            "name":        "Bhindi Masala",
            "time":        "25 mins",
            "difficulty":  "Easy",
            "ingredients": ["okra", "onion", "tomato", "cumin", "turmeric", "chili", "oil"],
            "steps": [
                "Wash and dry okra thoroughly, then slice into rounds.",
                "Heat oil and fry okra until slightly crisp, set aside.",
                "In the same pan, cook onion, tomato, and spices.",
                "Add okra back and mix well.",
                "Cook for 5 more minutes and serve with roti or rice.",
            ],
            "why": "Drying the okra before cooking prevents sliminess.",
        },
    ],
    "oranges": [
        {
            "name":        "Fresh Orange Juice",
            "time":        "5 mins",
            "difficulty":  "Easy",
            "ingredients": ["oranges"],
            "steps": [
                "Roll oranges on the counter to loosen the juice.",
                "Cut in half and squeeze using a juicer or by hand.",
                "Strain and serve immediately over ice.",
            ],
            "why": "Best way to use multiple oranges quickly.",
        },
        {
            "name":        "Orange and Carrot Salad",
            "time":        "10 mins",
            "difficulty":  "Easy",
            "ingredients": ["oranges", "carrots", "honey", "lemon juice", "mint"],
            "steps": [
                "Peel and segment oranges.",
                "Grate carrots coarsely.",
                "Mix together with honey and lemon juice.",
                "Garnish with mint and serve chilled.",
            ],
            "why": "A light salad that uses oranges before they dry out.",
        },
    ],
    "potato": [
        {
            "name":        "Aloo Jeera (Cumin Potatoes)",
            "time":        "25 mins",
            "difficulty":  "Easy",
            "ingredients": ["potato", "cumin seeds", "oil", "turmeric", "salt", "coriander"],
            "steps": [
                "Boil potatoes until just cooked, peel and cube.",
                "Heat oil in a pan and add cumin seeds until they splutter.",
                "Add potatoes and turmeric, toss to coat.",
                "Cook on medium heat for 5–7 minutes until slightly crisp.",
                "Garnish with fresh coriander and serve.",
            ],
            "why": "Simple and quick for potatoes that need using up.",
        },
        {
            "name":        "Potato Soup",
            "time":        "30 mins",
            "difficulty":  "Easy",
            "ingredients": ["potatoes", "onion", "garlic", "butter", "stock", "cream", "salt", "pepper"],
            "steps": [
                "Peel and dice potatoes and onion.",
                "Saute onion and garlic in butter until soft.",
                "Add potatoes and stock, bring to a boil.",
                "Simmer for 20 minutes until potatoes are tender.",
                "Blend until smooth, stir in cream, season and serve.",
            ],
            "why": "Good for potatoes that are starting to sprout — just cut away any green parts first.",
        },
    ],
    "tomato": [
        {
            "name":        "Fresh Tomato Chutney",
            "time":        "15 mins",
            "difficulty":  "Easy",
            "ingredients": ["tomatoes", "onion", "garlic", "chili", "oil", "salt", "sugar"],
            "steps": [
                "Chop tomatoes, onion, garlic, and chili.",
                "Heat oil and saute onion and garlic until soft.",
                "Add tomatoes, chili, salt, and a pinch of sugar.",
                "Cook on medium heat for 10 minutes until thick.",
                "Serve with bread, rice, or snacks.",
            ],
            "why": "Perfect for very ripe tomatoes that are too soft to eat raw.",
        },
        {
            "name":        "Tomato Rice",
            "time":        "25 mins",
            "difficulty":  "Easy",
            "ingredients": ["tomatoes", "rice", "onion", "garlic", "spices", "oil"],
            "steps": [
                "Cook rice and set aside.",
                "Saute onion and garlic in oil.",
                "Add chopped tomatoes and spices, cook until mushy.",
                "Mix in cooked rice and stir well.",
                "Serve hot with yogurt.",
            ],
            "why": "Uses up ripe or overripe tomatoes completely.",
        },
    ],
}


# ─────────────────────────────────────────────
# LOOKUP FUNCTIONS
# ─────────────────────────────────────────────
def get_storage_tips(food_key: str) -> dict:
    """Returns detailed storage tips for a food item."""
    return STORAGE_TIPS.get(food_key.lower(), {
        "short": "Store in a cool, dry place.",
        "tip":   "Consume as soon as possible for best quality.",
    })


def get_recipes(food_keys: list) -> dict:
    """
    Given a list of food keys (e.g. ['banana', 'tomato']),
    returns matching recipes grouped by food.
    """
    results = {}
    for key in food_keys:
        key = key.lower()
        if key in RECIPES:
            results[key] = RECIPES[key]
    return results


def get_recipes_for_expiring(scans: list) -> list:
    """
    Takes a list of scan dicts from the database,
    filters for fresh items expiring soon (<=3 days),
    and returns recipe suggestions sorted by urgency.
    """
    expiring = []
    for scan in scans:
        if scan.get("status") == "Fresh" and scan.get("days_to_spoil", 99) <= 3:
            food_key = (scan.get("predicted_class") or "").replace("fresh", "").replace("rotten", "")
            if food_key in RECIPES:
                expiring.append({
                    "food":         scan.get("food"),
                    "food_key":     food_key,
                    "days_to_spoil": scan.get("days_to_spoil"),
                    "recipes":      RECIPES[food_key],
                })

    # Sort by most urgent (fewest days left first)
    expiring.sort(key=lambda x: x["days_to_spoil"])
    return expiring
