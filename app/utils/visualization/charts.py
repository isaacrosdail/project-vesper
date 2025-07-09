from datetime import datetime, timedelta, timezone

import pandas as pd
import plotly.express as px
from app.modules.metrics.models import DailyMetric
from app.modules.time_tracking.models import TimeEntry
from typing import Type, Any
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.db_base import Base


# Function to return results from query for metric_type & timeframe for graphing our data with Plotly
# Gets metric data ready for visualization
def get_metric_dataframe(metric_type: str, days_ago: int, session: Session) -> pd.DataFrame:
    """
    Get metric data for the last X days, formatted for plotting.
    Args:
        metric_type: eg, 'weight', 'sleep'
        days_ago: Number of days back from today to include/start
        session: Database session for executing queries
    Returns:
        DataFrame with 'Date' & capitalized metric_type columns
    """
    
    today_utc = datetime.now(timezone.utc)
    # Since .func strips timezone, need .date() to make start_date a date, not a datetime
    start_date = (today_utc - timedelta(days=days_ago)).date()

    # Query for weight: 
    # Need all DailyMetrics for metric_type where date is between today & days_ago ordered by date
    metric_entries = session.query(DailyMetric).filter(
        DailyMetric.metric_type == metric_type,
        func.date(DailyMetric.created_at) >= start_date, # compares date to date
        DailyMetric.created_at <= today_utc              # compares datetime to datetime (fine to mix?)
    ).order_by(DailyMetric.created_at).all()

    # Extract dates & metric_type entries into lists for Plotly
    # Note: using .date() to strip datetime objects to dates => Plenty for graphs for now
    dates = [entry.created_at.date() for entry in metric_entries] # [date1, date2, date3, ...]
    values = [entry.value for entry in metric_entries]            # [value1, value2, null, ...]

    # Get these into our data frame
    df = pd.DataFrame({'Date': dates, metric_type.title(): values})

    # Return DataFrame to caller
    return df

# get_metric_dataframe adapted for TimeEntries
def get_time_entry_dataframe(model_name: Type[Any], category: str, days_ago: int, session: Session) -> pd.DataFrame:
    
    today_utc = datetime.now(timezone.utc)
    start_date = (today_utc - timedelta(days=days_ago)).date()

    # Query for given category
    # Need all model_names for metric_type where date is between today & days_ago ordered by date
    entries = session.query(model_name).filter(
        model_name.category == category,
        func.date(model_name.created_at) >= start_date, # compares date to date
        model_name.created_at <= today_utc              # compares datetime to datetime (fine to mix?)
    ).order_by(model_name.created_at).all()

    # Extract dates & category entries into lists for Plotly
    # Note: using .date() to strip datetime objects to dates => Plenty for graphs for now
    dates = [entry.created_at.date() for entry in entries] # [date1, date2, date3, ...]
    values = [entry.duration for entry in entries]            # [value1, value2, null, ...]

    # Get these into our data frame
    df = pd.DataFrame({'Date': dates, category.title(): values})

    # Return DataFrame to caller
    return df

def create_metric_chart_html(df: pd.DataFrame, 
                             metric_type: str, 
                             title: str = None, 
                             date_format: str = "%d.%m") -> str:

    """
    Convert metric DataFrame to HTML chart.
    Args:
        df: DataFrame from get_metric_dataframe()
        metric_type: Name of the metric (for titles/labels)
        chart_type: Type of chart ('line', 'bar', etc.)
        date_format: Format string for x-axis dates
        
    Returns:
        HTML string ready for template rendering
    """

    if title is None:
        title = f"{metric_type.title()} over time"

    fig = px.line(df, x=df.columns[0], y=df.columns[1], title=title)
    fig.update_xaxes(
        tickformat=date_format,        # Default: DD.MM
        dtick=2 * 24 * 60 * 60 * 1000, # 2 days in ms (show every other day)
        )

    fig.update_layout(
        autosize=True,
        margin=dict(l=30, r=10, t=30, b=30), # consistent margins
        xaxis=dict(
            tickangle=45,
        ),
        yaxis=dict(
            title=None  # Drop metric_type Y-axis title
            # But..add this back once we sort out displaying units here
        )
    )
    # rich hover info?
    # fig.update_traces(
    #     hovertemplate='<b>%{y}</b><br>%{x}<extra></extra>'
    # )

    return fig.to_html(include_plotlyjs='cdn')