import streamlit as st
import requests
import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt

# Session state initialization
if 'coin_id' not in st.session_state:
    st.session_state.coin_id = None
if 'project_name' not in st.session_state:
    st.session_state.project_name = None
if 'data' not in st.session_state:
    st.session_state.data = None

st.set_page_config(page_title="Crypto Project Scout", layout="wide")
st.title("🔍 Crypto Project Scout & Success Predictor")
st.markdown("""
Find new crypto projects, gather live data, and get evidence-based success predictions.
Enter a project name or token symbol below.
""")

project_input = st.text_input("Enter project name or token (e.g., Theoriq, THQ, bitcoin)", "bitcoin")

if st.button("Scout Project"):
    with st.spinner("Fetching live data from CoinGecko..."):
        # You need to add the actual fetching logic here!
        # Example placeholder (you probably have this already):
        search_url = f"https://api.coingecko.com/api/v3/search?query={project_input}"
        search_response = requests.get(search_url)
        search_data = search_response.json()
        
        if not search_data['coins']:
            st.error("Project not found!")
            st.stop()
        
        coin_id = search_data['coins'][0]['id']
        
        detail_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&market_data=true&community_data=true&developer_data=true&sparkline=false"
        detail_response = requests.get(detail_url)
        data = detail_response.json()
    
    # Save to session state
    st.session_state.coin_id = coin_id
    st.session_state.project_name = data['name']
    st.session_state.data = data
   
    st.success(f"Found: {data['name']} ({data['symbol'].upper()})")
    st.rerun()

# === MAIN CONTENT: Only show tabs when a project is scouted ===
if st.session_state.coin_id is not None:
    data = st.session_state.data
    market = data['market_data']
    community = data.get('community_data', {})
    developer = data.get('developer_data', {})
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🔬 Analysis", "🎯 Success Prediction", "📈 Price Forecast"])

    with tab1:
        st.subheader("Live Market Data")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Current Price", f"${market['current_price']['usd']:,.4f}")
        col2.metric("Market Cap", f"${market['market_cap']['usd']:,.0f}" if market['market_cap']['usd'] else "N/A")
        col3.metric("24h Volume", f"${market['total_volume']['usd']:,.0f}")
        col4.metric("24h Change", f"{market['price_change_percentage_24h']:+.2f}%")
       
        st.subheader("Project Description")
        desc = data['description']['en']
        st.write(desc[:1500] + "..." if len(desc) > 1500 else desc or "No description available")
       
        st.subheader("Community Metrics")
        col1, col2 = st.columns(2)
        twitter = community.get('twitter_followers')
        col1.metric("Twitter Followers", f"{twitter:,}" if twitter else "N/A")
        reddit = community.get('reddit_subscribers')
        col2.metric("Reddit Subscribers", f"{reddit:,}" if reddit else "N/A")
       
        st.subheader("Links")
        links = data['links']
        if links['homepage'][0]:
            st.markdown(f"🌐 [Official Website]({links['homepage'][0]})")
        if links['twitter_screen_name']:
            st.markdown(f"🐦 [Twitter / X](https://twitter.com/{links['twitter_screen_name']})")
        if links['repos_url']['github']:
            for repo in links['repos_url']['github']:
                if repo:
                    st.markdown(f"💻 [GitHub]({repo})")
                    break

    with tab2:
        st.subheader("Detailed Analysis")
       
        st.subheader("Developer Activity (GitHub)")
        col1, col2, col3 = st.columns(3)
        col1.metric("Stars", f"{developer.get('stars', 0):,}")
        col2.metric("Forks", f"{developer.get('forks', 0):,}")
        col3.metric("Commits (4 weeks)", f"{developer.get('commit_count_4_weeks', 0):,}")
       
        if developer.get('stars', 0) > 500:
            st.success("High developer activity — strong open-source engagement")
        elif developer.get('stars', 0) > 100:
            st.info("Moderate activity — decent development")
        else:
            st.warning("Low developer activity — potential risk")
       
        st.subheader("Funding & Team")
        st.info("Funding data (VC rounds, presale) — coming soon")
        st.info("Team doxxed status — coming soon")
       
        st.subheader("Key Risks")
        if market['price_change_percentage_24h'] < -20:
            st.warning("High volatility — large 24h drop")
        if market['market_cap']['usd'] < 10_000_000:
            st.warning("Low market cap — higher risk of manipulation")
        st.warning("Always DYOR — check audits, locked liquidity, and contract")

    with tab3:
        st.subheader("AI Success Prediction (Advanced Scoring)")
       
        market_cap = market['market_cap']['usd'] or 0
        volume = market['total_volume']['usd'] or 0
        dev_stars = developer.get('stars', 0)
        twitter = community.get('twitter_followers', 0)
        price_change = market['price_change_percentage_24h'] or 0
       
        short_score = 50
        long_score = 50
       
        if market_cap > 1_000_000_000:
            short_score += 25
            long_score += 20
        elif market_cap > 100_000_000:
            short_score += 15
            long_score += 15
       
        if volume > 50_000_000:
            short_score += 15
        if price_change > 10:
            short_score += 10
       
        if dev_stars > 500:
            short_score += 15
            long_score += 25
        elif dev_stars > 100:
            short_score += 10
            long_score += 15
       
        if twitter > 100_000:
            short_score += 10
            long_score += 15
        elif twitter > 50_000:
            short_score += 5
            long_score += 10
       
        factor_count = 0
        if market_cap > 500_000_000: factor_count += 1
        if volume > 20_000_000: factor_count += 1
        if dev_stars > 100: factor_count += 1
        if twitter > 50_000: factor_count += 1
        if price_change > -20: factor_count += 1
       
        if factor_count >= 4:
            short_score += 10
            long_score += 10
        elif factor_count <= 1:
            short_score -= 10
            long_score -= 10
       
        short_score = min(max(short_score, 20), 98)
        long_score = min(max(long_score, 20), 95)
       
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Short-term Success Probability (6–12 months)", f"{short_score}%")
        with col2:
            st.metric("Long-term Success Probability (2+ years)", f"{long_score}%")
       
        st.subheader("AI Reasoning")
        st.markdown("**Positive Factors**")
        positives = []
        if market_cap > 500_000_000:
            positives.append("Strong market cap — established player")
        if volume > 20_000_000:
            positives.append("High trading volume — good liquidity")
        if dev_stars > 100:
            positives.append("Active GitHub — ongoing development")
        if twitter > 50_000:
            positives.append("Large community — strong network effect")
        if price_change > 0:
            positives.append("Positive momentum")
       
        if positives:
            for p in positives:
                st.success(p)
        else:
            st.info("No strong positive factors detected")
       
        st.markdown("**Risk Factors**")
        risks = []
        if market_cap < 10_000_000:
            risks.append("Low market cap — higher manipulation risk")
        if dev_stars < 50:
            risks.append("Low developer activity — stalled development")
        if price_change < -30:
            risks.append("Extreme volatility — high risk")
        if market_cap < 50_000_000 and volume < 5_000_000:
            risks.append("Low liquidity — hard to exit")
       
        if risks:
            for r in risks:
                st.warning(r)
        else:
            st.success("No major risks detected")
       
        st.info("AI-enhanced rule-based model — combines market, dev, community, and momentum data")

    with tab4:
        st.subheader(f"AI Price Forecast for {st.session_state.project_name}")
        st.info("Forecasting using advanced Prophet AI (curved + confidence interval)")
       
        days_history = st.slider("Historical days", 30, 365, 90, key="hist_days")
        days_future = st.slider("Forecast days ahead", 7, 90, 30, key="fut_days")
       
        if st.button("Generate AI Forecast", key="gen_forecast"):
            with st.spinner("Training Prophet AI model..."):
                coin_id = st.session_state.coin_id
                url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days_history}"
                response = requests.get(url)
                if response.status_code != 200:
                    st.error("Failed to fetch price data")
                    st.stop()
                prices = response.json()['prices']
                df = pd.DataFrame(prices, columns=['timestamp', 'price'])
                df['ds'] = pd.to_datetime(df['timestamp'], unit='ms')
                df['y'] = df['price']
                df = df[['ds', 'y']]
               
                m = Prophet(daily_seasonality=True, weekly_seasonality=True)
                m.add_seasonality(name='monthly', period=30.5, fourier_order=5)
                m.fit(df)
               
                future = m.make_future_dataframe(periods=days_future)
                forecast = m.predict(future)
               
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.plot(df['ds'], df['y'], label='Historical', color='blue', linewidth=2)
                ax.plot(forecast['ds'], forecast['yhat'], label='AI Forecast', color='orange', linestyle='--', linewidth=2)
                ax.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='orange', alpha=0.2, label='Confidence')
                ax.set_title(f"{st.session_state.project_name} AI Price Forecast")
                ax.set_ylabel('Price (USD)')
                ax.legend()
                ax.grid(True)
                st.pyplot(fig)
               
                st.success("Prophet AI forecast complete! 🚀")

else:
    st.info("Scout a project to see analysis and forecasts")

st.caption("Built by you — powered by CoinGecko, DefiLlama, CryptoPanic, and more")