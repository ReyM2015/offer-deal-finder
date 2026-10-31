import io
import os
from datetime import datetime, timezone

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from offer_agent import DealFinder, OFFER_COLUMNS

load_dotenv()

st.set_page_config(page_title="Offer Finder", page_icon="🛍️", layout="wide")
st.title("🛍️ Offer Finder")
st.write("Search public web results for product and service offers, review the evidence, and export the results to Excel.")
st.caption("Web search cannot cover every website. Results depend on the search provider, your query, and pages that are publicly accessible.")

with st.sidebar:
    st.header("Search settings")
    tavily_key = st.text_input("Tavily API key", value=os.getenv("TAVILY_API_KEY", ""), type="password", help="Used to search the web. Get a key from tavily.com.")
    openai_key = st.text_input("OpenAI API key (optional)", value=os.getenv("OPENAI_API_KEY", ""), type="password", help="Improves structured price and coupon extraction. Without it, the app uses basic text matching.")
    model = st.text_input("OpenAI model", value=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"), disabled=not bool(openai_key))
    max_results = st.slider("Search results", min_value=5, max_value=20, value=10)

with st.form("offer_search"):
    query = st.text_input("What are you looking for?", placeholder="Example: noise cancelling headphones sale, tax preparation service discount")
    domains_text = st.text_input("Optional sites to prioritize", placeholder="amazon.com, bestbuy.com, example.com", help="Comma-separated domains. Leave blank to search broadly.")
    submitted = st.form_submit_button("Search offers", type="primary")

if submitted:
    if not tavily_key:
        st.error("Enter a Tavily API key in the sidebar to search the web.")
    elif not query.strip():
        st.error("Enter a product or service to search for.")
    else:
        domains = [d.strip().lower().removeprefix("www.") for d in domains_text.split(",") if d.strip()]
        finder = DealFinder(tavily_key=tavily_key, openai_key=openai_key or None, model=model)
        try:
            with st.spinner("Searching public web results and reviewing offer details…"):
                offers = finder.search(query.strip(), max_results=max_results, domains=domains)
            st.session_state["offers"] = offers
            st.session_state["search_query"] = query.strip()
            st.session_state["searched_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        except Exception as exc:
            st.error(f"Search could not be completed: {exc}")

offers = st.session_state.get("offers", [])
if offers:
    st.subheader(f"Found {len(offers)} possible offers")
    st.caption(f"Search: {st.session_state.get('search_query', '')} · {st.session_state.get('searched_at', '')}")
    st.info("Check the offer page before buying. Prices, availability, eligibility, and coupon terms can change. Blank prices mean the page text did not clearly confirm them.")

    view_rows = []
    for offer in offers:
        view_rows.append({
            "Product / service": offer["product_name"],
            "Original cost": offer["original_cost"],
            "Discounted cost": offer["discounted_cost"],
            "Discount %": offer["discount_percent"],
            "Coupon": offer["coupon_code"] or "",
            "Offer page": offer["site_link"],
            "Evidence / notes": offer["evidence"],
        })
    st.dataframe(pd.DataFrame(view_rows), use_container_width=True, hide_index=True, column_config={
        "Offer page": st.column_config.LinkColumn(display_text="Open offer"),
        "Discount %": st.column_config.NumberColumn(format="%.1f%%"),
    })

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export_rows = []
        for offer in offers:
            row = {column: offer.get(key, "") for column, key in zip(OFFER_COLUMNS, ("product_name", "original_cost", "discounted_cost", "discount_percent", "site_link", "coupon_code"))}
            if isinstance(row["% of discount"], (int, float)):
                row["% of discount"] = row["% of discount"] / 100
            export_rows.append(row)
        export_df = pd.DataFrame(export_rows, columns=OFFER_COLUMNS)
        export_df.to_excel(writer, index=False, sheet_name="Offers")
        ws = writer.sheets["Offers"]
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        widths = [36, 18, 20, 16, 62, 24]
        for idx, width in enumerate(widths, start=1):
            ws.column_dimensions[chr(64 + idx)].width = width
        for row in range(2, ws.max_row + 1):
            ws.cell(row, 4).number_format = "0.0%"
            ws.cell(row, 5).hyperlink = ws.cell(row, 5).value
            ws.cell(row, 5).style = "Hyperlink"
    st.download_button("Download Excel file", data=output.getvalue(), file_name=f"offers_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary")
elif "offers" in st.session_state:
    st.warning("No likely offers were found. Try a broader query, or add specific retailer domains.")

with st.expander("How this agent works and its limits"):
    st.markdown("""
- Searches public web pages through Tavily; it does not crawl the entire internet or bypass logins, paywalls, robots rules, or anti-bot protections.
- Uses page text returned by search to identify product/service names, list prices, sale prices, and coupon codes.
- Includes only values supported by the returned text. It calculates the discount percentage when both original and discounted prices are available.
- Search and AI provider accounts may have usage limits or charges. The app does not store API keys or search history outside the current browser session.
""")
