import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import time
import re

# Set page configuration
st.set_page_config(
    page_title="TweetTrader: Political Social Media Market Simulator",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1DA1F2;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 1rem;
    }
    .category-header {
        font-size: 1.2rem;
        font-weight: bold;
        margin-top: 0.8rem;
    }
    .info-text {
        font-size: 1rem;
        color: #555;
    }
    .highlight {
        background-color: #f0f7fb;
        border-left: 5px solid #1DA1F2;
        padding: 0.5rem 1rem;
        margin-bottom: 1rem;
    }
    .profit {
        color: #0faf0f;
        font-weight: bold;
    }
    .loss {
        color: #ff4040;
        font-weight: bold;
    }
    .neutral {
        color: #777;
    }
    .tweet-box {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        background-color: #f8f9fa;
    }
    .impact-high {
        background-color: rgba(255, 64, 64, 0.1);
        border-left: 3px solid #ff4040;
        padding: 0.5rem;
    }
    .impact-medium {
        background-color: rgba(255, 173, 51, 0.1);
        border-left: 3px solid #ffad33;
        padding: 0.5rem;
    }
    .impact-low {
        background-color: rgba(77, 175, 74, 0.1);
        border-left: 3px solid #4daf4a;
        padding: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {
        'cash': 100000.0,
        'stocks': {},
        'history': [],
        'current_value': 100000.0,
        'starting_value': 100000.0,
        'transactions': []
    }

if 'tweets' not in st.session_state:
    # Create sample political tweets with their impact
    st.session_state.tweets = [
        {
            'id': 1,
            'politician': 'Donald Trump',
            'handle': '@realDonaldTrump',
            'avatar': 'https://i.imgur.com/3oUeTXs.jpg',
            'content': 'Just got off the phone with Tim Cook of Apple. They will be building massive plants in the USA! JOBS! JOBS! JOBS!',
            'timestamp': datetime.now() - timedelta(days=3, hours=5),
            'impact': {
                'AAPL': {'sentiment': 'positive', 'impact_score': 0.82, 'price_change': 2.3},
                'MSFT': {'sentiment': 'negative', 'impact_score': 0.35, 'price_change': -0.7},
                'technology': {'sentiment': 'positive', 'impact_score': 0.65},
                'manufacturing': {'sentiment': 'positive', 'impact_score': 0.77}
            }
        },
        {
            'id': 2,
            'politician': 'Donald Trump',
            'handle': '@realDonaldTrump',
            'avatar': 'https://i.imgur.com/3oUeTXs.jpg',
            'content': 'Amazon is doing great damage to tax paying retailers. Towns, cities and states throughout the U.S. are being hurt - many jobs being lost!',
            'timestamp': datetime.now() - timedelta(days=2, hours=8),
            'impact': {
                'AMZN': {'sentiment': 'negative', 'impact_score': 0.89, 'price_change': -2.8},
                'WMT': {'sentiment': 'positive', 'impact_score': 0.41, 'price_change': 0.9},
                'retail': {'sentiment': 'mixed', 'impact_score': 0.62},
                'ecommerce': {'sentiment': 'negative', 'impact_score': 0.76}
            }
        },
        {
            'id': 3,
            'politician': 'Joe Biden',
            'handle': '@JoeBiden',
            'avatar': 'https://i.imgur.com/LPUJTKL.jpg',
            'content': 'Its time to build a clean energy future. My plan will create millions of good-paying jobs in wind, solar, and manufacturing while tackling climate change.',
            'timestamp': datetime.now() - timedelta(days=1, hours=12),
            'impact': {
                'TSLA': {'sentiment': 'positive', 'impact_score': 0.75, 'price_change': 3.2},
                'XOM': {'sentiment': 'negative', 'impact_score': 0.69, 'price_change': -1.8},
                'clean_energy': {'sentiment': 'positive', 'impact_score': 0.91},
                'oil_gas': {'sentiment': 'negative', 'impact_score': 0.84}
            }
        },
        {
            'id': 4,
            'politician': 'Elon Musk',
            'handle': '@elonmusk',
            'avatar': 'https://i.imgur.com/PWaSlKN.jpg',
            'content': 'The economy is not looking good. Fed needs to cut interest rates immediately or we risk a serious recession.',
            'timestamp': datetime.now() - timedelta(hours=6),
            'impact': {
                'SPY': {'sentiment': 'negative', 'impact_score': 0.72, 'price_change': -1.5},
                'TSLA': {'sentiment': 'negative', 'impact_score': 0.62, 'price_change': -2.1},
                'GLD': {'sentiment': 'positive', 'impact_score': 0.58, 'price_change': 1.2},
                'finance': {'sentiment': 'negative', 'impact_score': 0.65},
                'tech': {'sentiment': 'negative', 'impact_score': 0.59}
            }
        },
        {
            'id': 5,
            'politician': 'Donald Trump',
            'handle': '@realDonaldTrump',
            'avatar': 'https://i.imgur.com/3oUeTXs.jpg',
            'content': 'Big announcement coming soon about tax cuts for American businesses! Were going to supercharge this economy like never before. MAGA!',
            'timestamp': datetime.now() - timedelta(hours=1),
            'impact': {
                'SPY': {'sentiment': 'positive', 'impact_score': 0.81, 'price_change': 1.7},
                'XLF': {'sentiment': 'positive', 'impact_score': 0.75, 'price_change': 2.3},
                'SLV': {'sentiment': 'negative', 'impact_score': 0.42, 'price_change': -0.8},
                'financial': {'sentiment': 'positive', 'impact_score': 0.79},
                'small_business': {'sentiment': 'positive', 'impact_score': 0.88}
            }
        }
    ]

if 'stocks' not in st.session_state:
    # Create sample stock data
    st.session_state.stocks = {
        'AAPL': {'name': 'Apple Inc.', 'price': 187.42, 'sector': 'Technology', 'volatility': 0.015},
        'MSFT': {'name': 'Microsoft Corp.', 'price': 328.65, 'sector': 'Technology', 'volatility': 0.014},
        'AMZN': {'name': 'Amazon.com Inc.', 'price': 136.92, 'sector': 'Consumer Cyclical', 'volatility': 0.018},
        'TSLA': {'name': 'Tesla Inc.', 'price': 246.38, 'sector': 'Automotive', 'volatility': 0.025},
        'GOOGL': {'name': 'Alphabet Inc.', 'price': 134.63, 'sector': 'Technology', 'volatility': 0.016},
        'META': {'name': 'Meta Platforms Inc.', 'price': 334.91, 'sector': 'Technology', 'volatility': 0.017},
        'WMT': {'name': 'Walmart Inc.', 'price': 72.46, 'sector': 'Consumer Defensive', 'volatility': 0.012},
        'XOM': {'name': 'Exxon Mobil Corp.', 'price': 105.88, 'sector': 'Energy', 'volatility': 0.016},
        'JPM': {'name': 'JPMorgan Chase & Co.', 'price': 182.05, 'sector': 'Financial Services', 'volatility': 0.015},
        'BAC': {'name': 'Bank of America Corp.', 'price': 38.23, 'sector': 'Financial Services', 'volatility': 0.016},
        'SPY': {'name': 'S&P 500 ETF', 'price': 499.12, 'sector': 'ETF', 'volatility': 0.010},
        'QQQ': {'name': 'Nasdaq 100 ETF', 'price': 418.76, 'sector': 'ETF', 'volatility': 0.013},
        'GLD': {'name': 'Gold ETF', 'price': 185.32, 'sector': 'Commodities', 'volatility': 0.011},
        'SLV': {'name': 'Silver ETF', 'price': 25.78, 'sector': 'Commodities', 'volatility': 0.015},
        'XLF': {'name': 'Financial Sector ETF', 'price': 37.42, 'sector': 'ETF', 'volatility': 0.014}
    }

if 'sectors' not in st.session_state:
    # Create sample sector performance
    st.session_state.sectors = {
        'Technology': {'performance_1d': 0.8, 'performance_1w': 2.1, 'performance_1m': 3.5},
        'Energy': {'performance_1d': -0.3, 'performance_1w': 1.2, 'performance_1m': -2.1},
        'Financial Services': {'performance_1d': 0.5, 'performance_1w': 1.5, 'performance_1m': 2.8},
        'Healthcare': {'performance_1d': 0.2, 'performance_1w': 0.9, 'performance_1m': 1.7},
        'Consumer Cyclical': {'performance_1d': 0.6, 'performance_1w': 1.8, 'performance_1m': 2.5},
        'Consumer Defensive': {'performance_1d': 0.1, 'performance_1w': 0.5, 'performance_1m': 1.2},
        'Industrial': {'performance_1d': 0.4, 'performance_1w': 1.6, 'performance_1m': 2.3},
        'Basic Materials': {'performance_1d': -0.2, 'performance_1w': 0.8, 'performance_1m': 1.5},
        'Communication Services': {'performance_1d': 0.7, 'performance_1w': 1.9, 'performance_1m': 3.1},
        'Real Estate': {'performance_1d': 0.3, 'performance_1w': 1.0, 'performance_1m': 1.8},
        'Utilities': {'performance_1d': 0.0, 'performance_1w': 0.6, 'performance_1m': 1.0},
        'Commodities': {'performance_1d': 0.5, 'performance_1w': 1.3, 'performance_1m': 2.0},
    }

if 'portfolio_history' not in st.session_state:
    # Initialize portfolio history with some random data
    dates = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]
    values = [100000]
    for i in range(1, 30):
        change = random.uniform(-0.015, 0.018)
        values.append(values[i-1] * (1 + change))
    
    st.session_state.portfolio_history = pd.DataFrame({
        'Date': dates,
        'Value': values
    })


# Helper functions
def simulate_price_impact(tweet, stock_symbol, base_price, days=1):
    """Simulate the impact of a tweet on a stock price over time"""
    impact = tweet['impact'].get(stock_symbol, {'sentiment': 'neutral', 'impact_score': 0.1, 'price_change': 0})
    
    # Get impact details
    sentiment = impact['sentiment']
    impact_score = impact['impact_score']
    estimated_change = impact['price_change'] / 100  # Convert percentage to decimal
    
    # Create price data
    hours = days * 24
    timestamps = [datetime.now() + timedelta(hours=i) for i in range(hours)]
    
    # Model the price change with some randomness
    prices = [base_price]
    for i in range(1, hours):
        # Calculate how much of the impact has been realized
        time_factor = min(i / (hours * 0.6), 1)  # Most impact happens in first 60% of time
        
        # Add some random noise
        noise = np.random.normal(0, 0.001)
        
        if sentiment == 'positive':
            change = base_price * estimated_change * time_factor + noise
        elif sentiment == 'negative':
            change = base_price * estimated_change * time_factor + noise
        else:
            change = base_price * noise
            
        # Ensure we don't go negative
        new_price = max(prices[-1] + change, 0.01)
        prices.append(new_price)
    
    return pd.DataFrame({'Timestamp': timestamps, 'Price': prices})

def update_portfolio_value():
    """Calculate the current value of the portfolio"""
    cash = st.session_state.portfolio['cash']
    stock_value = 0
    
    for symbol, details in st.session_state.portfolio['stocks'].items():
        stock_value += details['shares'] * st.session_state.stocks[symbol]['price']
    
    st.session_state.portfolio['current_value'] = cash + stock_value
    
    # Update portfolio history
    if len(st.session_state.portfolio_history) > 0:
        last_date = st.session_state.portfolio_history['Date'].iloc[-1]
        if datetime.now().date() != last_date.date():
            new_row = pd.DataFrame({
                'Date': [datetime.now()],
                'Value': [st.session_state.portfolio['current_value']]
            })
            st.session_state.portfolio_history = pd.concat([st.session_state.portfolio_history, new_row], ignore_index=True)

def get_impact_class(impact_score):
    """Return the CSS class based on impact score"""
    if impact_score > 0.7:
        return "impact-high"
    elif impact_score > 0.4:
        return "impact-medium"
    else:
        return "impact-low"

def execute_trade(symbol, shares, action):
    """Execute a buy or sell trade"""
    current_price = st.session_state.stocks[symbol]['price']
    value = shares * current_price
    
    if action == 'buy':
        # Check if we have enough cash
        if value > st.session_state.portfolio['cash']:
            st.error(f"Insufficient funds to buy {shares} shares of {symbol}")
            return False
        
        # Execute buy
        st.session_state.portfolio['cash'] -= value
        
        # Update portfolio
        if symbol in st.session_state.portfolio['stocks']:
            st.session_state.portfolio['stocks'][symbol]['shares'] += shares
            avg_price = st.session_state.portfolio['stocks'][symbol]['avg_price']
            old_shares = st.session_state.portfolio['stocks'][symbol]['shares'] - shares
            st.session_state.portfolio['stocks'][symbol]['avg_price'] = (avg_price * old_shares + current_price * shares) / st.session_state.portfolio['stocks'][symbol]['shares']
        else:
            st.session_state.portfolio['stocks'][symbol] = {
                'shares': shares,
                'avg_price': current_price
            }
    
    elif action == 'sell':
        # Check if we have enough shares
        if symbol not in st.session_state.portfolio['stocks'] or st.session_state.portfolio['stocks'][symbol]['shares'] < shares:
            st.error(f"Insufficient shares to sell {shares} shares of {symbol}")
            return False
        
        # Execute sell
        st.session_state.portfolio['cash'] += value
        
        # Update portfolio
        st.session_state.portfolio['stocks'][symbol]['shares'] -= shares
        
        # Remove from portfolio if no shares left
        if st.session_state.portfolio['stocks'][symbol]['shares'] == 0:
            del st.session_state.portfolio['stocks'][symbol]
    
    # Record transaction
    st.session_state.portfolio['transactions'].append({
        'timestamp': datetime.now(),
        'symbol': symbol,
        'shares': shares,
        'price': current_price,
        'action': action,
        'value': value
    })
    
    # Update portfolio value
    update_portfolio_value()
    
    return True

# Main app layout
st.markdown('<div class="main-header">📊 TweetTrader: Political Social Media Market Simulator</div>', unsafe_allow_html=True)
st.markdown("""
<div class="info-text">
Trade the markets based on political tweets and their predicted impact. 
Monitor political figures, analyze market sentiment, and build your simulated portfolio!
</div>
""", unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Tweet Monitor", "Market Analysis", "Trading Simulator", "Portfolio Dashboard"])

with tab1:
    st.markdown('<div class="sub-header">Political Social Media Monitor</div>', unsafe_allow_html=True)
    st.markdown("""
    Monitor tweets from political figures and see their predicted market impact. 
    Use this intelligence to make trading decisions in the simulator tab.
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Filter options
        st.markdown('<div class="category-header">Filter Tweets</div>', unsafe_allow_html=True)
        politicians = list(set([tweet['politician'] for tweet in st.session_state.tweets]))
        selected_politicians = st.multiselect("Select Politicians", options=politicians, default=politicians)
        
        # Display tweets
        st.markdown('<div class="category-header">Recent Tweets</div>', unsafe_allow_html=True)
        
        filtered_tweets = [tweet for tweet in st.session_state.tweets if tweet['politician'] in selected_politicians]
        filtered_tweets.sort(key=lambda x: x['timestamp'], reverse=True)
        
        for tweet in filtered_tweets:
            with st.container():
                st.markdown(f"""
                <div class="tweet-box">
                    <p><strong>{tweet['politician']}</strong> {tweet['handle']} • {tweet['timestamp'].strftime('%b %d, %Y %I:%M %p')}</p>
                    <p>{tweet['content']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show market impact
                st.markdown('<span style="font-size:0.9rem; font-weight:bold;">Predicted Market Impact:</span>', unsafe_allow_html=True)
                
                impact_cols = st.columns(4)
                
                # Show stock impact
                stock_impacts = [(k, v) for k, v in tweet['impact'].items() if k in st.session_state.stocks]
                for i, (symbol, impact) in enumerate(stock_impacts):
                    with impact_cols[i % 4]:
                        sentiment_color = "green" if impact['sentiment'] == 'positive' else "red" if impact['sentiment'] == 'negative' else "gray"
                        change_str = f"+{impact['price_change']}%" if impact['price_change'] > 0 else f"{impact['price_change']}%"
                        st.markdown(f"""
                        <div class="{get_impact_class(impact['impact_score'])}">
                            <strong>{symbol}</strong>: <span style="color:{sentiment_color};">{change_str}</span><br>
                            <small>Confidence: {int(impact['impact_score']*100)}%</small>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Show trade buttons
                trade_cols = st.columns(len(stock_impacts))
                for i, (symbol, impact) in enumerate(stock_impacts):
                    with trade_cols[i]:
                        if st.button(f"Simulate Trade - {symbol}", key=f"sim_{tweet['id']}_{symbol}"):
                            # Set up the trading tab with this stock pre-selected
                            st.session_state['selected_ticker'] = symbol
                            st.session_state['active_tab'] = 2  # Switch to trading tab
                
                st.markdown("---")
    
    with col2:
        st.markdown('<div class="category-header">Impact Analysis</div>', unsafe_allow_html=True)
        
        # Create sector impact chart based on selected tweets
        sector_impact = {}
        
        for tweet in filtered_tweets:
            for key, impact in tweet['impact'].items():
                if key not in st.session_state.stocks:  # This is a sector, not a stock
                    if key not in sector_impact:
                        sector_impact[key] = []
                    
                    impact_value = impact['impact_score']
                    if impact['sentiment'] == 'negative':
                        impact_value = -impact_value
                    elif impact['sentiment'] == 'mixed':
                        impact_value = impact_value * 0.2  # Reduce impact for mixed sentiment
                        
                    sector_impact[key].append(impact_value)
        
        # Average the impacts
        avg_sector_impact = {}
        for sector, impacts in sector_impact.items():
            avg_sector_impact[sector] = sum(impacts) / len(impacts)
        
        # Create the chart
        if avg_sector_impact:
            sectors = list(avg_sector_impact.keys())
            impacts = list(avg_sector_impact.values())
            
            colors = ['green' if i > 0 else 'red' for i in impacts]
            
            fig = px.bar(
                x=sectors, 
                y=impacts,
                labels={'x': 'Sector', 'y': 'Sentiment Impact'},
                title='Sector Impact Based on Recent Tweets'
            )
            
            fig.update_traces(marker_color=colors)
            fig.update_layout(height=400)
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Show top impacted stocks
        st.markdown('<div class="category-header">Most Impacted Stocks</div>', unsafe_allow_html=True)
        
        stock_impacts = {}
        for tweet in filtered_tweets:
            for key, impact in tweet['impact'].items():
                if key in st.session_state.stocks:  # This is a stock, not a sector
                    if key not in stock_impacts:
                        stock_impacts[key] = []
                    
                    stock_impacts[key].append({
                        'impact_score': impact['impact_score'],
                        'sentiment': impact['sentiment'],
                        'price_change': impact['price_change'],
                        'timestamp': tweet['timestamp']
                    })
        
        # Find most impacted stocks
        stock_avg_impact = {}
        for stock, impacts in stock_impacts.items():
            # Prioritize recent impacts
            weighted_sum = 0
            weight_sum = 0
            
            for impact in impacts:
                # Calculate time-based weight (more recent = higher weight)
                hours_ago = (datetime.now() - impact['timestamp']).total_seconds() / 3600
                time_weight = max(1.0, 24 - hours_ago) / 24  # Linear decay over 24 hours
                
                weighted_sum += abs(impact['price_change']) * time_weight
                weight_sum += time_weight
            
            if weight_sum > 0:
                stock_avg_impact[stock] = weighted_sum / weight_sum
        
        # Sort by absolute impact
        sorted_stocks = sorted(stock_avg_impact.items(), key=lambda x: x[1], reverse=True)
        
        # Display top 5 impacted stocks
        if sorted_stocks:
            for i, (stock, impact) in enumerate(sorted_stocks[:5]):
                latest_impact = max(stock_impacts[stock], key=lambda x: x['timestamp'])
                sentiment = latest_impact['sentiment']
                price_change = latest_impact['price_change']
                
                sentiment_color = "green" if sentiment == 'positive' else "red" if sentiment == 'negative' else "gray"
                change_str = f"+{price_change}%" if price_change > 0 else f"{price_change}%"
                
                st.markdown(f"""
                <div style="padding: 10px; margin-bottom: 5px; border-radius: 5px; background-color: #f8f9fa;">
                    <strong>{stock}</strong> ({st.session_state.stocks[stock]['name']})<br>
                    Expected Impact: <span style="color:{sentiment_color};">{change_str}</span><br>
                    <small>Confidence: {int(latest_impact['impact_score']*100)}%</small>
                </div>
                """, unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="sub-header">Market Analysis</div>', unsafe_allow_html=True)
    st.markdown("""
    Analyze how political tweets have historically impacted various market sectors and stocks.
    Use these insights to inform your trading strategy.
    """)
    
    market_col1, market_col2 = st.columns([1, 1])
    
    with market_col1:
        # Stock price prediction based on selected tweet
        st.markdown('<div class="category-header">Tweet Impact Simulator</div>', unsafe_allow_html=True)
        
        # Select a tweet
        tweet_options = [f"{t['politician']}: {t['content'][:50]}..." for t in st.session_state.tweets]
        selected_tweet_index = st.selectbox("Select a Tweet to Analyze", range(len(tweet_options)), format_func=lambda x: tweet_options[x])
        selected_tweet = st.session_state.tweets[selected_tweet_index]
        
        # Select a stock to analyze
        impacted_stocks = [k for k in selected_tweet['impact'].keys() if k in st.session_state.stocks]
        if impacted_stocks:
            selected_stock = st.selectbox("Select Stock to Analyze", impacted_stocks)
            
            # Display the tweet
            st.markdown(f"""
            <div class="tweet-box">
                <p><strong>{selected_tweet['politician']}</strong> {selected_tweet['handle']} • {selected_tweet['timestamp'].strftime('%b %d, %Y %I:%M %p')}</p>
                <p>{selected_tweet['content']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Simulate price impact
            base_price = st.session_state.stocks[selected_stock]['price']
            impact_data = simulate_price_impact(selected_tweet, selected_stock, base_price, days=3)
            
            # Plot the predicted price movement
            fig = px.line(
                impact_data, 
                x='Timestamp', 
                y='Price',
                title=f"Predicted {selected_stock} Price Movement After Tweet"
            )
            
            # Add current price line
            fig.add_hline(
                y=base_price,
                line_dash="dash",
                line_color="gray",
                annotation_text="Current Price"
            )
            
            # Color the line based on price direction
            price_direction = "increasing" if impact_data['Price'].iloc[-1] > impact_data['Price'].iloc[0] else "decreasing"
            line_color = "green" if price_direction == "increasing" else "red"
            
            fig.update_traces(line_color=line_color)
            fig.update_layout(height=400)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display predicted change
            start_price = impact_data['Price'].iloc[0]
            end_price = impact_data['Price'].iloc[-1]
            percent_change = ((end_price - start_price) / start_price) * 100
            
            change_color = "green" if percent_change > 0 else "red"
            change_sign = "+" if percent_change > 0 else ""
            
            st.markdown(f"""
            <div class="highlight">
                <p>Predicted 3-Day Impact on {selected_stock}:</p>
                <p style="font-size: 1.2rem; color: {change_color};">{change_sign}{percent_change:.2f}%</p>
                <p>Price change from ${start_price:.2f} to ${end_price:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Add a button to trade this stock
            if st.button("Trade This Stock"):
                # Set up the trading tab with this stock pre-selected
                st.session_state['selected_ticker'] = selected_stock
                st.session_state['active_tab'] = 2  # Switch to trading tab
        else:
            st.info("This tweet doesn't have predicted stock impacts.")
    
    with market_col2:
        # Sector performance
        st.markdown('<div class="category-header">Sector Performance</div>', unsafe_allow_html=True)
        
        # Create sector performance chart
        sectors = list(st.session_state.sectors.keys())
        performance_1d = [st.session_state.sectors[s]['performance_1d'] for s in sectors]
        performance_1w = [st.session_state.sectors[s]['performance_1w'] for s in sectors]
        
        # Create dataframe for chart
        performance_df = pd.DataFrame({
            'Sector': sectors,
            'Daily Change (%)': performance_1d,
            'Weekly Change (%)': performance_1w
        })
        
        # Sort by daily performance
        performance_df = performance_df.sort_values('Daily Change (%)', ascending=False)
        
        # Create the chart
        fig = px.bar(
            performance_df,
            x='Sector',
            y=['Daily Change (%)', 'Weekly Change (%)'],
            barmode='group',
            title='Sector Performance'
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Politician influence rankings
        st.markdown('<div class="category-header">Politician Market Influence Rankings</div>', unsafe_allow_html=True)
        
        # Calculate influence based on impact scores
        politician_influence = {}
        for tweet in st.session_state.tweets:
            politician = tweet['politician']
            if politician not in politician_influence:
                politician_influence[politician] = {'tweets': 0, 'impact_sum': 0, 'avg_impact': 0}
            
            # Count the tweet
            politician_influence[politician]['tweets'] += 1
            
            # Sum the impact scores of all impacted stocks/sectors
            impact_sum = 0
            for _, impact in tweet['impact'].items():
                impact_sum += impact['impact_score']
            
            politician_influence[politician]['impact_sum'] += impact_sum
        
        # Calculate average impact
        for politician in politician_influence:
            politician_influence[politician]['avg_impact'] = (
                politician_influence[politician]['impact_sum'] / 
                politician_influence[politician]['tweets']
            )
        
        # Sort by average impact
        sorted_politicians = sorted(
            politician_influence.items(), 
            key=lambda x: x[1]['avg_impact'], 
            reverse=True
        )
        
        # Create the chart
        politician_names = [p[0] for p in sorted_politicians]
        avg_impacts = [p[1]['avg_impact'] for p in sorted_politicians]
        tweet_counts = [p[1]['tweets'] for p in sorted_politicians]
        
        fig = go.Figure()
        
        # Add avg impact bars
        fig.add_trace(go.Bar(
            x=politician_names,
            y=avg_impacts,
            name='Average Market Impact',
            marker_color='royalblue'
        ))
        
        # Add secondary y-axis for tweet count
        fig.add_trace(go.Scatter(
            x=politician_names,
            y=tweet_counts,
            name='Number of Tweets',
            marker_color='red',
            mode='markers',
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Politician Market Influence Rankings',
            yaxis=dict(title='Average Market Impact Score'),
            yaxis2=dict(title='Number of Tweets', overlaying='y', side='right'),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown('<div class="sub-header">Trading Simulator</div>', unsafe_allow_html=True)
    st.markdown("""
    Execute simulated trades based on your analysis of political tweets and their market impact.
    Build a portfolio and track your performance over time.
    """)
    
    trade_col1, trade_col2 = st.columns([1, 1])
    
    with trade_col1:
        # Stock selector
        st.markdown('<div class="category-header">Stock Selector</div>', unsafe_allow_html=True)
        
        # Check if we have a pre-selected ticker from another tab
        if 'selected_ticker' not in st.session_state:
            st.session_state['selected_ticker'] = list(st.session_state.stocks.keys())[0]
        
        selected_ticker = st.selectbox(
            "Select a stock to trade:",
            options=list(st.session_state.stocks.keys()),
            index=list(st.session_state.stocks.keys()).index(st.session_state['selected_ticker']),
            key="trading_ticker_selector"
        )
        
        # Update the selected ticker in session state
        st.session_state['selected_ticker'] = selected_ticker
        
        # Display stock info
        stock_info = st.session_state.stocks[selected_ticker]
        
        st.markdown(f"""
        <div class="highlight">
            <p><strong>{selected_ticker}</strong> - {stock_info['name']}</p>
            <p>Current Price: <span style="font-size: 1.2rem; font-weight: bold;">${stock_info['price']:.2f}</span></p>
            <p>Sector: {stock_info['sector']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show recent tweet impacts on this stock
        st.markdown('<div class="category-header">Recent Tweet Impacts</div>', unsafe_allow_html=True)
        
        relevant_tweets = []
        for tweet in st.session_state.tweets:
            if selected_ticker in tweet['impact']:
                relevant_tweets.append({
                    'tweet': tweet,
                    'impact': tweet['impact'][selected_ticker]
                })
        
        # Sort by recency
        relevant_tweets.sort(key=lambda x: x['tweet']['timestamp'], reverse=True)
        
        if relevant_tweets:
            for tweet_data in relevant_tweets:
                tweet = tweet_data['tweet']
                impact = tweet_data['impact']
                
                sentiment_color = "green" if impact['sentiment'] == 'positive' else "red" if impact['sentiment'] == 'negative' else "gray"
                change_str = f"+{impact['price_change']}%" if impact['price_change'] > 0 else f"{impact['price_change']}%"
                
                st.markdown(f"""
                <div class="tweet-box">
                    <p><strong>{tweet['politician']}</strong> {tweet['handle']} • {tweet['timestamp'].strftime('%b %d, %Y %I:%M %p')}</p>
                    <p>{tweet['content']}</p>
                    <p>Impact: <span style="color:{sentiment_color};">{change_str}</span> (Confidence: {int(impact['impact_score']*100)}%)</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(f"No recent tweets have mentioned {selected_ticker}")
        
    with trade_col2:
        # Trading interface
        st.markdown('<div class="category-header">Execute Trade</div>', unsafe_allow_html=True)
        
        # Show current position if any
        current_position = st.session_state.portfolio['stocks'].get(selected_ticker, None)
        
        if current_position:
            current_shares = current_position['shares']
            avg_price = current_position['avg_price']
            current_value = current_shares * stock_info['price']
            pnl = current_value - (current_shares * avg_price)
            pnl_pct = (pnl / (current_shares * avg_price)) * 100 if current_shares > 0 else 0
            
            pnl_color = "green" if pnl > 0 else "red" if pnl < 0 else "gray"
            pnl_sign = "+" if pnl > 0 else ""
            
            st.markdown(f"""
            <div class="highlight">
                <p><strong>Current Position</strong></p>
                <p>Shares: {current_shares}</p>
                <p>Average Price: ${avg_price:.2f}</p>
                <p>Current Value: ${current_value:.2f}</p>
                <p>P&L: <span style="color:{pnl_color};">{pnl_sign}${pnl:.2f} ({pnl_sign}{pnl_pct:.2f}%)</span></p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="highlight">
                <p>You don't currently own any shares of this stock.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Trade type
        trade_type = st.radio("Trade Type", options=["Buy", "Sell"], horizontal=True)
        
        # Number of shares
        shares = st.number_input("Number of Shares", min_value=1, max_value=10000, value=10, step=10)
        
        # Calculate trade value
        trade_value = shares * stock_info['price']
        
        st.markdown(f"""
        <p>Trade Value: <strong>${trade_value:.2f}</strong></p>
        <p>Available Cash: <strong>${st.session_state.portfolio['cash']:.2f}</strong></p>
        """, unsafe_allow_html=True)
        
        # Execute button
        if st.button(f"Execute {trade_type}"):
            if trade_type == "Buy":
                success = execute_trade(selected_ticker, shares, 'buy')
                if success:
                    st.success(f"Successfully bought {shares} shares of {selected_ticker} at ${stock_info['price']:.2f} per share")
            else:  # Sell
                success = execute_trade(selected_ticker, shares, 'sell')
                if success:
                    st.success(f"Successfully sold {shares} shares of {selected_ticker} at ${stock_info['price']:.2f} per share")
        
        # Portfolio summary
        st.markdown('<div class="category-header">Portfolio Summary</div>', unsafe_allow_html=True)
        
        # Calculate statistics
        total_value = st.session_state.portfolio['current_value']
        cash = st.session_state.portfolio['cash']
        stock_value = total_value - cash
        
        # Calculate returns
        starting_value = st.session_state.portfolio['starting_value']
        absolute_return = total_value - starting_value
        percent_return = (absolute_return / starting_value) * 100
        
        return_color = "green" if percent_return > 0 else "red" if percent_return < 0 else "gray"
        return_sign = "+" if percent_return > 0 else ""
        
        # Portfolio allocation chart
        if st.session_state.portfolio['stocks']:
            # Prepare data
            stock_values = []
            for symbol, details in st.session_state.portfolio['stocks'].items():
                stock_values.append({
                    'symbol': symbol,
                    'value': details['shares'] * st.session_state.stocks[symbol]['price']
                })
            
            # Add cash
            stock_values.append({
                'symbol': 'Cash',
                'value': cash
            })
            
            # Create pie chart
            fig = px.pie(
                [sv for sv in stock_values], 
                values='value', 
                names='symbol',
                title='Portfolio Allocation'
            )
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Just cash
            fig = px.pie(
                [{'symbol': 'Cash', 'value': cash}], 
                values='value', 
                names='symbol',
                title='Portfolio Allocation'
            )
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Display summary
        st.markdown(f"""
        <div class="highlight">
            <p><strong>Portfolio Summary</strong></p>
            <p>Total Value: ${total_value:.2f}</p>
            <p>Cash: ${cash:.2f} ({(cash/total_value*100):.1f}%)</p>
            <p>Stock Value: ${stock_value:.2f} ({(stock_value/total_value*100):.1f}%)</p>
            <p>Return: <span style="color:{return_color};">{return_sign}${absolute_return:.2f} ({return_sign}{percent_return:.2f}%)</span></p>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="sub-header">Portfolio Dashboard</div>', unsafe_allow_html=True)
    st.markdown("""
    Track your portfolio performance and transaction history. 
    See how your trading strategy based on political tweets is performing.
    """)
    
    # Portfolio overview
    dashboard_col1, dashboard_col2 = st.columns([2, 1])
    
    with dashboard_col1:
        # Portfolio performance chart
        st.markdown('<div class="category-header">Portfolio Performance</div>', unsafe_allow_html=True)
        
        # Get the portfolio history
        portfolio_df = st.session_state.portfolio_history.copy()
        
        # Append current value if it's a different day
        if datetime.now().date() != portfolio_df['Date'].iloc[-1].date():
            portfolio_df = pd.concat([
                portfolio_df,
                pd.DataFrame({'Date': [datetime.now()], 'Value': [st.session_state.portfolio['current_value']]})
            ])
        else:
            # Update last value
            portfolio_df.loc[portfolio_df.index[-1], 'Value'] = st.session_state.portfolio['current_value']
        
        # Calculate daily returns
        portfolio_df['Daily Return'] = portfolio_df['Value'].pct_change() * 100
        
        # Plot portfolio value
        fig = px.line(
            portfolio_df,
            x='Date',
            y='Value',
            title='Portfolio Value Over Time'
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Plot daily returns
        fig = px.bar(
            portfolio_df.dropna(),
            x='Date',
            y='Daily Return',
            title='Daily Portfolio Returns (%)'
        )
        
        # Color positive/negative returns
        fig.update_traces(marker_color=portfolio_df.dropna()['Daily Return'].apply(lambda x: 'green' if x > 0 else 'red'))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with dashboard_col2:
        # Portfolio statistics
        st.markdown('<div class="category-header">Portfolio Statistics</div>', unsafe_allow_html=True)
        
        # Calculate various metrics
        total_value = st.session_state.portfolio['current_value']
        starting_value = st.session_state.portfolio['starting_value']
        absolute_return = total_value - starting_value
        percent_return = (absolute_return / starting_value) * 100
        
        # Calculate additional statistics from portfolio history
        if len(portfolio_df) > 1:
            daily_returns = portfolio_df['Daily Return'].dropna()
            
            annualized_return = percent_return * (365 / len(portfolio_df))
            volatility = daily_returns.std() * (252 ** 0.5)  # Annualized
            sharpe = annualized_return / volatility if volatility > 0 else 0
            
            max_drawdown = 0
            peak = portfolio_df['Value'].iloc[0]
            
            for value in portfolio_df['Value']:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak
                max_drawdown = max(max_drawdown, drawdown)
            
            max_drawdown *= 100  # Convert to percentage
        else:
            annualized_return = 0
            volatility = 0
            sharpe = 0
            max_drawdown = 0
        
        # Format colors
        return_color = "green" if percent_return > 0 else "red" if percent_return < 0 else "gray"
        return_sign = "+" if percent_return > 0 else ""
        
        # Display metrics
        st.markdown(f"""
        <div class="highlight">
            <p><strong>Current Value:</strong> ${total_value:.2f}</p>
            <p><strong>Starting Value:</strong> ${starting_value:.2f}</p>
            <p><strong>Total Return:</strong> <span style="color:{return_color};">{return_sign}${absolute_return:.2f} ({return_sign}{percent_return:.2f}%)</span></p>
            <p><strong>Annualized Return:</strong> {annualized_return:.2f}%</p>
            <p><strong>Volatility (Annualized):</strong> {volatility:.2f}%</p>
            <p><strong>Sharpe Ratio:</strong> {sharpe:.2f}</p>
            <p><strong>Maximum Drawdown:</strong> {max_drawdown:.2f}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Holdings summary
        st.markdown('<div class="category-header">Current Holdings</div>', unsafe_allow_html=True)
        
        if st.session_state.portfolio['stocks']:
            for symbol, details in st.session_state.portfolio['stocks'].items():
                shares = details['shares']
                avg_price = details['avg_price']
                current_price = st.session_state.stocks[symbol]['price']
                current_value = shares * current_price
                
                pnl = current_value - (shares * avg_price)
                pnl_pct = (pnl / (shares * avg_price)) * 100
                
                pnl_color = "green" if pnl > 0 else "red" if pnl < 0 else "gray"
                pnl_sign = "+" if pnl > 0 else ""
                
                st.markdown(f"""
                <div style="padding: 10px; margin-bottom: 10px; border-radius: 5px; border: 1px solid #ddd;">
                    <p><strong>{symbol}</strong> - {shares} shares</p>
                    <p>Current: ${current_price:.2f} | Avg: ${avg_price:.2f}</p>
                    <p>Value: ${current_value:.2f}</p>
                    <p>P&L: <span style="color:{pnl_color};">{pnl_sign}${pnl:.2f} ({pnl_sign}{pnl_pct:.2f}%)</span></p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No stocks currently in portfolio")
        
        st.markdown(f"**Cash Balance:** ${st.session_state.portfolio['cash']:.2f}")
    
    # Transaction history
    st.markdown('<div class="category-header">Transaction History</div>', unsafe_allow_html=True)
    
    if st.session_state.portfolio['transactions']:
        # Create dataframe from transactions
        transactions = st.session_state.portfolio['transactions']
        
        # Create table
        trans_df = pd.DataFrame([
            {
                'Date': t['timestamp'].strftime('%Y-%m-%d %H:%M'),
                'Action': t['action'].title(),
                'Symbol': t['symbol'],
                'Shares': t['shares'],
                'Price': f"${t['price']:.2f}",
                'Value': f"${t['value']:.2f}"
            } for t in transactions
        ])
        
        st.dataframe(trans_df, hide_index=True, use_container_width=True)
    else:
        st.info("No transactions yet")

# Add a reset button at the bottom
if st.button("Reset Portfolio"):
    st.session_state.portfolio = {
        'cash': 100000.0,
        'stocks': {},
        'history': [],
        'current_value': 100000.0,
        'starting_value': 100000.0,
        'transactions': []
    }
    
    # Reset portfolio history but keep the dates
    dates = st.session_state.portfolio_history['Date']
    st.session_state.portfolio_history = pd.DataFrame({
        'Date': dates,
        'Value': [100000.0] * len(dates)
    })
    
    st.success("Portfolio has been reset to starting value of $100,000")
    
    time.sleep(1)
    st.rerun()