
from app.core.database import database_connection
from app.modules.habits.models import DailyMetric
from app.utils.visualization.charts import (create_metric_chart_html,
                                            get_metric_dataframe)
from flask import Blueprint, jsonify, render_template, request

metrics_bp = Blueprint('metrics', __name__, template_folder='templates', url_prefix='/metrics')


@metrics_bp.route('/dashboard', methods=["GET"])
def dashboard():

    DEFAULT_DAYS = 14

    with database_connection() as session:
        # # Takes in metric_type str & days_ago int => returns DataFrame
        # # Get DataFrame for metric_type weight starting from 7 days ago (ie, show last 7 days)
        df = get_metric_dataframe("weight", DEFAULT_DAYS, session)
        # # Pass in df, metric_type => returns graph_html figure
        weight_graph = create_metric_chart_html(df, "weight")

        # Same for steps
        df_2 = get_metric_dataframe("steps", DEFAULT_DAYS, session)
        steps_graph = create_metric_chart_html(df_2, "steps")

        return render_template("metrics/dashboard.html", 
                            weight_graph=weight_graph,
                            steps_graph=steps_graph)


@metrics_bp.route("/", methods=["POST"])
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