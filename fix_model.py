import tensorflow as tf

old_path = "ai-service/models/food_freshness_v2.keras"
new_path = "ai-service/models/food_freshness_v2_fixed.keras"

raw = tf.keras.models.load_model(old_path)

fixed = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(224, 224, 3)),
    *raw.layers
])

fixed.save(new_path)
print("Fixed model saved to:", new_path)
