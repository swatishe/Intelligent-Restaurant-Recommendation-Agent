"""
Flask Web Application for Restaurant Recommendation Agent
Run this to get a web UI for your agent

Installation:
    pip install flask

Usage:
    python app.py
    Then open browser to: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify
from restaurant_agent import RestaurantAgent, create_mock_database
import json

app = Flask(__name__)


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    """Handle search requests from the web UI"""
    try:
        # Get query from request
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({
                'error': 'No query provided',
                'results': []
            }), 400
        
        # Create agent and search
        agent = RestaurantAgent()
        results = agent.search(query)
        
        # Convert results to JSON-serializable format
        json_results = []
        for restaurant, utility_score, explanations in results:
            # Get constraint match details
            _, reasons = restaurant.matches_constraints(agent.constraints)
            
            json_results.append({
                'name': restaurant.name,
                'cuisine': restaurant.cuisine,
                'location': restaurant.location,
                'rating': restaurant.rating,
                'price_per_person': restaurant.avg_price_per_person,
                'price_range': restaurant.price_range,
                'utility_score': utility_score,
                'has_window_seating': restaurant.has_window_seating,
                'window_view': restaurant.window_view,
                'distance_from_center': restaurant.distance_from_center,
                'availability': restaurant.availability,
                'explanations': explanations,
                'constraint_matches': reasons
            })
        
        # Return results with logs
        return jsonify({
            'success': True,
            'query': query,
            'constraints': str(agent.constraints),
            'total_results': len(json_results),
            'results': json_results,
            'logs': agent.log
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'results': []
        }), 500


@app.route('/api/restaurants')
def get_restaurants():
    """Get all restaurants in database"""
    restaurants = create_mock_database()
    
    restaurant_list = []
    for r in restaurants:
        restaurant_list.append({
            'name': r.name,
            'cuisine': r.cuisine,
            'location': r.location,
            'rating': r.rating,
            'price_per_person': r.avg_price_per_person,
            'has_window_seating': r.has_window_seating,
            'window_view': r.window_view
        })
    
    return jsonify({
        'total': len(restaurant_list),
        'restaurants': restaurant_list
    })


if __name__ == '__main__':
    print("\n" + "="*80)
    print(" Restaurant Recommendation Agent - Web Interface")
    print("="*80)
    print("\nServer starting...")
    print(" Open your browser to: http://localhost:5001")
    print(" Press CTRL+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5001)