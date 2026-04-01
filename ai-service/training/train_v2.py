"""
train_v2.py  —  Food Freshness Model (Fine-tuned)
==================================================
Run from the project root:
    python ai-service/training/train_v2.py

What's new vs v1:
  - Data augmentation  (flip, rotate, zoom, brightness)
  - Two-phase fine-tuning  (frozen head → unfreeze top MobileNetV2 layers)
  - Dropout regularisation
  - Confidence-weighted days-left estimate  (no more random.randint)
  - Confusion matrix + classification report saved to ai-service/models/

Requirements (add to requirements.txt):
    tensorflow
    matplotlib
    numpy
    Pillow
    scikit-learn
    opencv-python
    streamlit
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
DATA_DIR  = os.path.join("ai-service", "data", "Train")
MODEL_DIR = os.path.join("ai-service", "models")
IMG_SIZE  = (224, 224)
BATCH_SIZE = 32
PHASE1_EPOCHS = 10
PHASE2_EPOCHS = 10
FREEZE_UNTIL  = 100   # MobileNetV2 has 154 layers; keep layers 0–99 frozen in phase 2

os.makedirs(MODEL_DIR, exist_ok=True)


# ─────────────────────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────────────────────
print("\n[1/6] Loading dataset...")

train_ds = tf.keras.utils.image_dataset_from_directory(
    DATA_DIR,
    validation_split=0.2,
    subset="training",
    seed=42,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
)
val_ds = tf.keras.utils.image_dataset_from_directory(
    DATA_DIR,
    validation_split=0.2,
    subset="validation",
    seed=42,
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
)

class_names = train_ds.class_names
print(f"    Classes ({len(class_names)}): {class_names}")

with open(os.path.join(MODEL_DIR, "class_names.json"), "w") as f:
    json.dump(class_names, f)
print(f"    Saved class_names.json")


# ─────────────────────────────────────────────
# 2. AUGMENTATION + PIPELINE
# ─────────────────────────────────────────────
print("\n[2/6] Building data pipeline with augmentation...")

augment = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(0.10),
    tf.keras.layers.RandomZoom(0.10),
    tf.keras.layers.RandomBrightness(0.10),
], name="augmentation")

AUTOTUNE = tf.data.AUTOTUNE
train_ds = (
    train_ds
    .map(lambda x, y: (augment(x, training=True), y), num_parallel_calls=AUTOTUNE)
    .cache()
    .shuffle(1000)
    .prefetch(AUTOTUNE)
)
val_ds = val_ds.cache().prefetch(AUTOTUNE)


# ─────────────────────────────────────────────
# 3. BUILD MODEL
# ─────────────────────────────────────────────
print("\n[3/6] Building model...")

base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights="imagenet",
)
base_model.trainable = False  # frozen for phase 1

inputs  = tf.keras.Input(shape=(224, 224, 3), name="image_input")
x       = tf.keras.layers.Rescaling(1.0 / 255, name="rescale")(inputs)
x       = base_model(x, training=False)
x       = tf.keras.layers.GlobalAveragePooling2D(name="gap")(x)
x       = tf.keras.layers.Dropout(0.3, name="dropout")(x)
x       = tf.keras.layers.Dense(256, activation="relu", name="dense_256")(x)
outputs = tf.keras.layers.Dense(len(class_names), activation="softmax", name="predictions")(x)
model   = tf.keras.Model(inputs, outputs, name="food_freshness_v2")

model.summary()


# ─────────────────────────────────────────────
# 4. PHASE 1 — Train head only
# ─────────────────────────────────────────────
print(f"\n[4/6] Phase 1: training head only ({PHASE1_EPOCHS} epochs, lr=1e-3)...")

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)

callbacks_p1 = [
    tf.keras.callbacks.EarlyStopping(
        monitor="val_accuracy", patience=3, restore_best_weights=True
    ),
]

history1 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=PHASE1_EPOCHS,
    callbacks=callbacks_p1,
)

print(f"    Phase 1 best val_accuracy: {max(history1.history['val_accuracy']):.4f}")


# ─────────────────────────────────────────────
# 5. PHASE 2 — Fine-tune top layers
# ─────────────────────────────────────────────
print(f"\n[5/6] Phase 2: fine-tuning top MobileNetV2 layers ({PHASE2_EPOCHS} epochs, lr=1e-5)...")

base_model.trainable = True
for layer in base_model.layers[:FREEZE_UNTIL]:
    layer.trainable = False

trainable_count = sum(1 for l in base_model.layers if l.trainable)
print(f"    Trainable base layers: {trainable_count} / {len(base_model.layers)}")

# Much lower learning rate — critical to avoid destroying ImageNet weights
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)

callbacks_p2 = [
    tf.keras.callbacks.EarlyStopping(
        monitor="val_accuracy", patience=4, restore_best_weights=True
    ),
    tf.keras.callbacks.ReduceLROnPlateau(
        monitor="val_loss", factor=0.5, patience=2, min_lr=1e-7
    ),
]

history2 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=PHASE2_EPOCHS,
    callbacks=callbacks_p2,
)

print(f"    Phase 2 best val_accuracy: {max(history2.history['val_accuracy']):.4f}")


# ─────────────────────────────────────────────
# 6. EVALUATE + SAVE
# ─────────────────────────────────────────────
print("\n[6/6] Evaluating and saving...")

# ── Confusion matrix & classification report ──
y_true, y_pred = [], []
for images, labels in val_ds:
    preds = model.predict(images, verbose=0)
    y_true.extend(labels.numpy())
    y_pred.extend(np.argmax(preds, axis=1))

report = classification_report(y_true, y_pred, target_names=class_names)
print("\nClassification Report:\n")
print(report)

report_path = os.path.join(MODEL_DIR, "eval_report.txt")
with open(report_path, "w") as f:
    f.write(report)
print(f"    Saved: {report_path}")

# ── Confusion matrix plot ──
cm = confusion_matrix(y_true, y_pred)
fig, ax = plt.subplots(figsize=(13, 11))
im = ax.imshow(cm, cmap="Blues")
plt.colorbar(im, ax=ax)
ax.set_xticks(range(len(class_names)))
ax.set_yticks(range(len(class_names)))
ax.set_xticklabels(class_names, rotation=45, ha="right", fontsize=9)
ax.set_yticklabels(class_names, fontsize=9)
ax.set_xlabel("Predicted label", fontsize=11)
ax.set_ylabel("True label", fontsize=11)
ax.set_title("Confusion matrix — food freshness v2", fontsize=13, pad=15)
for i in range(len(class_names)):
    for j in range(len(class_names)):
        ax.text(j, i, str(cm[i, j]),
                ha="center", va="center",
                color="white" if cm[i, j] > cm.max() / 2 else "black",
                fontsize=7)
plt.tight_layout()
cm_path = os.path.join(MODEL_DIR, "confusion_matrix.png")
plt.savefig(cm_path, dpi=150)
plt.close()
print(f"    Saved: {cm_path}")

# ── Training history plot ──
all_acc     = history1.history["accuracy"]     + history2.history["accuracy"]
all_val_acc = history1.history["val_accuracy"] + history2.history["val_accuracy"]
all_loss    = history1.history["loss"]         + history2.history["loss"]
all_val_loss= history1.history["val_loss"]     + history2.history["val_loss"]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
phase_split = len(history1.history["accuracy"])

for ax in (ax1, ax2):
    ax.axvline(x=phase_split - 0.5, color="gray", linestyle="--", linewidth=1, alpha=0.6)
    ax.text(phase_split - 0.3, ax.get_ylim()[0] if ax.get_ylim()[0] != 0 else 0.01,
            "fine-tune →", fontsize=8, color="gray", va="bottom")

ax1.plot(all_acc,     label="train accuracy")
ax1.plot(all_val_acc, label="val accuracy")
ax1.set_title("Accuracy")
ax1.set_xlabel("Epoch")
ax1.legend()
ax1.grid(alpha=0.3)

ax2.plot(all_loss,     label="train loss")
ax2.plot(all_val_loss, label="val loss")
ax2.set_title("Loss")
ax2.set_xlabel("Epoch")
ax2.legend()
ax2.grid(alpha=0.3)

plt.suptitle("Training history — food freshness v2", fontsize=13)
plt.tight_layout()
hist_path = os.path.join(MODEL_DIR, "training_history.png")
plt.savefig(hist_path, dpi=150)
plt.close()
print(f"    Saved: {hist_path}")

# ── Save model ──
model_path = os.path.join(MODEL_DIR, "food_freshness_v2.keras")
model.save(model_path)
print(f"    Saved: {model_path}")

print("\nDone! Update MODEL_PATH in predict.py to use food_freshness_v2.keras")
