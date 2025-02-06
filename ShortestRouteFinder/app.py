from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import googlemaps
import os  # Importing os to access environment variables

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)

# Initialize Google Maps API client with your API key
gmaps = googlemaps.Client(key=os.getenv('GOOGLE_API_KEY'))

@app.route('/')
def index():
    # Pass the Google Maps API key to the template
    google_api_key = os.getenv('GOOGLE_API_KEY')  # Get API key from environment variables
    return render_template('index.html', google_api_key=google_api_key)

@app.route('/route', methods=['POST'])
def get_route():
    # Get data from the frontend
    data = request.get_json()
    origin = data.get('origin')
    destination = data.get('destination')

    if not origin or not destination:
        return jsonify({'status': 'error', 'error': 'Origin or destination not provided'}), 400

    try:
        # Use Google Maps API to get the directions
        directions_result = gmaps.directions(origin, destination, mode="driving")

        # Check if directions result exists
        if directions_result:
            route = directions_result[0]
            leg = route['legs'][0]  # Extract the first leg of the journey
            
            # Extract step-by-step directions
            steps = []
            for step in leg['steps']:
                steps.append(step['html_instructions'])  # Extract directions text

            directions_data = {
                'status': 'OK',
                'legs': leg,  # Includes distance, duration, etc.
                'overview_polyline': route['overview_polyline']['points'],  # Polyline for map
                'steps': steps  # Step-by-step instructions
            }
            return jsonify(directions_data)
        else:
            return jsonify({'status': 'error', 'error': 'Unable to fetch directions'}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
