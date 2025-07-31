from flask import Blueprint, request, render_template, jsonify, current_app
from services.mcp_order_processor import MCPOrderProcessor

intelligent_orders_bp = Blueprint(
    "intelligent_orders", __name__, template_folder="templates/orders"
)


@intelligent_orders_bp.route("/parse-order", methods=["POST"])
def parse_order():
    raw_text = request.json.get("order_text", "")
    processor = MCPOrderProcessor(hf_token=current_app.config.get("HF_TOKEN"))
    result = processor.process_order(raw_text)
    return jsonify(result)


@intelligent_orders_bp.route("/copy-paste-interface", methods=["GET", "POST"])
def copy_paste_interface():
    if request.method == "POST":
        raw_text = request.form.get("order_input", "")
        processor = MCPOrderProcessor(hf_token=current_app.config.get("HF_TOKEN"))
        result = processor.process_order(raw_text)
        return render_template(
            "orders/copy_paste_input.html", result=result, raw_text=raw_text
        )
    return render_template("orders/copy_paste_input.html", result=None, raw_text="")


@intelligent_orders_bp.route("/customer-service", methods=["POST"])
def customer_service():
    request.json.get("question", "")
    # Call MCP QA tool here
    return jsonify({"answer": "Not implemented yet"})
