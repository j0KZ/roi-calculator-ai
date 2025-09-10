"""
Dark theme configuration for Plotly charts
"""

def apply_dark_theme(fig):
    """Apply black and gold dark theme to Plotly figure"""
    
    fig.update_layout(
        paper_bgcolor='#0a0a0a',
        plot_bgcolor='#1a1a1a',
        font=dict(
            color='#ffffff',
            family='sans-serif'
        ),
        title=dict(
            font=dict(
                color='#f5b800',
                size=20
            )
        ),
        xaxis=dict(
            gridcolor='#333333',
            linecolor='#f5b800',
            tickfont=dict(color='#ffffff'),
            zerolinecolor='#333333'
        ),
        yaxis=dict(
            gridcolor='#333333',
            linecolor='#f5b800',
            tickfont=dict(color='#ffffff'),
            zerolinecolor='#333333'
        ),
        legend=dict(
            bgcolor='#1a1a1a',
            bordercolor='#f5b800',
            borderwidth=1,
            font=dict(color='#ffffff')
        ),
        hoverlabel=dict(
            bgcolor='#1a1a1a',
            bordercolor='#f5b800',
            font=dict(color='#ffffff')
        ),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    # Update traces for better visibility (only for chart types that support marker properties)
    # Skip for Indicator traces (gauges) which don't have marker properties
    if fig.data and hasattr(fig.data[0], 'type'):
        if fig.data[0].type not in ['indicator']:
            fig.update_traces(
                marker_line_color='#f5b800',
                marker_line_width=1
            )
    
    return fig

def get_dark_color_sequence():
    """Get color sequence for dark theme"""
    return ['#f5b800', '#ffd700', '#ff9500', '#ff6b35', '#c9302c', '#8b4513']

def get_gauge_theme():
    """Get gauge chart theme configuration"""
    return {
        'bar_color': '#f5b800',
        'bgcolor': '#1a1a1a',
        'bordercolor': '#f5b800',
        'steps': [
            {'range': [0, 50], 'color': '#2a2a2a'},
            {'range': [50, 100], 'color': '#3a3a3a'},
            {'range': [100, 200], 'color': '#4a4a4a'},
            {'range': [200, 300], 'color': '#5a5a5a'}
        ],
        'threshold': {
            'line': {'color': '#ff0000', 'width': 4},
            'thickness': 0.75,
            'value': 100
        }
    }

def style_metric_container():
    """CSS for styling metric containers"""
    return """
    <style>
        [data-testid="metric-container"] {
            background-color: #1a1a1a;
            border: 1px solid #f5b800;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(245, 184, 0, 0.3);
        }
        [data-testid="metric-container"] [data-testid="metric-label"] {
            color: #f5b800 !important;
        }
        [data-testid="metric-container"] [data-testid="metric-value"] {
            color: #ffffff !important;
        }
        [data-testid="metric-container"] [data-testid="metric-delta"] {
            color: #f5b800 !important;
        }
    </style>
    """