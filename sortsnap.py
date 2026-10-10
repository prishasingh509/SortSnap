import json
import streamlit as st
import anthropic

st.set_page_config(page_title="SortSnap", page_icon="♻️")
st.title("♻️ SortSnap")
st.caption("Snap a photo of waste. Get instant segregation and disposal steps.")

lang = st.radio("Language", ["English", "हिन्दी"], horizontal=True)
img = st.file_uploader("Upload a photo of the waste item", type=["jpg", "jpeg", "png", "webp"])

PROMPT = f"""You are a waste segregation expert for Indian households, following India's
Solid Waste Management Rules 2016 (green bin = wet, blue = dry, black = hazardous/sanitary).
Look at the image and reply with ONLY valid JSON, no markdown, with these keys:
item, category (Wet / Dry-Recyclable / E-waste / Hazardous / Sanitary / Not waste),
bin_color, recyclable (true/false), disposal_steps (list of 2-3 short steps),
eco_tip (one line). Write all values in {lang}."""

if img and st.button("Analyze", type="primary"):
    with st.spinner("Looking at it..."):
        client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
        import base64
        data = base64.b64encode(img.getvalue()).decode()
        resp = client.messages.create(
            model="claude-sonnet-5-5",
            max_tokens=600,
            messages=[{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": img.type, "data": data}},
                {"type": "text", "text": PROMPT},
            ]}],
        )
        raw = resp.content[0].text.strip().strip("`").removeprefix("json").strip()
    try:
        r = json.loads(raw)
        st.image(img, width=300)
        st.subheader(f"{r['item']}  →  {r['category']}")
        st.markdown(f"**Bin:** {r['bin_color']}  |  **Recyclable:** {'Yes ♻️' if r['recyclable'] else 'No'}")
        for s in r["disposal_steps"]:
            st.markdown(f"- {s}")
        st.info(r["eco_tip"])
    except Exception:
        st.write(raw)
