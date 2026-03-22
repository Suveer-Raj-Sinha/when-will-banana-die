import streamlit as st
import os
from predict import analyze_image
from gradcam import generate_gradcam

st.set_page_config(page_title="When Will Banana Die?", layout="centered")

st.title("When Will fruit Die?")
st.write("Upload an image of a fruit or vegetable to analyze its freshness.")

uploaded = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded:
    temp_path = "temp_input.png"
    with open(temp_path, "wb") as f:
        f.write(uploaded.read())

    st.image(temp_path, caption="Uploaded Image", use_column_width=True)

    with st.spinner("Analyzing..."):
        result = analyze_image(temp_path)
        gradcam_path = generate_gradcam(
            temp_path,
            result["class_index"],
            output_path="gradcam_result.png"
        )

    st.subheader("Prediction Result")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Food", result["food"])
        st.metric("Status", result["status"])
        st.metric("Confidence", f'{result["confidence_percent"]}%')

    with col2:
        st.metric("Freshness Score", result["freshness_score"])
        st.metric("Days Left", result["days_to_spoil"])

    st.info(result["advice"])

    if result["note"]:
        st.warning(result["note"])

    if os.path.exists(gradcam_path):
        st.subheader("Model Attention (Grad-CAM)")
        st.image(gradcam_path, caption="Grad-CAM Output", use_column_width=True)
