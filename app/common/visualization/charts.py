from datetime import datetime, timedelta, timezone
from typing import Any, Type
import sys
import pandas as pd
import plotly.express as px
from sqlalchemy import func
from sqlalchemy.orm import Session



def get_filtered_dataframe(session: Session, model_name: Type[Any], user_id: int, filter_field:str, filter_value, value_field_name:str, days_ago: int) -> pd.DataFrame:
    """
    Queries a database table and returns a pandas DataFrame with filtered data ready for plotting.
    
    Args:
        session: SQLAlchemy Session object.
        model_name: Name of database table to query.
        user_id: User id by which to filter query.
        filter_field: Name of column we're filtering on. (ie, "category", "metric_type")
        filter_value: Name of what we're searching for. (ie, "Programming", "weight")
        value_field_name: Name of column we're extracting data from to be plotted. (ie, "duration", "value")
        days_ago: Integer representing how far back in time our query should reach.
    Returns:
        pd.DataFrame: Pandas DataFrame.
    Examples:
        ### Get weight from DailyMetric
        df = get_filtered_dataframe(session, DailyMetric, current_user.id, "metric_type", "weight", "value", 30)

        ### Get programming time from TimeEntry  
        df = get_filtered_dataframe(session, TimeEntry, current_user.id, "category", "Programming", "duration", 7)
    """
    today_utc = datetime.now(timezone.utc)
    start_date = (today_utc - timedelta(days=days_ago)).replace(hour=0, minute=0, second=0, microsecond=0)

    # SQLAlchemy uses column objects like TimeEntry.category & translates == into "'WHERE category = 'Programming'"
    # Just passing str "category" then doing model_name.filter_field directly wouldn't work here
    # Need to reconstruct column object from the string
    filter_field_obj = getattr(model_name, filter_field)

    # Query for filtered data
    # Extract matching entries & their values (e.g., duration, weight measurements)

    # Need all model_names for filter_field_obj where date is between today & days_ago, ordered by date
    entries = session.query(model_name).filter(
        filter_field_obj == filter_value,
        model_name.created_at >= start_date,    # now both datetime to datetime
        model_name.created_at <= today_utc,     # compares datetime to datetime
        model_name.user_id==user_id
    ).order_by(model_name.created_at).all()

    # Extract dates & values for plotting into discrete lists
    # Note: using .date() to strip datetime objects to dates => Plenty for graphs for now
    dates = [entry.created_at for entry in entries]            # [date1, date2, date3, ...]
    values = [getattr(entry, value_field_name) for entry in entries]  # [value1, value2, null, ...]

    # Get these into our data frame
    df = pd.DataFrame({'Date': dates, filter_value.title(): values})
    df['Date'] = pd.to_datetime(df['Date']) # makes this datetime64[ns] as it should be
    return df

## Note to self: Plotly uses D3.js time format specifiers under the hood, NOT Python's strftime
### Meaning time formats that are valid in Python are not necessarily valid in Plotly
def create_metric_chart_html(df: pd.DataFrame, 
                             metric_type: str, 
                             title: str = None,
                             date_format: str = "%d.%m") -> str:

    """
    Convert metric DataFrame to HTML chart.
    Args:
        df: Pandas DataFrame being passed in.
        metric_type: Name of the metric (for titles/labels)
        chart_type: Type of chart ('line', 'bar', etc.)
        date_format: Format string for x-axis dates
        
    Returns:
        HTML string ready for template rendering
    """

    if title is None:
        title = f"{metric_type.title()} over time"

    print(df.dtypes, file=sys.stderr)
    fig = px.line(df, x=df.columns[0], y=df.columns[1], title=title)

    fig.update_xaxes(
        # tickformat=date_format,        # TODO: This causes error for bad format, need to test & iron out
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