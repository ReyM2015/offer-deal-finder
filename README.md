# Offer Finder

A small local web app that searches for public product and service offers, extracts supported price/coupon details, and exports them to Excel.

## Excel columns

The `Offers` worksheet contains these columns:

1. Product name
2. Original cost
3. Discounted cost
4. % of discount
5. Site link for offer
6. Coupon code

The discount percentage is calculated only when both prices are found and the original price is greater than the discounted price. Coupon code is left blank when none is found.

## Run on Windows

1. Install Python 3.10 or newer.
2. Open PowerShell in this folder and run:

   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   Copy-Item .env.example .env
   notepad .env
   ```

3. Add your Tavily API key to `.env`. An OpenAI API key is optional and improves extraction.
4. Start the app:

   ```powershell
   streamlit run app.py
   ```

   The app opens in your browser. Enter a product/service query, optionally add retailer domains, run the search, review the source links, and download the Excel file.

## Run on macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
# Add your Tavily API key to .env; OpenAI is optional.
streamlit run app.py
```

## Keys and provider usage

- Tavily is required for internet search. Create an API key at [tavily.com](https://tavily.com/).
- OpenAI is optional. If supplied, the app uses a model to interpret returned page text, then validates extracted prices and coupon codes against that text.
- Provider usage may be subject to limits or charges. The app does not store keys in the workbook. A key entered in the sidebar is used for the current app session; for personal local use, `.env` is more convenient.

## Coverage and accuracy

“All websites” cannot be guaranteed by a public web search. This app searches pages indexed and returned by the search provider, and some stores may block indexing or require JavaScript, login, location, or membership. It does not bypass access controls or anti-bot protections.

Offer pages change frequently. Review each source link and confirm eligibility, shipping, taxes, availability, and coupon terms before purchase. Unsupported or unclear amounts stay blank. Search results are candidates, not a price guarantee.
