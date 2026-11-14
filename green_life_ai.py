import numpy as np
import requests
from geopy.geocoders import Nominatim
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

GLOBAL_TREE_DATABASE = [
    {
        "name": "Wild Olive (Olea europaea)",
        "features": [21.0, 250.0, 1],
        "benefit": "Produces nutritious olives & oil; prevents coastal soil erosion.",
        "why_safe": "Waxy leaves block sea salt spray; shallow roots protect groundwater."
    },
    {
        "name": "Acacia (Acacia tortilis)",
        "features": [30.0, 120.0, 0],
        "benefit": "Fixes nitrogen in poor desert soil; provides shade & fodder.",
        "why_safe": "Deep taproot survives extreme drought without draining surface moisture."
    },
    {
        "name": "Carob Tree (Ceratonia siliqua)",
        "features": [22.0, 300.0, 1],
        "benefit": "Produces nutrient-rich pods with minimal irrigation.",
        "why_safe": "Thrives in rocky coastal soil without needing chemical fertilizers."
    },
    {
        "name": "Date Palm (Phoenix dactylifera)",
        "features": [29.0, 80.0, 1],
        "benefit": "High-value date fruit harvest; creates micro-shade for smaller crops.",
        "why_safe": "Tolerates high heat and brackish water in arid oases and valleys."
    },
    {
        "name": "Moringa (Moringa oleifera)",
        "features": [28.0, 500.0, 0],
        "benefit": "Fast-growing superfood leaves; seeds naturally purify water.",
        "why_safe": "Low water demand and enriches degraded tropical/subtropical soils."
    },
    {
        "name": "Red Mangrove (Rhizophora mangle)",
        "features": [27.0, 1200.0, 1],
        "benefit": "Protects coastlines from storm surges and stores high carbon.",
        "why_safe": "Filters saltwater naturally and creates habitats for marine life."
    },
    {
        "name": "Silver Birch (Betula pendula)",
        "features": [11.0, 700.0, 0],
        "benefit": "Supports local pollinators and improves forest soil quality.",
        "why_safe": "Native to cooler climates; adapted to natural rainfall without irrigation."
    },
    {
        "name": "Scots Pine (Pinus sylvestris)",
        "features": [8.0, 650.0, 0],
        "benefit": "Prevents hillside erosion and provides year-round wildlife shelter.",
        "why_safe": "Hardy native evergreen adapted to cold winters and acidic soils."
    },
    {
        "name": "Tamarisk (Tamarix nilotica)",
        "features": [24.0, 150.0, 1],
        "benefit": "Acts as a natural coastal windbreak and stabilizes sand dunes.",
        "why_safe": "Native to Egyptian coasts and Nile banks; excretes excess salt safely."
    },
     {
        "name": "Mediterranean Cypress (Cupressus sempervirens)",
        "features": [20.0, 350.0, 1],
        "benefit": "Blocks strong coastal winds and provides long-term timber.",
        "why_safe": "High drought tolerance and prevents hillside soil erosion."
    },
     {
        "name": "Sycamore Fig (Ficus sycomorus)",
        "features": [26.0, 180.0, 0],
        "benefit": "Produces sweet figs and wide cooling shade in hot urban/rural areas.",
        "why_safe": "Historic native Egyptian tree that supports local birds and pollinators."
    },
        {
        "name": "Christ's Thorn Jujube / Sidr (Ziziphus spina-christi)",
        "features": [28.0, 140.0, 1],
        "benefit": "Produces edible Nabk fruit and supports desert honeybees.",
        "why_safe": "Survives severe heatwaves and poor, slightly salty soils."
    },
     {
        "name": "Grey Mangrove / Avicennia (Avicennia marina)",
        "features": [28.0, 300.0, 1],
        "benefit": "Thrives on Red Sea coasts; stabilizes tidal mudflats and sequesters CO2.",
        "why_safe": "Native to Egypt's Red Sea shore; grows directly in seawater without fresh water."
    },
      {
        "name": "Baobab (Adansonia digitata)",
        "features": [29.0, 600.0, 0],
        "benefit": "Produces vitamin-rich fruit pods and stores rainwater in its trunk.",
        "why_safe": "Deeply adapted to seasonal dry spells without depleting local wells."
    },
    {
        "name": "English Oak (Quercus robur)",
        "features": [13.0, 800.0, 0],
        "benefit": "Long-lived carbon sink supporting hundreds of native insect and bird species.",
        "why_safe": "Deeply rooted temperate native that strengthens forest biodiversity."
    } 
]

def recommend_trees_for_location(city_name, api_key=None):
    # Step A: Convert any city worldwide to GPS coordinates 
    geolocator = Nominatim(user_agent="green_life_isef_ml_engine")
    location = geolocator.geocode(city_name)
    if not location:
        return {"error": "Location not found. Try adding the country name (e.g., 'Cairo, Egypt' or 'London, UK')."}

    lat, lon = round(location.latitude, 4), round(location.longitude, 4)

    # Step B: Fetch real-time temperature & rain from Open-Meteo 
    avg_temp = 24.0
    est_annual_rain = 250.0
    try:
        weather_url = f"https://open-meteo.com{lat}&longitude={lon}&current_weather=true&daily=precipitation_sum&timezone=auto"
        w_data = requests.get(weather_url, timeout=5).json()
        avg_temp = w_data.get("current_weather", {}).get("temperature", 24.0)
        weekly_rain = sum(w_data.get("daily", {}).get("precipitation_sum", [2.0]))
        est_annual_rain = max(60.0, weekly_rain * 52)
    except Exception:
        # Estimate climate from latitude if offline
        avg_temp = 30.0 - (abs(lat) * 0.45)
        est_annual_rain = 150.0 if 15 <= abs(lat) <= 32 else 600.0

    addr_lower = location.address.lower()
    is_coastal = 1 if any(w in addr_lower for w in ["coast", "alexandria", "sea", "port", "beach", "island", "bay", "ocean"]) else 0

    # Step C: Run Machine Learning K-Nearest Neighbors (KNN) to find top 3 eco-safe trees
    X_train = np.array([t["features"] for t in GLOBAL_TREE_DATABASE])
    # Normalize features so temperature, rain, and salinity carry balanced weight
    scale = np.array([35.0, 1200.0, 1.0])
    X_norm = X_train / scale

    user_climate = np.array([[avg_temp, est_annual_rain, is_coastal]]) / scale

    knn = NearestNeighbors(n_neighbors=3, metric="euclidean")
    knn.fit(X_norm)
    distances, indices = knn.kneighbors(user_climate)

    recommended = []
    for idx in indices[0]:
        tree = GLOBAL_TREE_DATABASE[idx]
        # Eco-Safety Guardrail: Block non-salt-tolerant trees right on the sea coast
        if is_coastal == 1 and tree["features"][2] == 0:
            continue
        recommended.append(tree)

    if not recommended:
        recommended = [GLOBAL_TREE_DATABASE[0], GLOBAL_TREE_DATABASE[2]]

    return {
        "detected_address": location.address,
        "coordinates": (lat, lon),
        "coastal_zone": bool(is_coastal),
        "recommended_trees": recommended
    }


# 2. SELF-CONTAINED MULTI-TURN NLP PLANT DOCTOR 

PLANT_CASES = [
    {
        "keywords": "yellow leaves wet mushy soil drooping soft overwatered",
        "diagnosis": "Root Rot from Overwatering",
        "treatment": "Stop watering for 5 days, gently loosen the top 4 cm of soil to let oxygen reach the roots, and make sure excess water can drain away."
    },
    {
        "keywords": "brown crispy leaf tips dry soil cracked underwatered salt burn",
        "diagnosis": "Dehydration or Sea-Salt Accumulation",
        "treatment": "Water deeply once at sunrise to flush salt below the root zone, then cover the soil with 3 cm of dry leaves or organic mulch to lock in moisture."
    },
    {
        "keywords": "stopped growing stunted small pale leaves weak slow",
        "diagnosis": "Nitrogen Deficiency or Compacted Soil",
        "treatment": "Aerate the soil around the base with a small hand tool and mix in natural organic compost (avoid chemical fertilizers that harm coastal groundwater)."
    },
    {
        "keywords": "spots holes bugs insects eaten leaves white powder fungus",
        "diagnosis": "Fungal Mildew or Leaf Pests",
        "treatment": "Prune affected leaves, avoid wetting the foliage when watering, and spray a natural mixture of water with a few drops of organic neem oil or mild soap."
    }
]

def diagnose_plant_chat(tree_name, location_name, chat_history, api_key=None):
    user_messages = [m["text"] for m in chat_history if m["role"] == "user"]
    full_text = " ".join(user_messages).lower()

    # Step 1: On the first message, ask clarifying follow-up questions to prevent misdiagnosis
    if len(user_messages) == 1:
        has_soil_info = any(w in full_text for w in ["wet", "dry", "mushy", "moist", "damp", "hard"])
        has_leaf_info = any(w in full_text for w in ["yellow", "brown", "crispy", "spots", "holes", "pale"])
        
        if not (has_soil_info and has_leaf_info):
            return (
                f"To give an accurate, eco-safe diagnosis for your {tree_name} in {location_name}, please check two quick things:\n"
                "1. Touch the soil 3 cm deep: is it **wet/mushy** or **dry/cracked**?\n"
                "2. Look closely at the leaves: are they **turning yellow**, **crispy brown at the tips**, or **showing spots/holes**?"
            )

    # Step 2: Match combined symptoms + follow-up answers using TF-IDF Cosine Similarity
    corpus = [case["keywords"] for case in PLANT_CASES]
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(corpus + [full_text])
    scores = cosine_similarity(vectors[-1], vectors[:-1]).flatten()
    best_idx = int(scores.argmax())

    if scores[best_idx] < 0.08:
        return (
            f"Based on your notes for {tree_name}: Check soil moisture 3 cm deep before watering, "
            "add a layer of organic compost mulch around the base, and keep leaves dry during evening hours."
        )

    matched = PLANT_CASES[best_idx]
    confidence = min(98, int(65 + (scores[best_idx] * 60)))
    return (
        f"✅ Diagnosis ({confidence}% Match): {matched['diagnosis']}\n"
        f"🌿 Eco-Safe Treatment: {matched['treatment']}"
    )



