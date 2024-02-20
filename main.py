from fastapi import FastAPI, HTTPException
from fastapi.middleware.wsgi import WSGIMiddleware
from flask import Flask, request, render_template
from markupsafe import escape
import settrade_v2
from datetime import datetime
from settrade_v2.errors import SettradeError


def get_quote(symbol: str) -> float:
    mkt_data = investor.MarketData()
    quote = mkt_data.get_quote_symbol(symbol)
    price = float(list(quote.values())[2])
    return price


flask_app = Flask(__name__)


@flask_app.route("/")
def flask_main():
    return render_template("index.html")


@flask_app.route("/dashboard/<symbol>")
def hello(symbol: str = ""):
    return render_template("graph.html", symbol=symbol)


app = FastAPI()

investor = settrade_v2.Investor(
    app_id="020NpmB0KMjKbxEp",
    app_secret="ANmF2t227O0lZTKScLcXEIWfbhIxOl0Mr+UkVCRJ315b",
    broker_id="SANDBOX",
    app_code="SANDBOX",
    is_auto_queue=False,
)

deri = investor.Derivatives(account_no="64160038-D")


@app.get("/api/current_quote/{symbol}")
def read_main(symbol: str) -> dict:
    # try to get current price of symbol
    try:
        price = get_quote(symbol)
    except Exception as e:
        raise HTTPException(status_code=404, detail=e)
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    return {"symbol": symbol, "price": price, "datetime": dt_string}

@app.get("/api/buy/{symbol}/{qty}")
def buy(symbol: str, qty: int):
    try:
        order = deri.place_order(
                    pin="000000",
                    symbol=symbol,
                    side="Long",
                    position="Open",
                    price_type="Limit",
                    price=get_quote(symbol),
                    volume=qty,
                )
    except SettradeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return order

@app.get("/api/sell/{symbol}/{qty}")
def sell(symbol: str, qty: int):
    try:
        order = deri.place_order(
                    pin="000000",
                    symbol=symbol,
                    side="Short",
                    position="Open",
                    price_type="Limit",
                    price=get_quote(symbol),
                    volume=qty,
            )
    except SettradeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return order



app.mount("/public", WSGIMiddleware(flask_app))
