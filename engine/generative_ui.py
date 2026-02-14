
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from typing import Dict, Any, List

class GenerativeRenderer:
    """
    Safe renderer for Agent-generated UI components.
    Protocol: JSON Schema -> Streamlit Widgets.
    """
    
    @staticmethod
    def render(data: Dict[str, Any]):
        """
        Main entry point. Dispatcher based on 'type'.
        Expected JSON format:
        {
            "type": "dashboard | table | chart | mermaid | metrics",
            "title": "Optional Title",
            "content": ... (specific per type)
        }
        """
        try:
            c_type = data.get("type", "unknown")
            title = data.get("title")
            
            if title:
                st.subheader(title)
                
            if c_type == "dashboard":
                GenerativeRenderer._render_dashboard(data.get("components", []))
            elif c_type == "table":
                GenerativeRenderer._render_table(data)
            elif c_type == "chart":
                GenerativeRenderer._render_chart(data)
            elif c_type == "mermaid":
                GenerativeRenderer._render_mermaid(data)
            elif c_type == "metrics":
                GenerativeRenderer._render_metrics(data)
            else:
                st.warning(f"Unknown component type: {c_type}")
                st.json(data) # Fallback for debug
                
        except Exception as e:
            st.error(f"Generative UI Error: {str(e)}")
            st.json(data)

    @staticmethod
    def _render_dashboard(components: List[Dict]):
        """Render a list of components sequentially."""
        for comp in components:
            GenerativeRenderer.render(comp)
            st.markdown("---")

    @staticmethod
    def _render_table(data: Dict):
        """Render a Pandas DataFrame."""
        rows = data.get("data", [])
        if not rows:
            st.info("No data for table.")
            return
        
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)

    @staticmethod
    def _render_metrics(data: Dict):
        """Render a row of kpi metrics."""
        metrics = data.get("items", [])
        cols = st.columns(len(metrics))
        for i, m in enumerate(metrics):
            with cols[i]:
                st.metric(label=m.get("label", "Metric"), value=m.get("value"), delta=m.get("delta"))

    @staticmethod
    def _render_chart(data: Dict):
        """Render a Plotly chart (bar, line, scatter)."""
        chart_type = data.get("chart_type", "bar")
        rows = data.get("data", [])
        x_col = data.get("x")
        y_col = data.get("y")
        
        if not rows:
            st.info("No data for chart.")
            return

        df = pd.DataFrame(rows)
        
        if chart_type == "bar":
            fig = px.bar(df, x=x_col, y=y_col, template="plotly_dark")
        elif chart_type == "line":
            fig = px.line(df, x=x_col, y=y_col, template="plotly_dark")
        elif chart_type == "scatter":
            fig = px.scatter(df, x=x_col, y=y_col, template="plotly_dark")
        else:
            st.warning(f"Unsupported chart type: {chart_type}")
            return
            
        st.plotly_chart(fig, use_container_width=True)

    @staticmethod
    def _render_mermaid(data: Dict):
        """Render a Mermaid Diagram using HTML."""
        code = data.get("code", "")
        import uuid
        div_id = f"mermaid-{uuid.uuid4()}"
        
        # We use a robust CDN for mermaid
        html = f"""
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});
        </script>
        <div class="mermaid">
            {code}
        </div>
        """
        import streamlit.components.v1 as components
        components.html(html, height=500, scrolling=True)
