from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Base URL for the Inventory Service
INVENTORY_SERVICE_URL = "http://inventory-service"

@app.route('/placeOrder', methods=['POST'])
def place_order():
    try:
        # Parse request payload
        data = request.get_json()
        product_id = data.get("productId")
        
        if not product_id:
            return jsonify({"error": "Product ID is required"}), 400

        # Check inventory status
        inventory_status_url = f"{INVENTORY_SERVICE_URL}/inventory/{product_id}"
        inventory_response = requests.get(inventory_status_url)
                
        if inventory_response.status_code != 200:
            return jsonify({"error": "Failed to check inventory status"}), 500

        # Get the available quantity of the product
        inventory_data = inventory_response.json()
        available_quantity = inventory_data.get("quantity", 0)

        #Check if the product is out of stock or not
        if available_quantity <= 0:
            return jsonify({"message": "Product is out of stock"}), 200

        # Update inventory (decrement quantity)
        update_inventory_url = f"{INVENTORY_SERVICE_URL}/inventory/{product_id}"
        update_payload = {
            "op": "SUB",
            "qty": 1  # Assuming we decrement by 1 for each order
        }
        update_response = requests.put(update_inventory_url, json=update_payload)

        if update_response.status_code == 200:
            return jsonify({"message": "Order has been placed"}), 200
        else:
            return jsonify({"message": "Something went wrong. Please retry"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
