import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# ---- Config ----
st.set_page_config(page_title="Blog Writer", layout="centered")
st.title("🧠 Affiliate Blog Generator (Minimal Version)")

# ---- Gemini API Key ----
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# ---- Scrape Product Info ----
def get_product_info(url):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else "Product"
        meta = soup.find("meta", attrs={"name": "description"})
        desc = meta["content"].strip() if meta else "No description available"
        return title, desc
    except Exception as e:
        st.error(f"❌ Error scraping URL: {e}")
        return None, None

# ---- Generate Blog using Gemini ----
def generate_blog_html(title, description, url):
    prompt = f"""
You are a professional blog writer.

Write a 500-700 word HTML blog post about this product:
- Title: {title}
- Description: {description}
- Affiliate link: {url}

Requirements:
- Use <h2>, <p>, <ul>, <li>, <strong> etc.
- Explain benefits of the product
- Include a call-to-action with the affiliate link
- Make it SEO-optimized and engaging
- Write in friendly, trustworthy tone
"""

    model = genai.GenerativeModel(model_name="models/gemini-pro")
    response = model.generate_content(prompt)
    return response.text

# ---- UI ----
url = st.text_input("Paste your product or affiliate URL:")

if st.button("Generate Blog"):
    if not url:
        st.warning("Please enter a product URL.")
    else:
        title, desc = get_product_info(url)
        if not title:
            st.error("Could not fetch product info.")
        else:
            st.info("🧠 Generating blog content...")
            blog_html = generate_blog_html(title, desc, url)
            st.success("✅ Blog generated below:")
            st.markdown(blog_html, unsafe_allow_html=True)
