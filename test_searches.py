"""
Test searches for Restaurant Agent
This file demonstrates various ways to use the agent
"""

from restaurant_agent import RestaurantAgent

def test_basic_search():
    """Test 1: Basic search with minimal constraints"""
    print("\n" + "="*80)
    print("TEST 1: BASIC SEARCH")
    print("="*80)
    
    agent = RestaurantAgent()
    query = "Turkish restaurant in Downtown Baltimore"
    results = agent.search(query)
    agent.display_results()
    print(f"\nFound {len(results)} restaurants")


def test_price_constraint():
    """Test 2: Search with price constraint"""
    print("\n" + "="*80)
    print("TEST 2: PRICE CONSTRAINT")
    print("="*80)
    
    agent = RestaurantAgent()
    query = "Turkish restaurant for 2 people under $50"
    results = agent.search(query)
    agent.display_results()


def test_full_specification():
    """Test 3: Full specification with all constraints"""
    print("\n" + "="*80)
    print("TEST 3: FULL SPECIFICATION")
    print("="*80)
    
    agent = RestaurantAgent()
    query = """Find a Turkish restaurant in Downtown Baltimore, MD for two people 
    to have dinner under $65 on Thursday night at 7:30 pm with a table for two 
    near a window with a view of the garden or the street."""
    results = agent.search(query)
    agent.display_results()
    agent.save_logs("full_search_log.txt")


def test_programmatic_access():
    """Test 4: Access results programmatically"""
    print("\n" + "="*80)
    print("TEST 4: PROGRAMMATIC ACCESS")
    print("="*80)
    
    agent = RestaurantAgent()
    query = "Turkish restaurant in Downtown Baltimore for 2 under $65"
    results = agent.search(query)
    
    print("\n📊 PROGRAMMATIC RESULTS ACCESS:")
    print(f"Total matches: {len(results)}\n")
    
    for rank, (restaurant, utility_score, explanations) in enumerate(results, 1):
        print(f"Rank {rank}: {restaurant.name}")
        print(f"  Utility Score: {utility_score}")
        print(f"  Cuisine: {restaurant.cuisine}")
        print(f"  Location: {restaurant.location}")
        print(f"  Rating: {restaurant.rating} ⭐")
        print(f"  Price: ${restaurant.avg_price_per_person}/person")
        print(f"  Window Seating: {restaurant.has_window_seating}")
        if restaurant.window_view:
            print(f"  Views: {', '.join(restaurant.window_view)}")
        print()


def test_no_matches():
    """Test 5: Query with no matches"""
    print("\n" + "="*80)
    print("TEST 5: NO MATCHES SCENARIO")
    print("="*80)
    
    agent = RestaurantAgent()
    query = "Turkish restaurant for 2 people under $30"
    results = agent.search(query)
    agent.display_results()
    
    if not results:
        print("\n💡 TIP: Try relaxing constraints (increase budget, change time, etc.)")


def test_different_cuisine():
    """Test 6: Different cuisine (should return no Turkish restaurants)"""
    print("\n" + "="*80)
    print("TEST 6: DIFFERENT CUISINE")
    print("="*80)
    
    agent = RestaurantAgent()
    query = "Italian restaurant in Downtown Baltimore"
    results = agent.search(query)
    agent.display_results()


def compare_utility_scores():
    """Test 7: Compare utility scores across restaurants"""
    print("\n" + "="*80)
    print("TEST 7: UTILITY SCORE COMPARISON")
    print("="*80)
    
    agent = RestaurantAgent()
    query = "Turkish restaurant in Downtown Baltimore for 2 under $70"
    results = agent.search(query)
    
    print("\n UTILITY SCORE COMPARISON:")
    print(f"{'Restaurant':<25} {'Utility':<10} {'Rating':<10} {'Price':<10} {'Distance':<10}")
    print("-" * 75)
    
    for restaurant, utility_score, explanations in results:
        price = f"${restaurant.avg_price_per_person}"
        distance = f"{restaurant.distance_from_center}mi"
        print(f"{restaurant.name:<25} {utility_score:<10.2f} {restaurant.rating:<10} {price:<10} {distance:<10}")


def interactive_search():
    """Test 8: Interactive search with user input"""
    print("\n" + "="*80)
    print("TEST 8: INTERACTIVE SEARCH")
    print("="*80)
    
    print("\nEnter your restaurant preferences:")
    print("Example: Turkish restaurant in Downtown Baltimore for 2 under $65 on Thursday at 7:30 pm\n")
    
    try:
        query = input("Your query: ")
        if query.strip():
            agent = RestaurantAgent()
            results = agent.search(query)
            agent.display_results()
        else:
            print("No query entered. Using default...")
            agent = RestaurantAgent()
            results = agent.search("Turkish restaurant in Downtown Baltimore")
            agent.display_results()
    except KeyboardInterrupt:
        print("\n\nSearch cancelled.")


def batch_searches():
    """Test 9: Multiple searches in batch"""
    print("\n" + "="*80)
    print("TEST 9: BATCH SEARCHES")
    print("="*80)
    
    queries = [
        "Turkish restaurant for 2 under $60",
        "Turkish restaurant for 2 under $70",
        "Turkish restaurant for 4 under $100",
    ]
    
    all_results = {}
    
    for query in queries:
        print(f"\n{'='*80}")
        print(f"Query: {query}")
        print('='*80)
        
        agent = RestaurantAgent()
        results = agent.search(query)
        all_results[query] = results
        
        print(f"\nFound {len(results)} restaurants")
        if results:
            print(f"Top recommendation: {results[0][0].name} (Utility: {results[0][1]:.2f})")
    
    # Summary
    print("\n" + "="*80)
    print("BATCH SEARCH SUMMARY")
    print("="*80)
    for query, results in all_results.items():
        print(f"\n'{query}'")
        print(f"  Results: {len(results)}")
        if results:
            print(f"  Top: {results[0][0].name} ({results[0][1]:.2f} pts)")


def export_results_json():
    """Test 10: Export results to JSON format"""
    print("\n" + "="*80)
    print("TEST 10: EXPORT TO JSON")
    print("="*80)
    
    import json
    
    agent = RestaurantAgent()
    query = "Turkish restaurant in Downtown Baltimore for 2 under $65"
    results = agent.search(query)
    
    # Convert results to JSON-serializable format
    json_results = []
    for restaurant, utility_score, explanations in results:
        json_results.append({
            "name": restaurant.name,
            "cuisine": restaurant.cuisine,
            "location": restaurant.location,
            "rating": restaurant.rating,
            "price_per_person": restaurant.avg_price_per_person,
            "price_range": restaurant.price_range,
            "utility_score": utility_score,
            "has_window_seating": restaurant.has_window_seating,
            "window_view": restaurant.window_view,
            "distance_from_center": restaurant.distance_from_center,
            "explanations": explanations
        })
    
    # Save to file
    with open('results.json', 'w') as f:
        json.dump({
            "query": query,
            "total_results": len(json_results),
            "restaurants": json_results
        }, f, indent=2)
    
    print(f"\n Results exported to 'results.json'")
    print(f"Total restaurants: {len(json_results)}")


def main():
    """Run all tests or specific tests"""
    print("\n" + "="*80)
    print("RESTAURANT AGENT TEST SUITE")
    print("="*80)
    
    # Uncomment the tests you want to run:
    
    # test_basic_search()
    # test_price_constraint()
    test_full_specification()
    # test_programmatic_access()
    # test_no_matches()
    # test_different_cuisine()
    # compare_utility_scores()
    # interactive_search()
    # batch_searches()
    # export_results_json()
    
    # Or run all tests:
    # run_all_tests()


def run_all_tests():
    """Run all tests sequentially"""
    tests = [
        test_basic_search,
        test_price_constraint,
        test_full_specification,
        test_programmatic_access,
        test_no_matches,
        test_different_cuisine,
        compare_utility_scores,
        batch_searches,
        export_results_json
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"\n\n{'#'*80}")
        print(f"# Running Test {i}/{len(tests)}: {test.__name__}")
        print(f"{'#'*80}")
        try:
            test()
        except Exception as e:
            print(f" Test failed: {e}")
        
        input("\nPress Enter to continue to next test...")


if __name__ == "__main__":
    main()