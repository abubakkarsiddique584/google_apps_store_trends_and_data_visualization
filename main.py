import pandas as pd
import plotly.express as px

# Load the data
df = pd.read_csv('googleplaystore.csv')

# Drop unnecessary columns
df.drop(columns=['Last Updated', 'Android Ver'], inplace=True)

# Drop rows with missing values and duplicates
clean_df = df.dropna().drop_duplicates()

# Filter out 'Varies with device' entries in Size
clean_df = clean_df[clean_df['Size'] != 'Varies with device']

# Convert Size to numeric (in MB)
def convert_size(size_str):
    size_str = size_str.strip().upper()
    if 'M' in size_str:
        return float(size_str.replace('M', ''))
    elif 'K' in size_str:
        return float(size_str.replace('K', '')) / 1024  # KB to MB
    else:
        return None

clean_df['Size_MB'] = clean_df['Size'].apply(convert_size)
clean_df = clean_df.dropna(subset=['Size_MB'])

# Convert Installs to numeric
clean_df['Installs'] = clean_df['Installs'].str.replace('+', '', regex=False).str.replace(',', '', regex=False)
clean_df['Installs'] = pd.to_numeric(clean_df['Installs'])

# Check apps with extreme install counts
print("Apps with 1+ Billion Installs:", len(clean_df[clean_df['Installs'] >= 1_000_000_000]))
print("Apps with only 1 Install:", len(clean_df[clean_df['Installs'] == 1]))

# Convert Price to numeric
clean_df['Price'] = clean_df['Price'].str.replace('$', '', regex=False)
clean_df['Price'] = pd.to_numeric(clean_df['Price'])

# Top 5 highest rated apps
highest_rated_apps = clean_df.sort_values(by='Rating', ascending=False)
print("\nTop Highest Rated Apps:")
print(highest_rated_apps[['App', 'Category', 'Rating', 'Reviews', 'Size_MB', 'Installs', 'Price']].head())

# Top 5 largest apps by size
top_5_highest_size_apps = clean_df.sort_values(by='Size_MB', ascending=False)
print("\nTop 5 Largest Apps by Size:")
print(top_5_highest_size_apps[['App', 'Category', 'Rating', 'Size_MB', 'Installs']].head())

# Top 5 most reviewed apps
top_5_most_reviews = clean_df.sort_values(by='Reviews', ascending=False)
print("\nTop 5 Apps with Most Reviews:")
print(top_5_most_reviews[['App', 'Category', 'Rating', 'Reviews', 'Installs', 'Price']].head())

# Find most expensive apps
most_expensive = clean_df.sort_values(by='Price', ascending=False)
print("\nTop 20 Most Expensive Apps:")
print(most_expensive[['App', 'Category', 'Price', 'Installs']].head(20))

# Remove apps with Price > $250
clean_df = clean_df[clean_df['Price'] <= 250]

# Estimate Revenue (Paid apps only)
clean_df['Revenue_Estimate'] = clean_df['Price'] * clean_df['Installs']
top_revenue_apps = clean_df[clean_df['Type'] == 'Paid'].sort_values(by='Revenue_Estimate', ascending=False)
print("\nTop 10 Highest Grossing Paid Apps:")
print(top_revenue_apps[['App', 'Category', 'Price', 'Installs', 'Revenue_Estimate']].head(10))

# Count how many of top 10 are games
games_count = top_revenue_apps.head(10)['Category'].str.contains('GAME').sum()
print(f"\nNumber of games among top 10 highest grossing apps: {games_count}")

# ---------------------------
# Plotly Pie Chart: Content Ratings
# ---------------------------
content_rating_counts = clean_df['Content Rating'].value_counts().reset_index()
content_rating_counts.columns = ['Content Rating', 'Count']

fig_pie = px.pie(content_rating_counts, values='Count', names='Content Rating',
                 title='Distribution of Content Ratings', hole=0)
fig_pie.show()

# Donut Chart version
fig_donut = px.pie(content_rating_counts, values='Count', names='Content Rating',
                   title='Content Rating Distribution (Donut Chart)', hole=0.4)
fig_donut.show()

# ---------------------------
# Plotly Bar: Apps per Category
# ---------------------------
category_counts = clean_df['Category'].value_counts().reset_index()
category_counts.columns = ['Category', 'Number of Apps']

fig_bar = px.bar(category_counts, x='Category', y='Number of Apps',
                 title='Number of Apps per Category', template='plotly', color='Number of Apps')
fig_bar.update_layout(xaxis={'categoryorder':'total descending'})
fig_bar.show()

# ---------------------------
# Plotly Scatter: Rating vs Reviews by Category
# ---------------------------
fig_scatter = px.scatter(clean_df, x='Rating', y='Reviews',
                         color='Category', size='Installs',
                         hover_name='App', title='Rating vs. Reviews by Category',
                         template='plotly', size_max=60)
fig_scatter.update_traces(marker=dict(opacity=0.6))
fig_scatter.show()

# ---------------------------
# Plotly Bar: Average Rating by Category
# ---------------------------
avg_rating = clean_df.groupby('Category')['Rating'].mean().reset_index().sort_values(by='Rating', ascending=False)

fig_avg_rating = px.bar(avg_rating, x='Category', y='Rating',
                        title='Average App Rating by Category',
                        template='plotly_dark', color='Rating', color_continuous_scale='Tealgrn')
fig_avg_rating.update_layout(xaxis={'categoryorder': 'total descending'})
fig_avg_rating.show()
# ---------------------------
# Vertical Bar Chart: Highest Competition (Number of Apps per Category)
# ---------------------------
fig_vertical_bar = px.bar(
    category_counts.sort_values(by='Number of Apps', ascending=False),
    x='Category',
    y='Number of Apps',
    title='Vertical Bar Chart - Highest Competition by Category',
    template='plotly_white',
    color='Number of Apps',
    color_continuous_scale='Viridis'
)

fig_vertical_bar.update_layout(
    xaxis_title='App Category',
    yaxis_title='Number of Apps',
    xaxis_tickangle=45
)

fig_vertical_bar.show()
# Horizontal Bar Chart - Most Popular Categories (Highest Downloads)
# ---------------------------
# Calculate total installs per category
category_installs = clean_df.groupby('Category')['Installs'].sum().reset_index()
category_installs = category_installs.sort_values(by='Installs', ascending=True)  # ascending for horizontal

fig_horizontal_bar = px.bar(
    category_installs,
    x='Installs',
    y='Category',
    orientation='h',
    title='Horizontal Bar Chart - Most Popular Categories by Total Downloads',
    template='plotly_dark',
    color='Installs',
    color_continuous_scale='Aggrnyl'
)
fig_horizontal_bar.update_layout(
    xaxis_title='Total Downloads',
    yaxis_title='App Category'
)
fig_horizontal_bar.show()
# ---------------------------------------------
# Category Concentration: Downloads vs Competition (with log scale)
# ---------------------------------------------

# Create DataFrame with number of apps and installs per category
category_concentration = clean_df.groupby('Category').agg({
    'App': 'count',
    'Installs': 'sum'
}).reset_index()
category_concentration.columns = ['Category', 'Number of Apps', 'Total Installs']

# Plotly scatter plot
fig_concentration = px.scatter(
    category_concentration,
    x='Number of Apps',
    y='Total Installs',
    size='Total Installs',
    color='Category',
    hover_name='Category',
    title='Category Concentration: Downloads vs Competition',
    template='plotly_white',
    size_max=60
)

# Apply log scale to Y-axis
fig_concentration.update_layout(
    yaxis=dict(type='log'),
    xaxis_title='Number of Apps (Competition)',
    yaxis_title='Total Installs (Popularity - Log Scale)'
)

# Optional: slightly transparent bubbles
fig_concentration.update_traces(marker=dict(opacity=0.7))

# Show plot
fig_concentration.show()
# ---------------------------------------------
# Analyzing the 'Genres' Column
# ---------------------------------------------

# Step 1: Check unique genre strings and value counts
print("\nTop Genre Combinations (raw):")
print(clean_df['Genres'].value_counts().head(10))

# Step 2: Split genres on ';' if they are nested (e.g., 'Art & Design;Creativity')
genre_split = clean_df['Genres'].str.split(';')

# Step 3: Use .stack() to flatten the nested lists into one Series
all_genres = genre_split.apply(pd.Series).stack().reset_index(drop=True)

# Step 4: Count unique genres
unique_genres = all_genres.nunique()
print(f"\nTotal Unique Genres: {unique_genres}")

# Step 5: Show top 10 most common individual genres
print("\nTop 10 Most Common Individual Genres:")
print(all_genres.value_counts().head(10))

# Step 6: Check if any app has more than one genre
multi_genre_apps = clean_df[clean_df['Genres'].str.contains(';', na=False)]
print(f"\nNumber of apps with multiple genres: {len(multi_genre_apps)}")
# ---------------------------------------------
# Plotly Bar Chart: Competition in Genres with Color Scales
# ---------------------------------------------

# Step 1: Get genre counts
genre_counts = all_genres.value_counts().reset_index()
genre_counts.columns = ['Genre', 'Number of Apps']

# Step 2: Create color-scaled bar chart
fig_genre_comp = px.bar(
    genre_counts,
    x='Genre',
    y='Number of Apps',
    title='Competition in Genres (Number of Apps)',
    template='plotly',
    color='Number of Apps',
    color_continuous_scale='Turbo'  # You can try: 'Viridis', 'Blues', 'Magma', etc.
)

# Step 3: Customize layout
fig_genre_comp.update_layout(
    xaxis_title='Genre',
    yaxis_title='Number of Apps',
    xaxis_tickangle=45
)

fig_genre_comp.show()
# ---------------------------------------------
# Grouped Bar Chart: Free vs. Paid Apps per Category
# ---------------------------------------------

# Step 1: Group and count Free vs Paid apps per Category
category_type_counts = clean_df.groupby(['Category', 'Type'])['App'].count().reset_index()
category_type_counts.columns = ['Category', 'Type', 'Number of Apps']

# Step 2: Plot using Plotly Express
fig_grouped_bar = px.bar(
    category_type_counts,
    x='Category',
    y='Number of Apps',
    color='Type',
    barmode='group',
    title='Free vs Paid Apps per Category',
    template='plotly_dark',
    color_discrete_map={'Free': 'skyblue', 'Paid': 'salmon'}
)

# Step 3: Improve layout
fig_grouped_bar.update_layout(
    xaxis_title='App Category',
    yaxis_title='Number of Apps',
    xaxis_tickangle=45
)

fig_grouped_bar.show()



# ---------------------------------------------
# Box Plot: Installs for Free vs Paid Apps
# ---------------------------------------------

# Filter only Free and Paid apps with valid installs
install_comparison = clean_df[clean_df['Type'].isin(['Free', 'Paid'])]

# Plotly Box Plot
fig_box = px.box(
    install_comparison,
    x='Type',
    y='Installs',
    color='Type',
    title='Box Plot - Lost Downloads for Paid Apps',
    template='plotly_white',
    color_discrete_map={'Free': 'green', 'Paid': 'orange'},
    points='all'  # shows all points (optional)
)

# Use log scale for y-axis to manage skew from extreme values
fig_box.update_layout(
    yaxis=dict(type='log'),
    xaxis_title='App Type',
    yaxis_title='Number of Installs (Log Scale)'
)

fig_box.show()
# ---------------------------------------------
# Box Plot: Revenue by App Category (Paid Apps Only)
# ---------------------------------------------

# Step 1: Filter for Paid apps with Revenue_Estimate > 0
paid_revenue = clean_df[(clean_df['Type'] == 'Paid') & (clean_df['Revenue_Estimate'] > 0)]

# Optional: Only include categories with enough data (e.g., at least 5 paid apps)
category_counts = paid_revenue['Category'].value_counts()
valid_categories = category_counts[category_counts >= 5].index
paid_revenue = paid_revenue[paid_revenue['Category'].isin(valid_categories)]

# Step 2: Create the box plot
fig_revenue_box = px.box(
    paid_revenue,
    x='Category',
    y='Revenue_Estimate',
    title='Box Plot - Estimated Revenue by App Category (Paid Apps Only)',
    color='Category',
    template='plotly_white',
    points='all'  # Show individual data points
)

# Step 3: Use log scale to manage wide revenue range
fig_revenue_box.update_layout(
    yaxis=dict(type='log'),
    xaxis_title='App Category',
    yaxis_title='Estimated Revenue (Log Scale)',
    xaxis_tickangle=45,
    showlegend=False
)

# Show the plot
fig_revenue_box.show()

# ---------------------------------------------
# Paid App Pricing Strategies by Category
# ---------------------------------------------

# Step 1: Filter only Paid apps
paid_apps = clean_df[clean_df['Type'] == 'Paid']

# Step 2: Find median price of paid apps
median_price = paid_apps['Price'].median()
print(f"💰 Median Price of Paid Apps: ${median_price:.2f}")

# Optional: filter out extreme pricing (e.g., under $100) for better visualization
paid_apps_filtered = paid_apps[paid_apps['Price'] <= 100]

# Step 3: Box plot - Price by Category
fig_price_box = px.box(
    paid_apps_filtered,
    x='Category',
    y='Price',
    color='Category',
    title='Box Plot - Paid App Prices by Category',
    template='plotly_white',
    points='all'
)

# Step 4: Sort categories by median price descending
fig_price_box.update_layout(
    xaxis_title='App Category',
    yaxis_title='Price ($)',
    xaxis_tickangle=45,
    xaxis={'categoryorder':'max descending'},
    showlegend=False
)

fig_price_box.show()

