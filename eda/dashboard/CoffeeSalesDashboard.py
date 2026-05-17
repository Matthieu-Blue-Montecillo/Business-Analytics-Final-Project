import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# ── Data ──────────────────────────────────────────────────────────────────────
df = pd.read_csv('Project.csv')

MONTH_ORDER = ['January', 'February', 'March', 'April', 'May', 'June']
MONTH_MAP   = {1:'January', 2:'February', 3:'March', 4:'April', 5:'May', 6:'June'}
df['Month Name'] = df['Month'].map(MONTH_MAP)

STORES     = ['All Stores', 'Astoria', "Hell's Kitchen", 'Lower Manhattan']
CATEGORIES = df['product_category'].unique().tolist()

STORE_COLORS = {
    'Astoria':         '#2e75b6',
    "Hell's Kitchen":  '#c0392b',
    'Lower Manhattan': '#27ae60',
}

CAT_COLORS = {
    'Coffee':              '#2e75b6',
    'Tea':                 '#27ae60',
    'Bakery':              '#8e44ad',
    'Drinking Chocolate':  '#c0392b',
    'Coffee beans':        '#e67e22',
    'Flavours':            '#f1c40f',
    'Loose Tea':           '#16a085',
    'Branded':             '#7f8c8d',
    'Packaged Chocolate':  '#6d4c41',
}

# ── KPI base numbers ──────────────────────────────────────────────────────────
TOTAL_REV   = df['Total_Bill'].sum()
TOTAL_TXN   = len(df)
AVG_TXN     = df['Total_Bill'].mean()
TOP_STORE   = df.groupby('store_location')['Total_Bill'].sum().idxmax()

# ── App ───────────────────────────────────────────────────────────────────────
app = Dash(__name__)
app.title = 'Coffee Shop Sales Dashboard'

# ── Styles ────────────────────────────────────────────────────────────────────
FONT        = 'Georgia, serif'
BG          = '#f5f0eb'
CARD_BG     = '#ffffff'
HEADER_BG   = '#1a1a2e'
ACCENT      = '#c0392b'
TEXT_DARK   = '#1a1a2e'
TEXT_LIGHT  = '#ffffff'
BORDER      = '#ddd5c8'

card_style = {
    'backgroundColor': CARD_BG,
    'borderRadius':    '8px',
    'padding':         '20px',
    'boxShadow':       '0 2px 8px rgba(0,0,0,0.08)',
    'border':          f'1px solid {BORDER}',
}

kpi_style = {
    **card_style,
    'textAlign':  'center',
    'flex':       '1',
    'margin':     '0 8px',
}

# ── Layout ────────────────────────────────────────────────────────────────────
app.layout = html.Div(style={'backgroundColor': BG, 'fontFamily': FONT, 'minHeight': '100vh'}, children=[

    # Header
    html.Div(style={
        'backgroundColor': HEADER_BG,
        'padding':         '28px 40px 20px 40px',
        'borderBottom':    f'4px solid {ACCENT}',
    }, children=[
        html.H1('Coffee Shop Chain Sales Analysis',
                style={'color': TEXT_LIGHT, 'margin': '0 0 6px 0',
                       'fontSize': '28px', 'letterSpacing': '0.5px'}),
        html.P('January to June 2023  |  149,116 Transactions  |  3 NYC Locations: Astoria, Hell\'s Kitchen, Lower Manhattan',
               style={'color': '#aaa', 'margin': '0 0 18px 0', 'fontSize': '13px'}),

        # Store filter
        html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '12px'}, children=[
            html.Label('Filter by Store:', style={'color': TEXT_LIGHT, 'fontSize': '13px', 'whiteSpace': 'nowrap'}),
            dcc.Dropdown(
                id='store-filter',
                options=[{'label': s, 'value': s} for s in STORES],
                value='All Stores',
                clearable=False,
                style={'width': '220px', 'fontSize': '13px'},
            ),
        ]),
    ]),

    # KPI Row
    html.Div(style={'display': 'flex', 'padding': '24px 40px 8px 40px', 'gap': '0'}, children=[
        html.Div(id='kpi-revenue', style=kpi_style),
        html.Div(id='kpi-transactions', style=kpi_style),
        html.Div(id='kpi-avg', style=kpi_style),
        html.Div(id='kpi-top-store', style=kpi_style),
    ]),

    # Row 1: Monthly Trend + Category Heatmap
    html.Div(style={'display': 'flex', 'padding': '16px 40px', 'gap': '16px'}, children=[
        html.Div(style={**card_style, 'flex': '1.4'}, children=[
            html.H3('Monthly Revenue Trend', style={'margin': '0 0 4px 0', 'fontSize': '15px', 'color': TEXT_DARK}),
            html.P('Q2: How did revenue change from January to June?',
                   style={'margin': '0 0 12px 0', 'fontSize': '11px', 'color': '#888'}),
            dcc.Graph(id='monthly-trend', config={'displayModeBar': False}),
        ]),
        html.Div(style={**card_style, 'flex': '1'}, children=[
            html.H3('Revenue by Category and Store', style={'margin': '0 0 4px 0', 'fontSize': '15px', 'color': TEXT_DARK}),
            html.P('Q3: Do the three stores sell to the same type of customer?',
                   style={'margin': '0 0 12px 0', 'fontSize': '11px', 'color': '#888'}),
            dcc.Graph(id='category-heatmap', config={'displayModeBar': False}),
        ]),
    ]),

    # Row 2: Hour x Store Heatmap + Top 10 Products
    html.Div(style={'display': 'flex', 'padding': '0 40px 16px 40px', 'gap': '16px'}, children=[
        html.Div(style={**card_style, 'flex': '1.2'}, children=[
            html.H3('Revenue by Hour and Store', style={'margin': '0 0 4px 0', 'fontSize': '15px', 'color': TEXT_DARK}),
            html.P('Q4: When is each store generating its revenue across the day?',
                   style={'margin': '0 0 12px 0', 'fontSize': '11px', 'color': '#888'}),
            dcc.Graph(id='hour-heatmap', config={'displayModeBar': False}),
        ]),
        html.Div(style={**card_style, 'flex': '1'}, children=[
            html.H3('Top 10 Products by Revenue', style={'margin': '0 0 4px 0', 'fontSize': '15px', 'color': TEXT_DARK}),
            html.P('Q4: Which specific products are driving the most revenue?',
                   style={'margin': '0 0 12px 0', 'fontSize': '11px', 'color': '#888'}),
            dcc.Graph(id='top-products', config={'displayModeBar': False}),
        ]),
    ]),

    # Footer
    html.Div(style={
        'backgroundColor': HEADER_BG,
        'padding':         '12px 40px',
        'textAlign':       'center',
        'borderTop':       f'2px solid {ACCENT}',
    }, children=[
        html.P('Business Analytics Final Project  |  Coffee Shop Chain Sales Analysis  |  Jan-Jun 2023',
               style={'color': '#888', 'margin': '0', 'fontSize': '11px'}),
    ]),
])

# ── Callbacks ─────────────────────────────────────────────────────────────────

def filter_df(store):
    if store == 'All Stores':
        return df
    return df[df['store_location'] == store]


# KPI cards
@app.callback(
    Output('kpi-revenue',       'children'),
    Output('kpi-transactions',  'children'),
    Output('kpi-avg',           'children'),
    Output('kpi-top-store',     'children'),
    Input('store-filter', 'value'),
)
def update_kpis(store):
    d = filter_df(store)
    rev  = d['Total_Bill'].sum()
    txn  = len(d)
    avg  = d['Total_Bill'].mean()
    top  = d.groupby('store_location')['Total_Bill'].sum().idxmax() if store == 'All Stores' else store

    def kpi_card(label, value):
        return [
            html.P(label, style={'margin': '0 0 6px 0', 'fontSize': '11px',
                                 'color': '#888', 'textTransform': 'uppercase', 'letterSpacing': '0.8px'}),
            html.H2(value, style={'margin': '0', 'fontSize': '24px',
                                  'color': ACCENT, 'fontWeight': 'bold'}),
        ]

    return (
        kpi_card('Total Revenue',      f'${rev:,.0f}'),
        kpi_card('Total Transactions', f'{txn:,}'),
        kpi_card('Avg Transaction',    f'${avg:.2f}'),
        kpi_card('Top Store',          top),
    )


# Monthly trend
@app.callback(
    Output('monthly-trend', 'figure'),
    Input('store-filter', 'value'),
)
def update_monthly(store):
    fig = go.Figure()

    if store == 'All Stores':
        for s, color in STORE_COLORS.items():
            d = df[df['store_location'] == s].groupby('Month')['Total_Bill'].sum().reset_index()
            d['Month Name'] = d['Month'].map(MONTH_MAP)
            d = d.sort_values('Month')
            fig.add_trace(go.Scatter(
                x=d['Month Name'], y=d['Total_Bill'],
                mode='lines+markers', name=s,
                line=dict(color=color, width=2.5),
                marker=dict(size=7),
                hovertemplate=f'<b>{s}</b><br>%{{x}}<br>Revenue: $%{{y:,.0f}}<extra></extra>',
            ))
    else:
        d = df[df['store_location'] == store].groupby('Month')['Total_Bill'].sum().reset_index()
        d['Month Name'] = d['Month'].map(MONTH_MAP)
        d = d.sort_values('Month')
        color = STORE_COLORS.get(store, ACCENT)
        fig.add_trace(go.Scatter(
            x=d['Month Name'], y=d['Total_Bill'],
            mode='lines+markers', name=store,
            line=dict(color=color, width=2.5),
            marker=dict(size=7),
            fill='tozeroy',
            fillcolor='rgba(46,117,182,0.08)' if store == 'Astoria' else 'rgba(192,57,43,0.08)' if store == "Hell's Kitchen" else 'rgba(39,174,96,0.08)',
            hovertemplate=f'<b>{store}</b><br>%{{x}}<br>Revenue: $%{{y:,.0f}}<extra></extra>',
        ))

    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0, font=dict(size=11)),
        xaxis=dict(title='Month', showgrid=False, categoryorder='array', categoryarray=MONTH_ORDER),
        yaxis=dict(title='Total Revenue ($)', showgrid=True, gridcolor='#eee'),
        hovermode='x unified',
        height=300,
    )
    return fig


# Category heatmap
@app.callback(
    Output('category-heatmap', 'figure'),
    Input('store-filter', 'value'),
)
def update_heatmap(store):
    d = filter_df(store)
    pivot = d.groupby(['product_category', 'store_location'])['Total_Bill'].sum().unstack(fill_value=0)
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0).round(3) * 100

    # If filtered to one store, show category bar chart instead
    if store != 'All Stores':
        cat_rev = d.groupby('product_category')['Total_Bill'].sum().sort_values(ascending=True).reset_index()
        colors  = [CAT_COLORS.get(c, '#aaa') for c in cat_rev['product_category']]
        fig = go.Figure(go.Bar(
            x=cat_rev['Total_Bill'], y=cat_rev['product_category'],
            orientation='h',
            marker_color=colors,
            hovertemplate='<b>%{y}</b><br>Revenue: $%{x:,.0f}<extra></extra>',
        ))
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title='Total Revenue ($)', showgrid=True, gridcolor='#eee'),
            yaxis=dict(title=''),
            height=300,
        )
        return fig

    # All stores: heatmap
    fig = go.Figure(go.Heatmap(
        z=pivot_pct.values,
        x=pivot_pct.columns.tolist(),
        y=pivot_pct.index.tolist(),
        colorscale='YlOrRd',
        hovertemplate='<b>%{y}</b><br>%{x}<br>Revenue Share: %{z:.1f}%<extra></extra>',
        colorbar=dict(title=dict(text='% Share', font=dict(size=10)), thickness=12),
        zmin=20,
        zmax=45,
    ))
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title='Store Location'),
        yaxis=dict(title='Product Category'),
        height=300,
    )
    return fig


# Hour heatmap (static, always all stores)
@app.callback(
    Output('hour-heatmap', 'figure'),
    Input('store-filter', 'value'),
)
def update_hour_heatmap(store):
    d = filter_df(store)
    pivot = d.groupby(['store_location', 'Hour'])['Total_Bill'].sum().unstack(fill_value=0)

    if store != 'All Stores':
        hour_rev = d.groupby('Hour')['Total_Bill'].sum().reset_index()
        fig = go.Figure(go.Bar(
            x=hour_rev['Hour'], y=hour_rev['Total_Bill'],
            marker_color=STORE_COLORS.get(store, ACCENT),
            hovertemplate='Hour %{x}:00<br>Revenue: $%{y:,.0f}<extra></extra>',
        ))
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title='Hour of Day', tickmode='linear', dtick=1, showgrid=False),
            yaxis=dict(title='Total Revenue ($)', showgrid=True, gridcolor='#eee'),
            height=300,
        )
        return fig

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[f'{h}:00' for h in pivot.columns.tolist()],
        y=pivot.index.tolist(),
        colorscale='Blues',
        hovertemplate='<b>%{y}</b><br>Hour %{x}<br>Revenue: $%{z:,.0f}<extra></extra>',
        colorbar=dict(title=dict(text='Revenue ($)', font=dict(size=10)), thickness=12),
    ))
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title='Hour of Day'),
        yaxis=dict(title='Store Location'),
        height=300,
    )
    return fig


# Top 10 products
@app.callback(
    Output('top-products', 'figure'),
    Input('store-filter', 'value'),
)
def update_top_products(store):
    d = filter_df(store)
    top = d.groupby('product_detail')['Total_Bill'].sum().sort_values(ascending=False).head(10).reset_index()
    top.columns = ['Product', 'Revenue']

    # Get category for color
    cat_map = df.groupby('product_detail')['product_category'].first()
    top['Category'] = top['Product'].map(cat_map)
    colors = [CAT_COLORS.get(c, '#aaa') for c in top['Category']]

    fig = go.Figure(go.Bar(
        x=top['Revenue'][::-1],
        y=top['Product'][::-1],
        orientation='h',
        marker_color=colors[::-1],
        hovertemplate='<b>%{y}</b><br>Revenue: $%{x:,.0f}<extra></extra>',
    ))
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title='Total Revenue ($)', showgrid=True, gridcolor='#eee'),
        yaxis=dict(title=''),
        height=300,
    )
    return fig


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)