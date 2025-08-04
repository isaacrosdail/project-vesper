
from app.core.database import database_connection
from app.modules.metrics.models import DailyMetric
from app.modules.metrics import repository as metrics_repo
from app.common.visualization.charts import (create_metric_chart_html,
                                            get_filtered_dataframe)
from flask import Blueprint, jsonify, render_template, request
from app.common.sorting import bubble_sort

from app.core.constants import DEFAULT_CHART_DAYS
from flask_login import current_user, login_required

metrics_bp = Blueprint('metrics', __name__, template_folder='templates', url_prefix='/metrics')


@metrics_bp.route('/dashboard', methods=["GET"])
@login_required
def dashboard():

    with database_connection() as session:
        # # Takes in metric_type str & days_ago int => returns DataFrame
        # # Get DataFrame for metric_type weight starting from 7 days ago (ie, show last 7 days)
        df = get_filtered_dataframe(session, DailyMetric, current_user.id, "metric_type", "weight", "value", DEFAULT_CHART_DAYS)
        # # Pass in df, metric_type => returns graph_html figure
        weight_graph = create_metric_chart_html(df, "weight")

        # Same for steps
        df_2 = get_filtered_dataframe(session, DailyMetric, current_user.id, "metric_type", "steps", "value", DEFAULT_CHART_DAYS)
        steps_graph = create_metric_chart_html(df_2, "steps")

        # Get list of all metrics for table, sort by date for now
        metrics = metrics_repo.get_user_metrics(session, current_user.id)
        bubble_sort(metrics, 'created_at', reverse=True)

        return render_template("metrics/dashboard.html", 
                            weight_graph=weight_graph,
                            steps_graph=steps_graph,
                            metrics=metrics)


@metrics_bp.route("/", methods=["POST"])
@login_required
def metrics():
    data = request.get_json()

    try:
        with database_connection() as session:
            new_metric = DailyMetric(
                metric_type=data["metric_type"],
                value=data["value"],
                unit=data["unit"]
            )
            session.add(new_metric)

            return jsonify({"success": True, "message": "Successfully added metric"}), 201

    # TODO: Security - don't expose internal errors to users, need to adjust
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500