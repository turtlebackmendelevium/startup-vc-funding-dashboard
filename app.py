# --- IMPORTS ---
import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
from sklearn.linear_model import LinearRegression
import numpy as np
from streamlit_extras.metric_cards import style_metric_cards
import streamlit.components.v1 as components

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="VC Investment Trends Explorer",
    layout="wide",
    initial_sidebar_state="expanded",
)
alt.themes.enable("dark")

# --- LOAD DATA ---
funding = pd.read_csv("startup_data/funding_rounds.csv")
objects = pd.read_csv("https://drive.google.com/uc?export=download&id=1Xi8VnD1rIE14BZcdFi6LkqBtkBXvI7oF")
# --- MERGE & CLEAN ---
merged = funding_rounds.merge(
    objects[['id', 'name', 'category_code', 'country_code']],
    left_on='object_id', right_on='id', how='left'
)
merged.rename(columns={
    'name': 'company_name',
    'category_code': 'industry',
    'country_code': 'country'
}, inplace=True)
merged = merged.dropna(subset=['industry', 'country', 'raised_amount_usd', 'funded_at'])
merged['raised_amount_usd'] = merged['raised_amount_usd'].astype(float)
merged['funded_at'] = pd.to_datetime(merged['funded_at'], errors='coerce')
merged = merged.dropna(subset=['funded_at'])
merged['year'] = merged['funded_at'].dt.year
merged = merged[merged['raised_amount_usd'] > 0]

# --- SIDEBAR FILTERS ---
st.sidebar.title("🎯 Filter Data")
year_range = st.sidebar.slider(
    "Select Year Range", int(merged['year'].min()), int(merged['year'].max()), (2005, 2015)
)
selected_industries = st.sidebar.multiselect(
    "Select Industries", merged['industry'].unique(), default=['software', 'biotech']
)
selected_countries = st.sidebar.multiselect(
    "Select Countries", merged['country'].unique(), default=['USA', 'GBR', 'CAN']
)
color_theme = st.sidebar.selectbox(
    "Select a Color Theme", ['Blues', 'Viridis', 'Plasma', 'Inferno', 'Cividis']
)

# --- APPLY FILTERS ---
filtered = merged[
    (merged['year'].between(*year_range)) &
    (merged['industry'].isin(selected_industries)) &
    (merged['country'].isin(selected_countries))
]

# --- TOP METRICS ---
st.title("🚀 VC Investment Trends Explorer")
st.markdown("Explore trends in startup funding by year, industry, and country.")

total_funding = filtered['raised_amount_usd'].sum()
total_rounds = filtered.shape[0]
top_industry = filtered['industry'].value_counts().idxmax()

col1, col2, col3 = st.columns(3)
col1.metric("Total VC Raised", f"${total_funding / 1e9:.2f}B")
col2.metric("Total Rounds", f"{total_rounds:,}")
col3.metric("Top Industry", top_industry.title())

style_metric_cards(border_color="#000000", background_color="rgba(0, 0, 0, 0)")

# --- 🌎 VC FUNDING BY COUNTRY ---
st.subheader("🌍 VC Funding by Country")

map_data = filtered.groupby('country')['raised_amount_usd'].sum().reset_index()

fig_map = px.choropleth(
    map_data,
    locations="country",
    locationmode="ISO-3",
    color="raised_amount_usd",
    color_continuous_scale=color_theme.lower(),
    hover_name="country",
    labels={"raised_amount_usd": "Total Funding (USD)"},
    title=""
)

fig_map.update_layout(
    template="plotly_dark",
    geo=dict(
        showframe=False,
        showcoastlines=True,
        coastlinecolor="gray",
        bgcolor="#0e0e0e",
        landcolor="black",
        projection_type="equirectangular",
    ),
    coloraxis_colorbar=dict(title="Funding (USD)"),
    margin=dict(l=0, r=0, t=30, b=0)
)
st.plotly_chart(fig_map, use_container_width=True)

# --- COUNTRY BREAKDOWN ---
st.subheader("🏳️ Country-Specific Funding Breakdown")
selected_country = st.selectbox("Select a country to drill down:", map_data['country'].unique())

country_data = filtered[filtered['country'] == selected_country]

col1, col2, col3 = st.columns(3)
col1.metric("Total Raised", f"${country_data['raised_amount_usd'].sum() / 1e9:.2f}B")
col2.metric("Total Rounds", f"{country_data.shape[0]:,}")
col3.metric("Top Industry", country_data['industry'].value_counts().idxmax().title())

import streamlit.components.v1 as components

# --- 🏢 Top Funded Companies with Industry (Final Version) ---
st.subheader(f"🏢 Top Funded Companies in {selected_country}")

top_companies = (
    country_data.groupby(['company_name', 'industry'])['raised_amount_usd']
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

# Build the polished HTML
table_html = """
<style>
.table-card {
  background-color: #111;
  border-radius: 16px;
  padding: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.6);
  margin-top: 20px;
  overflow: hidden;
  animation: fadeIn 0.5s ease-in;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.table-card table {
  width: 100%;
  border-collapse: collapse;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 16px;
}
.table-card thead {
  background-color: #1a1a1a;
  color: #FFD700;
}
.table-card th, .table-card td {
  padding: 14px 16px;
  border-bottom: 1px solid #333;
}
.table-card th {
  text-align: left;
}
.table-card td {
  text-align: left;
  color: white;
}
.table-card td.rank-cell {
  text-align: center;
  font-size: 18px;
}
.table-card tr:hover {
  background-color: #222;
  box-shadow: inset 0 0 10px rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  transform: scale(1.01);
}
.table-card td:first-child {
  white-space: nowrap;
}
.highlight {
  font-weight: bold;
  letter-spacing: 0.5px;
}
.gold { color: #FFD700; }
.silver { color: #C0C0C0; }
.bronze { color: #CD7F32; }
</style>

<div class="table-card">
<table>
  <thead>
    <tr>
      <th style="text-align: center;">🏆 Rank</th>
      <th>🏢 Company Name</th>
      <th>💵 Funding (Billion USD)</th>
      <th>🏭 Industry</th>
    </tr>
  </thead>
  <tbody>
"""

colors = ['gold', 'silver', 'bronze']
default_color = ''

for idx, row in top_companies.iterrows():
    color_class = colors[idx] if idx < 3 else default_color
    highlight = 'highlight' if idx < 3 else ''
    
    company = row['company_name']
    funding = f"${row['raised_amount_usd']/1e9:.2f}B"
    industry = row['industry'].title() if pd.notnull(row['industry']) else "N/A"
    rank = idx + 1
    
    table_html += f"""
    <tr class="{highlight}">
      <td class="rank-cell {color_class}">🏆 {rank}</td>
      <td class="{color_class if idx<3 else ''}">🏢 {company}</td>
      <td class="{color_class if idx<3 else ''}">{funding}</td>
      <td class="{color_class if idx<3 else ''}">🏭 {industry}</td>
    </tr>
    """

table_html += """
  </tbody>
</table>
</div>
"""

components.html(table_html, height=700, scrolling=True)

# --- 📈 VC FUNDING TREND BY INDUSTRY ---
st.subheader("📈 VC Funding Trends by Industry")
trend_data = (
    filtered.groupby(['year', 'industry'])['raised_amount_usd']
    .sum()
    .reset_index()
)

fig_trend = px.line(
    trend_data,
    x='year',
    y='raised_amount_usd',
    color='industry',
    labels={'raised_amount_usd': 'Funding (USD)', 'year': 'Year'},
    color_discrete_sequence=px.colors.qualitative.Set1
)
fig_trend.update_layout(
    yaxis_tickprefix="$",
    yaxis_tickformat=".2s",
    margin=dict(l=0, r=0, t=30, b=0),
)
st.plotly_chart(fig_trend, use_container_width=True)

# --- 🤖 PREDICTED FUNDING NEXT YEAR ---
st.subheader("🤖 Predicted VC Funding Next Year")
pred_data = (
    filtered.groupby('year')['raised_amount_usd']
    .sum()
    .reset_index()
)

X = pred_data[['year']]
y = pred_data['raised_amount_usd']

model = LinearRegression()
model.fit(X, y)
next_year = np.array([[pred_data['year'].max() + 1]])
predicted_funding = model.predict(next_year)[0]

st.success(f"Predicted VC funding for {int(next_year[0][0])}: ${predicted_funding / 1e9:.2f}B")

# --- 🔥 HEATMAP FUNDING INTENSITY ---
st.subheader("🔥 Heatmap of VC Funding Activity")
heatmap_data = filtered.groupby(['year', 'industry'])['raised_amount_usd'].sum().reset_index()

fig_heatmap = px.density_heatmap(
    heatmap_data,
    x='industry',
    y='year',
    z='raised_amount_usd',
    color_continuous_scale=color_theme.lower(),
    labels={'raised_amount_usd': 'Total Funding'},
)

fig_heatmap.update_layout(margin=dict(l=0, r=0, t=30, b=0))
st.plotly_chart(fig_heatmap, use_container_width=True)

# --- ℹ️ ABOUT ---
with st.expander("ℹ️ About this Dashboard"):
    st.markdown('''
    - Built with [Streamlit](https://streamlit.io/)
    - Dataset: Crunchbase Public Startup Funding Data
    - Visualizing VC trends across year, industry, and country
    - Bonus: Machine learning prediction for next-year VC funding
    ''')
