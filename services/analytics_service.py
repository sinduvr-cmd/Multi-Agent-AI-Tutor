"""
Analytics Service using Plotly and Pandas.
Generates interactive visualizations for student mastery radar,
session accuracy trends, and topic breakdown.
"""

from typing import Dict, Any, List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class AnalyticsService:
    """Generates charts and metric visualizations for student and teacher dashboards."""

    @staticmethod
    def create_mastery_radar(mastery_data: List[Dict[str, Any]]) -> go.Figure:
        """Radar / Polar chart showing student mastery % across different topics."""
        if not mastery_data:
            # Empty state figure
            fig = go.Figure()
            fig.add_annotation(
                text="Take a quiz to view your Topic Mastery Radar",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=14, color="#64748B")
            )
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=False)),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=300
            )
            return fig

        categories = [m["topic_title"] for m in mastery_data]
        scores = [m["score_percentage"] for m in mastery_data]
        
        # Close the polygon loop
        categories.append(categories[0])
        scores.append(scores[0])

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=scores,
            theta=categories,
            fill='toself',
            fillcolor='rgba(79, 70, 229, 0.25)',
            line=dict(color='#4F46E5', width=2.5),
            marker=dict(size=7, color='#4338CA'),
            name='Mastery %'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickfont=dict(size=10, color="#64748B"),
                    gridcolor="#E2E8F0"
                ),
                angularaxis=dict(
                    tickfont=dict(size=11, color="#1E293B", family="sans-serif")
                )
            ),
            showlegend=False,
            margin=dict(l=40, r=40, t=30, b=30),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=320
        )
        return fig

    @staticmethod
    def create_accuracy_donut(correct: int, total: int) -> go.Figure:
        """Donut chart for overall quiz accuracy."""
        incorrect = max(0, total - correct)
        
        if total == 0:
            labels = ["No Data"]
            values = [1]
            colors = ["#CBD5E1"]
        else:
            labels = ["Correct", "Incorrect"]
            values = [correct, incorrect]
            colors = ["#10B981", "#EF4444"]

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.68,
            marker=dict(colors=colors),
            textinfo='percent' if total > 0 else 'none',
            hoverinfo='label+value'
        )])

        pct_text = f"{int((correct / max(1, total)) * 100)}%" if total > 0 else "0%"
        fig.update_layout(
            annotations=[dict(text=pct_text, x=0.5, y=0.5, font_size=24, font_family="sans-serif", font_color="#1E293B", showarrow=False)],
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
            margin=dict(l=10, r=10, t=10, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=240
        )
        return fig

    @staticmethod
    def create_attempts_timeline(attempts: List[Dict[str, Any]]) -> go.Figure:
        """Bar or line chart showing student score progression over time."""
        if not attempts:
            fig = go.Figure()
            fig.add_annotation(
                text="No quiz history yet. Start a quiz to track your progress!",
                xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
                font=dict(size=14, color="#64748B")
            )
            fig.update_layout(
                xaxis=dict(visible=False), yaxis=dict(visible=False),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=260
            )
            return fig

        df = pd.DataFrame(attempts)
        df["attempt_time"] = pd.to_datetime(df["attempt_time"])
        df = df.sort_values("attempt_time")

        # Rolling 5-attempt accuracy
        df["rolling_accuracy"] = df["is_correct"].rolling(window=5, min_periods=1).mean() * 100

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(range(1, len(df) + 1)),
            y=df["marks_awarded"],
            name="Marks Earned",
            marker_color="#818CF8",
            opacity=0.7
        ))
        fig.add_trace(go.Scatter(
            x=list(range(1, len(df) + 1)),
            y=df["rolling_accuracy"],
            name="Accuracy Trend (5-Q Avg %)",
            mode='lines+markers',
            line=dict(color='#059669', width=2.5),
            yaxis="y2"
        ))

        fig.update_layout(
            yaxis=dict(title="Marks", range=[0, max(df["max_marks"]) + 1]),
            yaxis2=dict(title="Accuracy %", overlaying="y", side="right", range=[0, 105]),
            xaxis=dict(title="Question Attempt #", gridcolor="#F1F5F9"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=40, r=40, t=30, b=40),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=280
        )
        return fig
