import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from googleapiclient.discovery import build
from google.oauth2 import service_account

# ---- PAGE SETUP ----
st.set_page_config(page_title="Affiliate Blog Generator", layout="centered")
st.title("🧠 Affiliate Blog Writer with Gemini AI")
st.markdown("Paste an affiliate product URL, and we’ll generate an SEO-optimized blog saved to your Google Docs.")

# ---- CONFIGURE GEMINI API ----
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GEMINI_API_KEY)

# ---- GOOGLE DOCS SETUP ----
def init_docs_service():
    creds_dict = st.secrets["gcp_service_account"]
    creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=[
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/drive',
    ])
    docs_service = build('docs', 'v1', credentials=creds)
    return docs_service

# ---- SCRAPE PRODUCT PAGE ----
def crawl_page(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string if soup.title else "No title"
        desc_tag = soup.find("meta", attrs={"name": "description"})
        description = desc_tag["content"] if desc_tag else "No description available"
        paras = soup.find_all("p")
        content = ' '.join([p.get_text(strip=True) for p in paras[:10]])
        return {"title": title.strip(), "description": description.strip(), "info": content.strip()}
    except:
        return None

# ---- GENERATE BLOG ----
def generate_blog(product, url):
    prompt = f"""
Write a detailed, SEO-optimized blog post promoting this product:

Title: {product['title']}
Description: {product['description']}
Affiliate Link: {url}
Additional Page Content: {product['info']}

Structure:
- Catchy title
- Introduction on problem solved
- H2 and H3 headers
- Bullet points or numbered list
- Highlight benefits and features
- Call to action with the link
- Optimized for Google search

Write in a friendly, persuasive, informative tone.
"""
    model = genai.GenerativeModel("models/gemini-pro")
    response = model.generate_content(prompt)
    return response.text

# ---- SAVE TO GOOGLE DOCS ----
def save_to_docs(title, content):
    docs_service = init_docs_service()
    doc = docs_service.documents().create(body={"title": title}).execute()
    doc_id = doc.get("documentId")
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": [{"insertText": {"location": {"index": 1}, "text": content}}]}
    ).execute()
    return f"https://docs.google.com/document/d/{doc_id}/edit"

# ---- STREAMLIT UI ----
product_url = st.text_input("Paste affiliate product URL here")

if st.button("Generate Blog Post"):
    if not product_url:
        st.error("Please enter a product URL.")
    else:
        st.info("🔍 Scraping product page...")
        product = crawl_page(product_url)
        if not product:
            st.error("Could not scrape product details. Check the URL.")
        else:
            st.success("✅ Product data extracted.")
            st.info("🧠 Generating blog with Gemini...")
            blog = generate_blog(product, product_url)
            st.success("✅ Blog generated.")
            st.info("💾 Saving to Google Docs...")
            link = save_to_docs(product['title'], blog)
            st.success("✅ Done! [View on Google Docs](%s)" % link)
