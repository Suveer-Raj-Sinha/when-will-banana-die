import tensorflow as tf
import os, json

DATA_DIR = os.path.join("ai-service", "data", "Train")
MODEL_DIR = os.path.join("ai-service", "models")
IMG_SIZE = (224, 224)
BATCH_SIZE = 32

# --- Data ---
train_ds = tf.keras.utils.image_dataset_from_directory(
    DATA_DIR, validation_split=0.2, subset="training",
    seed=42, image_size=IMG_SIZE, batch_size=BATCH_SIZE
)
val_ds = tf.keras.utils.image_dataset_from_directory(
    DATA_DIR, validation_split=0.2, subset="validation",
    seed=42, image_size=IMG_SIZE, batch_size=BATCH_SIZE
)
class_names = train_ds.class_names
AUTOTUNE = tf.data.AUTOTUNE

# Data augmentation — helps a lot with small datasets
augment = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(0.1),
    tf.keras.layers.RandomZoom(0.1),
    tf.keras.layers.RandomBrightness(0.1),
])

train_ds = train_ds.map(lambda x, y: (augment(x, training=True), y))
train_ds = train_ds.cache().shuffle(1000).prefetch(AUTOTUNE)
val_ds   = val_ds.cache().prefetch(AUTOTUNE)

os.makedirs(MODEL_DIR, exist_ok=True)
with open(os.path.join(MODEL_DIR, "class_names.json"), "w") as f:
    json.dump(class_names, f)

# --- Build model ---
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3), include_top=False, weights="imagenet"
)
base_model.trainable = False  # frozen for phase 1

inputs  = tf.keras.Input(shape=(224, 224, 3))
x       = tf.keras.layers.Rescaling(1./255)(inputs)
x       = base_model(x, training=False)
x       = tf.keras.layers.GlobalAveragePooling2D()(x)
x       = tf.keras.layers.Dropout(0.3)(x)       # regularization
x       = tf.keras.layers.Dense(256, activation="relu")(x)
outputs = tf.keras.layers.Dense(len(class_names), activation="softmax")(x)
model   = tf.keras.Model(inputs, outputs)

# --- Phase 1: train head only ---
model.compile(optimizer=tf.keras.optimizers.Adam(1e-3),
              loss="sparse_categorical_crossentropy", metrics=["accuracy"])
model.fit(train_ds, validation_data=val_ds, epochs=10)

# --- Phase 2: unfreeze top layers ---
base_model.trainable = True
for layer in base_model.layers[:100]:   # keep early layers frozen
    layer.trainable = False

model.compile(optimizer=tf.keras.optimizers.Adam(1e-5),  # MUCH lower lr
              loss="sparse_categorical_crossentropy", metrics=["accuracy"])
model.fit(train_ds, validation_data=val_ds, epochs=10)

model.save(os.path.join(MODEL_DIR, "food_freshness_v2.keras"))
print("Saved fine-tuned model.")