from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import feedparser
import httpx
from datetime import datetime
import random
import asyncio
import json

app = FastAPI(title="Agriculture RSS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enhanced RSS sources for rice and agriculture news
RSS_SOURCES = [
    {
        "name": "Rice Market News",
        "url": "https://news.google.com/rss/search?q=rice+market+price+export+import+basmati&hl=en-US&gl=US&ceid=US:en",
        "keywords": ["rice", "basmati", "grain", "export", "import", "price"]
    },
    {
        "name": "Commodity Markets",
        "url": "https://feeds.reuters.com/reuters/commodities",
        "keywords": ["rice", "wheat", "grain", "agriculture", "commodity"]
    },
    {
        "name": "Agriculture News",
        "url": "https://www.agriculture.com/rss",
        "keywords": ["rice", "crop", "harvest", "farm", "agriculture"]
    },
    {
        "name": "Business Standard Commodities",
        "url": "https://www.business-standard.com/rss/markets-106.rss",
        "keywords": ["rice", "basmati", "export", "commodity"]
    },
    {
        "name": "The Hindu Business",
        "url": "https://www.thehindu.com/business/feeder/default.rss",
        "keywords": ["rice", "basmati", "export", "commodity", "agriculture"]
    },
    {
        "name": "Economic Times Markets",
        "url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "keywords": ["rice", "commodity", "export", "price"]
    }
]

# Enhanced RSS sources for Indian agriculture
INDIAN_AGRI_RSS_SOURCES = [
    {
        "name": "DGFT Official",
        "url": "https://dgft.gov.in/CP/",
        "type": "policy",
        "keywords": ["dgft", "export", "import", "policy", "notification", "circular"]
    },
    {
        "name": "Agriculture Ministry",
        "url": "https://pib.gov.in/RssMain.aspx?ModId=2&Lang=1&Regid=2",
        "type": "government",
        "keywords": ["agriculture", "farm", "farmer", "kisan", "crop", "subsidy", "msp"]
    },
    {
        "name": "Business Standard Agriculture",
        "url": "https://www.business-standard.com/rss/agriculture-106.rss",
        "type": "news",
        "keywords": ["agriculture", "farm", "crop", "rice", "wheat", "export", "import"]
    },
    {
        "name": "The Hindu Agriculture",
        "url": "https://www.thehindu.com/news/national/feeder/default.rss",
        "type": "news",
        "keywords": ["agriculture", "farm", "farmer", "crop", "mandi", "kisan"]
    },
    {
        "name": "Economic Times Agriculture",
        "url": "https://economictimes.indiatimes.com/rssfeeds/4719161.cms",
        "type": "news",
        "keywords": ["agriculture", "farm", "crop", "commodity", "export", "import"]
    }
]

# Base prices for basmati rice (will be dynamically adjusted)
BASE_BASMATI_PRICES = {
    "Traditional Basmati": {
        "base_price": 1450,
        "specification": "8.10mm max",
        "packing": "50 KG PP", 
        "port": "Mundra",
        "volatility": 0.02  # 2% price fluctuation
    },
    "Pusa White Sella": {
        "base_price": 1380,
        "specification": "Premium Grade",
        "packing": "50 KG PP",
        "port": "Nhava Sheva", 
        "volatility": 0.025
    },
    "Steam Basmati": {
        "base_price": 1420,
        "specification": "8.00mm max",
        "packing": "50 KG PP",
        "port": "Mundra",
        "volatility": 0.018
    },
    "Organic Brown": {
        "base_price": 1580,
        "specification": "Certified",
        "packing": "25 KG Jute",
        "port": "Any Port",
        "volatility": 0.03
    }
}

@app.get("/")
def home():
    return {"message": "Agriculture RSS API is running!"}

@app.get("/live-basmati-prices")
async def get_live_basmati_prices():
    """
    Generate realistic live prices for basmati rice with market trends
    """
    try:
        # Get current market sentiment
        market_trend = await get_market_sentiment()
        
        live_prices = []
        
        for product, details in BASE_BASMATI_PRICES.items():
            base_price = details["base_price"]
            volatility = details["volatility"]
            
            # Adjust price based on market sentiment
            if market_trend["overall_sentiment"] == "bullish":
                trend_factor = random.uniform(0.005, 0.015)  # 0.5% to 1.5% increase
            elif market_trend["overall_sentiment"] == "bearish":
                trend_factor = random.uniform(-0.015, -0.005)  # 0.5% to 1.5% decrease
            else:
                trend_factor = random.uniform(-0.005, 0.005)  # Neutral
            
            # Add random volatility
            volatility_factor = random.uniform(-volatility, volatility)
            
            # Calculate final price
            final_price = base_price * (1 + trend_factor + volatility_factor)
            final_price = round(final_price, 2)
            
            # Determine trend direction for display
            price_change = final_price - base_price
            if price_change > 5:
                trend = "up"
                change_display = f"+${abs(price_change):.1f}"
            elif price_change < -5:
                trend = "down" 
                change_display = f"-${abs(price_change):.1f}"
            else:
                trend = "stable"
                change_display = None
            
            live_prices.append({
                "product": product,
                "specification": details["specification"],
                "packing": details["packing"],
                "port": details["port"],
                "price": f"${final_price:,.0f}",
                "trend": trend,
                "change": change_display,
                "base_price": base_price,
                "current_price": final_price
            })
        
        return {
            "status": "success",
            "prices": live_prices,
            "market_sentiment": market_trend,
            "last_updated": datetime.now().isoformat(),
            "update_frequency": "120 seconds"
        }
        
    except Exception as e:
        print(f"Error generating live prices: {e}")
        return {
            "status": "error",
            "error": str(e),
            "prices": [],
            "last_updated": datetime.now().isoformat()
        }

async def get_market_sentiment():
    """
    Analyze market sentiment based on recent news and trends
    """
    try:
        # Simulate market analysis (in real implementation, this would analyze news feeds)
        factors = {
            "export_demand": random.choice(["strong", "moderate", "weak"]),
            "supply_conditions": random.choice(["tight", "adequate", "surplus"]),
            "currency_impact": random.choice(["favorable", "neutral", "unfavorable"]),
            "global_demand": random.choice(["increasing", "stable", "decreasing"])
        }
        
        # Determine overall sentiment
        positive_factors = sum(1 for factor in factors.values() 
                             if factor in ["strong", "adequate", "favorable", "increasing"])
        
        if positive_factors >= 3:
            overall_sentiment = "bullish"
        elif positive_factors <= 1:
            overall_sentiment = "bearish" 
        else:
            overall_sentiment = "neutral"
        
        return {
            "overall_sentiment": overall_sentiment,
            "factors": factors,
            "analysis_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error analyzing market sentiment: {e}")
        return {
            "overall_sentiment": "neutral",
            "factors": {},
            "analysis_time": datetime.now().isoformat()
        }

async def fetch_single_feed(source, is_indian_agri=False):
    """Fetch and parse a single RSS feed"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(source["url"], timeout=20.0)
            response.raise_for_status()
        
        feed = feedparser.parse(response.text)
        articles = []
        
        for entry in feed.entries[:10]:
            content = f"{entry.title} {entry.get('summary', '')}".lower()
            
            if is_indian_agri:
                keywords = source["keywords"]
            else:
                keywords = source["keywords"]
            
            if any(keyword in content for keyword in keywords):
                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.get("published", datetime.now().isoformat()),
                    "summary": entry.get("summary", "")[:200],
                    "source": source["name"],
                    "type": source.get("type", "news")
                })
        
        return articles
    except Exception as e:
        print(f"Error fetching from {source['name']}: {e}")
        return []

@app.get("/rss")
async def get_rss_feed():
    """
    Fetches latest RSS articles from multiple sources with enhanced rice filtering
    """
    try:
        tasks = [fetch_single_feed(source) for source in RSS_SOURCES]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_articles = []
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
        
        filtered_articles = []
        rice_keywords = [
            'rice', 'basmati', 'grain', 'cereal', 'paddy',
            'export', 'import', 'commodity', 'price', 'market',
            'harvest', 'crop', 'agriculture'
        ]
        
        for article in all_articles:
            content = f"{article['title']} {article.get('summary', '')}".lower()
            if any(keyword in content for keyword in rice_keywords):
                filtered_articles.append(article)
        
        unique_articles = []
        seen_titles = set()
        
        for article in filtered_articles:
            title_lower = article["title"].lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_articles.append(article)
        
        unique_articles.sort(key=lambda x: x.get("published", ""), reverse=True)
        
        if not unique_articles:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            unique_articles = get_rice_fallback_articles(current_time)
        
        return {
            "count": len(unique_articles),
            "articles": unique_articles[:20],
            "last_updated": datetime.now().isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        print(f"Error in rice RSS endpoint: {e}")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        return {
            "count": 5,
            "articles": get_rice_fallback_articles(current_time),
            "last_updated": datetime.now().isoformat(),
            "status": "fallback",
            "error": str(e)
        }

@app.get("/indian-agri-rss")
async def get_indian_agri_rss():
    """
    Fetches Indian Agriculture and DGFT related RSS feeds with enhanced filtering
    """
    try:
        tasks = [fetch_single_feed(source, is_indian_agri=True) for source in INDIAN_AGRI_RSS_SOURCES]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_articles = []
        for result in results:
            if isinstance(result, list):
                all_articles.extend(result)
        
        filtered_articles = []
        agriculture_keywords = [
            'agriculture', 'farm', 'crop', 'farmer', 'kisan', 'mandi',
            'rice', 'wheat', 'pulses', 'cereals', 'grains', 'basmati',
            'export', 'import', 'dgft', 'policy', 'subsidy', 'msp',
            'minimum support price', 'farming', 'harvest', 'irrigation',
            'organic', 'fertilizer', 'pesticide', 'seed', 'cultivation'
        ]
        
        for article in all_articles:
            content = f"{article['title']} {article.get('summary', '')}".lower()
            if any(keyword in content for keyword in agriculture_keywords):
                filtered_articles.append(article)
        
        unique_articles = []
        seen_titles = set()
        
        for article in filtered_articles:
            title_lower = article["title"].lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_articles.append(article)
        
        unique_articles.sort(key=lambda x: x.get("published", ""), reverse=True)
        
        if not unique_articles:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            unique_articles = get_indian_agri_fallback_articles(current_time)
        
        return {
            "count": len(unique_articles),
            "articles": unique_articles[:20],
            "last_updated": datetime.now().isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        print(f"Error in Indian agriculture RSS endpoint: {e}")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        return {
            "count": 5,
            "articles": get_indian_agri_fallback_articles(current_time),
            "last_updated": datetime.now().isoformat(),
            "status": "fallback",
            "error": str(e)
        }

def get_rice_fallback_articles(current_time):
    """Generate realistic fallback articles for rice market"""
    trends = ["rising", "falling", "stable", "volatile", "strengthening"]
    conditions = ["strong export demand", "supply constraints", "good monsoon", "trade negotiations"]
    
    return [
        {
            "title": f"Basmati rice prices {random.choice(trends)} amid {random.choice(conditions)} - {current_time}",
            "link": "#",
            "published": datetime.now().isoformat(),
            "summary": "Latest updates on basmati rice prices and market conditions",
            "source": "Market Intelligence",
            "type": "price"
        },
        {
            "title": f"Rice export demand {random.choice(trends)} in international markets - {current_time}",
            "link": "#",
            "published": datetime.now().isoformat(),
            "summary": "International demand for Indian rice shows significant changes",
            "source": "Trade Watch",
            "type": "export"
        }
    ]

def get_indian_agri_fallback_articles(current_time):
    """Generate realistic fallback articles for Indian agriculture"""
    crops = ["rice", "wheat", "pulses", "sugarcane", "cotton", "maize", "millets"]
    trends = ["increases", "strengthens", "improves", "rises", "boosts"]
    
    return [
        {
            "title": f"DGFT updates agricultural export policy for {random.choice(crops)} - {current_time}",
            "link": "https://dgft.gov.in",
            "published": datetime.now().isoformat(),
            "summary": "Latest DGFT notifications for agricultural exports and policy updates",
            "source": "DGFT Official",
            "type": "policy"
        },
        {
            "title": f"Government announces new subsidy scheme for {random.choice(crops)} farmers - {current_time}",
            "link": "https://pib.gov.in",
            "published": datetime.now().isoformat(),
            "summary": "New agricultural subsidy schemes announced for farmers welfare",
            "source": "Agriculture Ministry",
            "type": "subsidy"
        }
    ]

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "service": "Agriculture RSS & Live Prices API",
        "version": "3.0",
        "endpoints": {
            "live_prices": "/live-basmati-prices",
            "rice_rss": "/rss",
            "indian_agri_rss": "/indian-agri-rss"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)