import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# ---- CONFIG ----
st.set_page_config(page_title="Affiliate Blog Writer", layout="centered")
st.title("🧠 Affiliate Blog Generator (FREE Gemini API)")

# ✅ Load your Gemini API key from Streamlit secrets
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
Write a short blog post (500-700 words) promoting this product:

- Product: {title}
- Description: {description}
- Affiliate link: {url}

Requirements:
- Format the blog in HTML using <h2>, <p>, <ul>, etc.
- Use friendly, helpful tone
- Include a strong call-to-action with the affiliate link
- Be SEO-friendly
"""
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text

# ---- UI ----
url = st.text_input("Paste your product or affiliate URL:")

if st.button("Generate Blog"):
    if not url:
        st.warning("Please enter a URL.")
    else:
        title, desc = get_product_info(url)
        if not title:
            st.error("Could not fetch product info.")
        else:
            st.info("🧠 Generating blog content...")
            blog_html = generate_blog_html(title, desc, url)
            st.success("✅ Blog generated below:")
            st.markdown(blog_html, unsafe_allow_html=True)
