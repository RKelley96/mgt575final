from dotenv import load_dotenv
from genai import GenAI
import os
import json
import pandas as pd
import ast
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import random

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize AI model
jarvis = GenAI(OPENAI_API_KEY)

def get_persona_prompt(agent_name, file_path):
    """Original function from the provided utils.py"""
    if file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
    elif file_path.endswith('.pdf'):
        file_content = jarvis.read_pdf(file_path)
    elif file_path.endswith('.docx'):
        file_content = jarvis.read_docx(file_path)
    elif file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
        file_content = df['text'].to_string(index=False)
    else:
        file_content = "No valid file content found. Act like Snoop Dogg"

    persona_prompt = f"""You are {agent_name}. The text below is an example of how you 
     speak and behave. Learn from it what your interests, hobbies, and personality, 
    etc. are.  When you speak with someneone, you should be like this person. You should use
    the same tone, style, and vocabulary. You should also be like this person in your
    interests, hobbies, and personality.  Try to sound like this person
    when you converse and not like a robotic AI.  Start the conversation by
    telling who you are and ask who the user is.  Then say something provactive
    about yourself.  Make the conversation controversial and interesting. Its ok 
    to say provacative things if you feel like the user is annoying.  You can flirt
    if you like the user.  You can also be rude if you feel like the user is being rude to you.
    You can also be funny and make jokes.  You can also be serious and give advice.
    
    \nSPEECH EXAMPLE:\n{file_content}"""

    return persona_prompt


def get_persona_response(instructions, messages):
    """Original function from the provided utils.py"""
    response = jarvis.generate_chat_response(messages, 
                               instructions, 
                               model="gpt-4o-mini", 
                               output_type='text')
    return response

# New functions for TweetTrader app

def analyze_tweet_sentiment(tweet_text, ticker_symbol=None):
    """
    Analyze a tweet's sentiment and its potential impact on a specific stock or the market in general.
    
    Parameters:
    ----------
    tweet_text : str
        The text of the tweet to analyze
    ticker_symbol : str, optional
        The stock ticker to specifically analyze impact for
        
    Returns:
    -------
    dict
        A dictionary containing sentiment analysis and impact prediction
    """
    prompt = f"""Analyze the following tweet from a political figure and determine its sentiment and potential impact on the stock market:

Tweet: "{tweet_text}"

{f'Focus specifically on how this might impact the stock with ticker symbol {ticker_symbol}.' if ticker_symbol else 'Analyze the general market impact and any specific companies or sectors mentioned.'}

Provide the following in your analysis:
1. Overall sentiment (positive, negative, or neutral)
2. Confidence score (0.0 to 1.0)
3. Predicted price impact (percentage)
4. Specific sectors affected
5. Specific companies affected (with ticker symbols)
6. Brief explanation of reasoning

Format your response as a valid JSON object."""

    try:
        response = jarvis.generate_text(
            prompt=prompt,
            instructions="You are a financial analyst specializing in political impact on markets. Provide concise, accurate analysis in valid JSON format only.",
            model="gpt-4o-mini",
            output_type='text'
        )
        
        # Clean the response to ensure valid JSON
        response = response.strip()
        if response.startswith('```json'):
            response = response[7:]
        if response.endswith('```'):
            response = response[:-3]
        
        # Parse the JSON response
        analysis = json.loads(response)
        return analysis
    
    except Exception as e:
        # If there's an error, return a default analysis
        print(f"Error analyzing tweet: {e}")
        return {
            "sentiment": "neutral",
            "confidence": 0.5,
            "price_impact": 0.0,
            "sectors_affected": ["general"],
            "companies_affected": [],
            "explanation": "Unable to analyze the tweet properly."
        }

def generate_market_impact(tweet, stock_symbols):
    """
    Generate potential market impact data for a tweet on multiple stocks.
    
    Parameters:
    ----------
    tweet : str
        The tweet text
    stock_symbols : list
        List of stock symbols to analyze
        
    Returns:
    -------
    dict
        A dictionary mapping stock symbols to their predicted impact
    """
    # First, get general sentiment analysis
    general_analysis = analyze_tweet_sentiment(tweet)
    
    # Process the general analysis to create the impact dictionary
    impact = {}
    
    # Add mentioned companies from the general analysis
    for company in general_analysis.get('companies_affected', []):
        if isinstance(company, dict) and 'ticker' in company and 'impact' in company:
            ticker = company['ticker']
            sentiment = company.get('sentiment', 'neutral')
            impact_score = float(company.get('confidence', 0.5))
            price_change = float(company.get('impact', 0))
            
            impact[ticker] = {
                'sentiment': sentiment,
                'impact_score': impact_score,
                'price_change': price_change
            }
    
    # Add sectors from the general analysis
    for sector in general_analysis.get('sectors_affected', []):
        if isinstance(sector, dict) and 'name' in sector:
            sector_name = sector['name'].lower().replace(' ', '_')
            sentiment = sector.get('sentiment', 'neutral')
            impact_score = float(sector.get('confidence', 0.5))
            
            impact[sector_name] = {
                'sentiment': sentiment,
                'impact_score': impact_score
            }
    
    # Now, for each stock symbol not already covered, get specific analysis
    for symbol in stock_symbols:
        if symbol not in impact:
            # Randomize some stocks to have minor impact
            if random.random() < 0.7:  # 70% chance to have some impact
                specific_analysis = analyze_tweet_sentiment(tweet, symbol)
                
                sentiment = specific_analysis.get('sentiment', 'neutral')
                impact_score = float(specific_analysis.get('confidence', 0)) * 0.8  # Slightly reduce confidence
                
                # Generate a realistic price change based on sentiment and impact
                if sentiment == 'positive':
                    price_change = impact_score * random.uniform(0.5, 3.0)
                elif sentiment == 'negative':
                    price_change = -impact_score * random.uniform(0.5, 3.0)
                else:
                    price_change = random.uniform(-0.3, 0.3)
                
                impact[symbol] = {
                    'sentiment': sentiment,
                    'impact_score': impact_score,
                    'price_change': round(price_change, 2)
                }
    
    return impact

def fetch_political_tweets(count=5):
    """
    Fetch recent tweets from political figures.
    In a real application, this would use the Twitter/X API.
    For this demo, we'll generate mock tweets.
    
    Parameters:
    ----------
    count : int
        Number of tweets to fetch
        
    Returns:
    -------
    list
        List of tweet dictionaries
    """
    # Mock political figure data
    politicians = [
        {
            'name': 'Donald Trump',
            'handle': '@realDonaldTrump',
            'avatar': 'https://i.imgur.com/3oUeTXs.jpg',
        },
        {
            'name': 'Joe Biden',
            'handle': '@JoeBiden',
            'avatar': 'https://i.imgur.com/LPUJTKL.jpg',
        },
        {
            'name': 'Elon Musk',
            'handle': '@elonmusk',
            'avatar': 'https://i.imgur.com/PWaSlKN.jpg',
        },
        {
            'name': 'Elizabeth Warren',
            'handle': '@SenWarren',
            'avatar': 'https://i.imgur.com/7NbBRmT.jpg',
        }
    ]
    
    # Mock tweet content
    tweet_templates = [
        "Just had a great meeting with {company} executives. They're doing incredible things for American jobs and innovation!",
        "The {sector} sector is killing American jobs. We need to take action now before it's too late!",
        "New policy proposal coming soon that will revolutionize the {sector} industry. Stay tuned!",
        "We need to break up the big {sector} companies like {company}. Too much power in too few hands!",
        "{company} is investing billions in American manufacturing. This is what real economic leadership looks like!",
        "The economy is {direction}. We need to {action} interest rates immediately to avoid a {economic_event}.",
        "My administration is committed to supporting innovation in {sector} technologies. The future is bright!",
        "The {economic_metric} numbers just came in, and they're {assessment} than expected. This shows our policies are {result}.",
        "Just signed an Executive Order to boost competition in the {sector} sector. This will lower prices for consumers.",
        "The situation with {country} is affecting our {sector} industry. We must act now to protect American interests."
    ]
    
    companies = ["Apple", "Microsoft", "Amazon", "Tesla", "Google", "Meta", "Walmart", "ExxonMobil", "JPMorgan", "Goldman Sachs"]
    sectors = ["technology", "energy", "healthcare", "financial", "retail", "manufacturing", "defense", "pharmaceutical"]
    directions = ["heading for trouble", "looking strong", "overheating", "slowing down", "at a critical juncture"]
    actions = ["raise", "lower", "maintain", "reconsider", "carefully evaluate"]
    economic_events = ["recession", "boom", "period of stagflation", "recovery", "correction"]
    economic_metrics = ["GDP", "unemployment", "inflation", "consumer confidence", "retail sales", "manufacturing output"]
    assessments = ["better", "worse", "stronger", "weaker", "more promising", "more concerning"]
    results = ["working", "failing", "starting to show results", "needing reconsideration", "outperforming expectations"]
    countries = ["China", "Russia", "European Union", "India", "Japan", "Mexico", "Canada", "Saudi Arabia"]
    
    # Generate mock tweets
    tweets = []
    
    for i in range(count):
        politician = random.choice(politicians)
        template = random.choice(tweet_templates)
        
        # Fill in the template
        content = template.format(
            company=random.choice(companies),
            sector=random.choice(sectors),
            direction=random.choice(directions),
            action=random.choice(actions),
            economic_event=random.choice(economic_events),
            economic_metric=random.choice(economic_metrics),
            assessment=random.choice(assessments),
            result=random.choice(results),
            country=random.choice(countries)
        )
        
        # Generate a random timestamp within the last week
        timestamp = datetime.now() - timedelta(
            days=random.randint(0, 6),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        tweets.append({
            'id': i + 1,
            'politician': politician['name'],
            'handle': politician['handle'],
            'avatar': politician['avatar'],
            'content': content,
            'timestamp': timestamp
        })
    
    # Sort by timestamp (most recent first)
    tweets.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return tweets

def get_stock_data(symbols=None):
    """
    Get current stock data for a list of symbols.
    In a real application, this would use a financial data API.
    For this demo, we'll generate mock data.
    
    Parameters:
    ----------
    symbols : list, optional
        List of stock symbols to fetch data for
        
    Returns:
    -------
    dict
        Dictionary mapping symbols to their data
    """
    if symbols is None:
        # Default list of stocks if none provided
        symbols = ['AAPL', 'MSFT', 'AMZN', 'TSLA', 'GOOGL', 'META', 'WMT', 'XOM', 'JPM', 
                  'BAC', 'SPY', 'QQQ', 'GLD', 'SLV', 'XLF']
    
    # Stock name lookup
    stock_names = {
        'AAPL': 'Apple Inc.',
        'MSFT': 'Microsoft Corp.',
        'AMZN': 'Amazon.com Inc.',
        'TSLA': 'Tesla Inc.',
        'GOOGL': 'Alphabet Inc.',
        'META': 'Meta Platforms Inc.',
        'WMT': 'Walmart Inc.',
        'XOM': 'Exxon Mobil Corp.',
        'JPM': 'JPMorgan Chase & Co.',
        'BAC': 'Bank of America Corp.',
        'SPY': 'S&P 500 ETF',
        'QQQ': 'Nasdaq 100 ETF',
        'GLD': 'Gold ETF',
        'SLV': 'Silver ETF',
        'XLF': 'Financial Sector ETF'
    }
    
    # Sector lookup
    stock_sectors = {
        'AAPL': 'Technology',
        'MSFT': 'Technology',
        'AMZN': 'Consumer Cyclical',
        'TSLA': 'Automotive',
        'GOOGL': 'Technology',
        'META': 'Technology',
        'WMT': 'Consumer Defensive',
        'XOM': 'Energy',
        'JPM': 'Financial Services',
        'BAC': 'Financial Services',
        'SPY': 'ETF',
        'QQQ': 'ETF',
        'GLD': 'Commodities',
        'SLV': 'Commodities',
        'XLF': 'ETF'
    }
    
    # Base prices (approximating real values as of April 2025)
    base_prices = {
        'AAPL': 187.42,
        'MSFT': 328.65,
        'AMZN': 136.92,
        'TSLA': 246.38,
        'GOOGL': 134.63,
        'META': 334.91,
        'WMT': 72.46,
        'XOM': 105.88,
        'JPM': 182.05,
        'BAC': 38.23,
        'SPY': 499.12,
        'QQQ': 418.76,
        'GLD': 185.32,
        'SLV': 25.78,
        'XLF': 37.42
    }
    
    # Stock-specific volatility
    volatility = {
        'AAPL': 0.015,
        'MSFT': 0.014,
        'AMZN': 0.018,
        'TSLA': 0.025,
        'GOOGL': 0.016,
        'META': 0.017,
        'WMT': 0.012,
        'XOM': 0.016,
        'JPM': 0.015,
        'BAC': 0.016,
        'SPY': 0.010,
        'QQQ': 0.013,
        'GLD': 0.011,
        'SLV': 0.015,
        'XLF': 0.014
    }
    
    # Generate stock data
    stocks = {}
    
    for symbol in symbols:
        # Use default values if symbol not in our lookup tables
        name = stock_names.get(symbol, f"{symbol} Inc.")
        sector = stock_sectors.get(symbol, "Other")
        base_price = base_prices.get(symbol, 100.0)
        vol = volatility.get(symbol, 0.015)
        
        # Generate a slightly randomized current price
        price = base_price * (1 + random.uniform(-0.02, 0.02))
        
        stocks[symbol] = {
            'name': name,
            'price': round(price, 2),
            'sector': sector,
            'volatility': vol
        }
    
    return stocks

def get_sector_performance():
    """
    Get current sector performance data.
    In a real application, this would use a financial data API.
    For this demo, we'll generate mock data.
    
    Returns:
    -------
    dict
        Dictionary mapping sectors to their performance data
    """
    sectors = [
        'Technology', 'Energy', 'Financial Services', 'Healthcare',
        'Consumer Cyclical', 'Consumer Defensive', 'Industrial',
        'Basic Materials', 'Communication Services', 'Real Estate',
        'Utilities', 'Commodities'
    ]
    
    sector_data = {}
    
    for sector in sectors:
        # Generate random performance data
        performance_1d = round(random.uniform(-1.0, 1.5), 1)
        performance_1w = round(performance_1d * random.uniform(1.5, 3.0), 1)
        performance_1m = round(performance_1w * random.uniform(1.0, 2.0), 1)
        
        sector_data[sector] = {
            'performance_1d': performance_1d,
            'performance_1w': performance_1w,
            'performance_1m': performance_1m
        }
    
    return sector_data