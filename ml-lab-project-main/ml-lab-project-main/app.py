import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import yfinance as yf
import joblib
import os

folder = "models"
scaler = joblib.load(os.path.join(folder, "market_scaler.pkl"))
pca = joblib.load(os.path.join(folder, "market_pca.pkl"))
svm = joblib.load(os.path.join(folder, "market_svm.pkl"))

app = dash.Dash(__name__)

SIDEBAR_STYLE = {
    "position": "fixed", "top": 0, "left": 0, "bottom": 0,
    "width": "22rem", "padding": "2rem 1rem", "backgroundColor": "#1a1a1a", "color": "white"
}
CONTENT_STYLE = {"marginLeft": "25rem", "marginRight": "2rem", "padding": "2rem 1rem"}

app.layout = html.Div([
    html.Div([
        html.H2("ML ARCHITECTURE", style={'color': '#00d1b2', 'fontSize': '22px'}),
        html.Hr(style={'borderColor': '#444'}),
        html.P("Syllabus Alignment:", style={'fontWeight': 'bold', 'color': '#888'}),
        html.Ul([
            html.Li([html.Span("Sec 2.1: ", style={'color': '#00d1b2'}), "Feature Scaling"]),
            html.Li([html.Span("Sec 6.3: ", style={'color': '#00d1b2'}), "PCA Projection"]),
            html.Li([html.Span("Sec 4.2: ", style={'color': '#00d1b2'}), "EM Clustering"]),
            html.Li([html.Span("Sec 3.2: ", style={'color': '#00d1b2'}), "SVM Classification"]),
        ], style={'lineHeight': '2.2', 'listStyleType': 'none', 'paddingLeft': '0'}),
        html.Hr(style={'borderColor': '#444'}),
        html.Div(id="stats-box")
    ], style=SIDEBAR_STYLE),

    html.Div([
        html.H1("Nifty 50 Real-Time Intelligence", style={'fontWeight': '800', 'marginBottom': '0px'}),
        html.P("Predictive Market Regime Detection Engine", style={'color': '#666', 'fontSize': '18px'}),
        html.Div(id='live-status-indicator', style={'marginTop': '10px'}),
        
        dcc.Graph(id='regime-graph', config={'displayModeBar': True}),
        
        html.Div([
            html.H4("Inference Logic Path:", style={'marginBottom': '15px'}),
            html.Div(id='pipeline-explanation', style={
                'padding': '25px', 'backgroundColor': '#ffffff', 'borderRadius': '12px', 
                'border': '1px solid #ddd', 'boxShadow': '0px 4px 12px rgba(0,0,0,0.05)'
            })
        ], style={'marginTop': '30px'}),

        dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0)
    ], style=CONTENT_STYLE)
])

@app.callback(
    [Output('regime-graph', 'figure'),
     Output('live-status-indicator', 'children'),
     Output('pipeline-explanation', 'children'),
     Output('stats-box', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    raw_data = yf.download("^NSEI", period="2y", interval="1d")
    
    if raw_data.empty:
        return go.Figure(), "Waiting for data...", "No data found.", "N/A"

    try:
        df = raw_data.xs('^NSEI', axis=1, level='Ticker').copy()
    except:
        df = raw_data.copy()

    df['Returns'] = np.log(df['Close'] / df['Close'].shift(1))
    df['Range'] = (df['High'] - df['Low']) / df['Close']
    df['Volatility'] = df['Returns'].rolling(window=20).std()
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['Upper'] = df['MA20'] + (df['Close'].rolling(window=20).std() * 2)
    df['Lower'] = df['MA20'] - (df['Close'].rolling(window=20).std() * 2)
    df.dropna(inplace=True)

    if df.empty:
        return go.Figure(), "Insufficient Data", "Calculating indicators...", "Processing..."

    features = ['Returns', 'Range', 'Volatility']
    X_scaled = scaler.transform(df[features].values)
    X_pca = pca.transform(X_scaled)
    df['Regime'] = svm.predict(X_scaled)
    
    current_regime = df['Regime'].iloc[-1]
    status_label = "CRITICAL STRESS" if current_regime == 1 else "OPTIMAL STABILITY"
    status_color = "#ff3860" if current_regime == 1 else "#23d160"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index.tolist() + df.index[::-1].tolist(),
        y=df['Upper'].tolist() + df['Lower'][::-1].tolist(),
        fill='toself', fillcolor='rgba(0,209,178,0.07)',
        line=dict(color='rgba(255,255,255,0)'), name='Vol Band'
    ))
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price', line=dict(color='#34495e', width=2)))
    stress = df[df['Regime'] == 1]
    fig.add_trace(go.Scatter(x=stress.index, y=stress['Close'], mode='markers', 
                             name='Stress Detected', marker=dict(color='#ff3860', size=8, symbol='x')))

    fig.update_layout(
        template='plotly_white', height=550, margin=dict(l=10, r=10, t=10, b=10),
        yaxis=dict(fixedrange=False, autorange=True, title="Nifty 50 Points"),
        xaxis=dict(rangeslider=dict(visible=True)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    status_indicator = html.Div([
        html.Span(status_label, style={
            'backgroundColor': status_color, 'color': 'white', 'padding': '8px 20px', 
            'borderRadius': '25px', 'fontWeight': 'bold', 'fontSize': '22px'
        })
    ])
    
    explanation = html.Div([
        html.P([html.Strong("Step 1: "), "Standardized features (Sec 2.1)."]),
        html.P([html.Strong("Step 2: "), f"PCA Projection (Sec 6.3): P1={X_pca[-1,0]:.2f}, P2={X_pca[-1,1]:.2f}."]),
        html.P([html.Strong("Step 3: "), f"SVM Classification (Sec 3.2). Current state: {status_label}."])
    ])

    stats = html.Div([
        html.P(f"Live Price: {df['Close'].iloc[-1]:.2f}"),
        html.P(f"Volatility: {df['Volatility'].iloc[-1]:.5f}"),
        html.P(f"Sample: {len(df)} Days")
    ], style={'color': '#00d1b2', 'fontSize': '16px', 'marginTop': '20px'})

    return fig, status_indicator, explanation, stats

if __name__ == '__main__':
    app.run(debug=True, port=8050)