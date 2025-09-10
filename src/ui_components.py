#!/usr/bin/env python3
"""
Modern UI Components for ROI Calculator
Magic UI-inspired components with animations and glassmorphism
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import Optional, Dict, Any, List
import json

class ModernUI:
    """Modern UI components with glassmorphism and animations"""
    
    @staticmethod
    def inject_custom_css():
        """Inject custom CSS for modern UI effects"""
        st.markdown("""
        <style>
        /* Glassmorphism effect */
        .glass-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            padding: 2rem;
            margin: 1rem 0;
            transition: all 0.3s ease;
        }
        
        .glass-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.5);
        }
        
        /* Gradient buttons */
        .gradient-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 50px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .gradient-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        
        /* Animated gradients */
        .animated-gradient {
            background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
        }
        
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        /* Neon glow effect */
        .neon-text {
            color: #fff;
            text-shadow: 
                0 0 10px #fff,
                0 0 20px #fff,
                0 0 30px #e60073,
                0 0 40px #e60073,
                0 0 50px #e60073,
                0 0 60px #e60073,
                0 0 70px #e60073;
        }
        
        /* Floating animation */
        .floating {
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
            100% { transform: translateY(0px); }
        }
        
        /* Pulse animation */
        .pulse {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        /* Modern card */
        .modern-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.18);
            padding: 20px;
            margin: 10px 0;
        }
        
        /* Smooth transitions */
        * {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
        }
        
        /* Tooltip */
        .tooltip {
            position: relative;
            display: inline-block;
        }
        
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 200px;
            background: linear-gradient(135deg, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.7) 100%);
            color: #fff;
            text-align: center;
            border-radius: 10px;
            padding: 10px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def glass_card(content: str, title: Optional[str] = None):
        """Create a glassmorphism card"""
        title_html = f"<h3 style='color: #fff; margin-bottom: 1rem;'>{title}</h3>" if title else ""
        st.markdown(f"""
        <div class="glass-card">
            {title_html}
            <div style='color: rgba(255,255,255,0.9);'>
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def gradient_button(label: str, key: str) -> bool:
        """Create a gradient button"""
        return st.button(label, key=key, use_container_width=True)
    
    @staticmethod
    def animated_metric(label: str, value: str, delta: Optional[str] = None, animation: str = "pulse"):
        """Create an animated metric display"""
        delta_html = f"<div style='color: #4ecdc4; font-size: 0.9rem;'>{delta}</div>" if delta else ""
        st.markdown(f"""
        <div class="modern-card {animation}">
            <div style='color: rgba(255,255,255,0.6); font-size: 0.9rem; margin-bottom: 0.5rem;'>
                {label}
            </div>
            <div style='color: #fff; font-size: 2rem; font-weight: 700;'>
                {value}
            </div>
            {delta_html}
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def progress_ring(percentage: float, label: str):
        """Create a circular progress ring"""
        circumference = 2 * 3.14159 * 45
        offset = circumference - (percentage / 100) * circumference
        
        st.markdown(f"""
        <div style='text-align: center; margin: 20px;'>
            <svg width="120" height="120">
                <circle cx="60" cy="60" r="45" 
                    stroke="rgba(255,255,255,0.1)" 
                    stroke-width="10" 
                    fill="none"/>
                <circle cx="60" cy="60" r="45" 
                    stroke="url(#gradient)" 
                    stroke-width="10" 
                    fill="none"
                    stroke-dasharray="{circumference}"
                    stroke-dashoffset="{offset}"
                    transform="rotate(-90 60 60)"
                    style="transition: stroke-dashoffset 0.5s ease;"/>
                <defs>
                    <linearGradient id="gradient">
                        <stop offset="0%" stop-color="#667eea"/>
                        <stop offset="100%" stop-color="#764ba2"/>
                    </linearGradient>
                </defs>
                <text x="60" y="55" text-anchor="middle" 
                    fill="white" font-size="24" font-weight="bold">
                    {percentage:.0f}%
                </text>
                <text x="60" y="75" text-anchor="middle" 
                    fill="rgba(255,255,255,0.6)" font-size="12">
                    {label}
                </text>
            </svg>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def animated_header(text: str, gradient: bool = True):
        """Create an animated header with gradient"""
        class_name = "animated-gradient" if gradient else ""
        st.markdown(f"""
        <h1 class="{class_name}" style='
            font-size: 3rem;
            font-weight: 800;
            text-align: center;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
        '>
            {text}
        </h1>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def floating_card(content: str, icon: str = "🚀"):
        """Create a floating card with icon"""
        st.markdown(f"""
        <div class="modern-card floating" style='text-align: center;'>
            <div style='font-size: 3rem; margin-bottom: 1rem;'>{icon}</div>
            <div style='color: rgba(255,255,255,0.9);'>{content}</div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def create_particles():
        """Create particle animation background"""
        particles_html = """
        <div id="particles-js" style="position: fixed; width: 100%; height: 100%; top: 0; left: 0; z-index: -1;"></div>
        <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
        <script>
        particlesJS('particles-js', {
            particles: {
                number: { value: 80, density: { enable: true, value_area: 800 } },
                color: { value: "#ffffff" },
                shape: { type: "circle" },
                opacity: { value: 0.5, random: false },
                size: { value: 3, random: true },
                line_linked: {
                    enable: true,
                    distance: 150,
                    color: "#ffffff",
                    opacity: 0.4,
                    width: 1
                },
                move: {
                    enable: true,
                    speed: 2,
                    direction: "none",
                    random: false,
                    straight: false,
                    out_mode: "out",
                    bounce: false
                }
            },
            interactivity: {
                detect_on: "canvas",
                events: {
                    onhover: { enable: true, mode: "repulse" },
                    onclick: { enable: true, mode: "push" },
                    resize: true
                }
            },
            retina_detect: true
        });
        </script>
        """
        components.html(particles_html, height=0)

class RealTimeUpdates:
    """Real-time update components using WebSockets"""
    
    @staticmethod
    def create_websocket_component():
        """Create WebSocket component for real-time updates"""
        websocket_html = """
        <script>
        let ws = null;
        
        function connectWebSocket() {
            ws = new WebSocket('ws://localhost:8765');
            
            ws.onopen = function() {
                console.log('WebSocket connected');
                document.dispatchEvent(new CustomEvent('ws-connected'));
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                document.dispatchEvent(new CustomEvent('ws-message', { detail: data }));
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
            
            ws.onclose = function() {
                console.log('WebSocket closed, reconnecting...');
                setTimeout(connectWebSocket, 3000);
            };
        }
        
        // Auto-connect on load
        if (typeof ws === 'undefined' || ws === null || ws.readyState === WebSocket.CLOSED) {
            connectWebSocket();
        }
        
        // Function to send data
        window.sendWSMessage = function(data) {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify(data));
            }
        };
        </script>
        """
        components.html(websocket_html, height=0)
    
    @staticmethod
    def live_metric(metric_id: str, initial_value: Any = 0):
        """Create a live updating metric"""
        update_script = f"""
        <div id="{metric_id}" class="modern-card pulse">
            <span style='font-size: 2rem; color: #fff;'>{initial_value}</span>
        </div>
        <script>
        document.addEventListener('ws-message', function(e) {{
            if (e.detail.metric_id === '{metric_id}') {{
                document.getElementById('{metric_id}').querySelector('span').innerText = e.detail.value;
            }}
        }});
        </script>
        """
        components.html(update_script, height=100)

class ChartComponents:
    """Modern chart components with animations"""
    
    @staticmethod
    def animated_line_chart(data: Dict[str, List], title: str):
        """Create an animated line chart"""
        chart_html = f"""
        <div class="modern-card">
            <h3 style='color: #fff; margin-bottom: 1rem;'>{title}</h3>
            <canvas id="animatedChart"></canvas>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
        const ctx = document.getElementById('animatedChart').getContext('2d');
        const chart = new Chart(ctx, {{
            type: 'line',
            data: {json.dumps(data)},
            options: {{
                responsive: true,
                animation: {{
                    duration: 2000,
                    easing: 'easeInOutQuart'
                }},
                scales: {{
                    y: {{ beginAtZero: true }}
                }},
                plugins: {{
                    legend: {{
                        labels: {{ color: 'white' }}
                    }}
                }}
            }}
        }});
        </script>
        """
        components.html(chart_html, height=400)
    
    @staticmethod
    def gauge_chart(value: float, max_value: float, label: str):
        """Create a gauge chart"""
        percentage = (value / max_value) * 100
        rotation = (percentage * 1.8) - 90  # Convert to degrees
        
        st.markdown(f"""
        <div class="modern-card" style='text-align: center;'>
            <h4 style='color: rgba(255,255,255,0.8);'>{label}</h4>
            <div style='position: relative; width: 200px; height: 100px; margin: 0 auto;'>
                <svg width="200" height="100">
                    <!-- Background arc -->
                    <path d="M 20 80 A 60 60 0 0 1 180 80" 
                        stroke="rgba(255,255,255,0.1)" 
                        stroke-width="20" 
                        fill="none"/>
                    <!-- Value arc -->
                    <path d="M 20 80 A 60 60 0 0 1 180 80" 
                        stroke="url(#gaugeGradient)" 
                        stroke-width="20" 
                        fill="none"
                        stroke-dasharray="{percentage * 1.88} 188"
                        style="transition: stroke-dasharray 1s ease;"/>
                    <defs>
                        <linearGradient id="gaugeGradient">
                            <stop offset="0%" stop-color="#23d5ab"/>
                            <stop offset="50%" stop-color="#23a6d5"/>
                            <stop offset="100%" stop-color="#e73c7e"/>
                        </linearGradient>
                    </defs>
                    <!-- Needle -->
                    <line x1="100" y1="80" x2="100" y2="30" 
                        stroke="white" 
                        stroke-width="3"
                        transform="rotate({rotation} 100 80)"
                        style="transition: transform 1s ease;"/>
                    <circle cx="100" cy="80" r="5" fill="white"/>
                </svg>
                <div style='position: absolute; bottom: -10px; width: 100%; text-align: center;'>
                    <span style='color: #fff; font-size: 1.5rem; font-weight: bold;'>
                        {value:.1f} / {max_value:.1f}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

class NotificationSystem:
    """Modern notification system"""
    
    @staticmethod
    def show_success(message: str):
        """Show success notification"""
        st.markdown(f"""
        <div class="notification success" style='
            background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: 10px;
            margin: 1rem 0;
            animation: slideIn 0.5s ease;
        '>
            ✅ {message}
        </div>
        <style>
        @keyframes slideIn {{
            from {{ transform: translateX(100%); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def show_error(message: str):
        """Show error notification"""
        st.markdown(f"""
        <div class="notification error" style='
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: 10px;
            margin: 1rem 0;
            animation: shake 0.5s ease;
        '>
            ❌ {message}
        </div>
        <style>
        @keyframes shake {{
            0%, 100% {{ transform: translateX(0); }}
            25% {{ transform: translateX(-10px); }}
            75% {{ transform: translateX(10px); }}
        }}
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def show_info(message: str):
        """Show info notification"""
        st.markdown(f"""
        <div class="notification info" style='
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: 10px;
            margin: 1rem 0;
            animation: fadeIn 0.5s ease;
        '>
            ℹ️ {message}
        </div>
        <style>
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        </style>
        """, unsafe_allow_html=True)