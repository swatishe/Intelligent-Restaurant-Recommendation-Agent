"""
Restaurant Recommendation AI Agent
Author: AI Course Project
Date: 2025

Demonstrates: Search algorithms, Constraint reasoning, and Deterministic Planning

Usage:
    python restaurant_agent.py
    
Or import in another script:
    from restaurant_agent import RestaurantAgent
    agent = RestaurantAgent()
    results = agent.search("Turkish restaurant in Downtown Baltimore")
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# PART 1: STATE DEFINITIONS AND DATA STRUCTURES
# ============================================================================

class SearchState(Enum):
    """Agent state during search process"""
    INITIAL = "initial"
    NLP_PARSING = "nlp_parsing"
    CONSTRAINT_EXTRACTION = "constraint_extraction"
    DATA_RETRIEVAL = "data_retrieval"
    FILTERING = "filtering"
    RANKING = "ranking"
    COMPLETE = "complete"


@dataclass
class Constraints:
    """Extracted constraints from user query"""
    cuisine: str = None
    location: str = None
    price_max: float = None
    party_size: int = None
    day: str = None
    time: str = None
    special_requests: List[str] = field(default_factory=list)
    
    def __str__(self):
        return f"Cuisine={self.cuisine}, Location={self.location}, " \
               f"Price≤${self.price_max}, Party={self.party_size}, " \
               f"Time={self.day} {self.time}, Special={self.special_requests}"


@dataclass
class Restaurant:
    """Restaurant entity"""
    name: str
    cuisine: str
    location: str
    price_range: str
    avg_price_per_person: float
    rating: float
    availability: Dict[str, List[str]]
    has_window_seating: bool
    window_view: List[str]
    distance_from_center: float  # miles from downtown center
    
    def matches_constraints(self, constraints: Constraints) -> Tuple[bool, List[str]]:
        """Check if restaurant matches constraints"""
        matches = []
        reasons = []
        
        # Cuisine match
        if constraints.cuisine:
            if self.cuisine.lower() == constraints.cuisine.lower():
                matches.append(True)
                reasons.append(f"✓ Cuisine: {self.cuisine}")
            else:
                matches.append(False)
                reasons.append(f"✗ Cuisine: {self.cuisine} (need {constraints.cuisine})")
        
        # Location match (Downtown Baltimore)
        if constraints.location:
            if "downtown" in self.location.lower() and "baltimore" in self.location.lower():
                matches.append(True)
                reasons.append(f"✓ Location: {self.location}")
            else:
                matches.append(False)
                reasons.append(f"✗ Location: {self.location}")
        
        # Price constraint
        if constraints.price_max and constraints.party_size:
            total_cost = self.avg_price_per_person * constraints.party_size
            if total_cost <= constraints.price_max:
                matches.append(True)
                reasons.append(f"✓ Price: ${total_cost:.2f} for {constraints.party_size} ≤ ${constraints.price_max}")
            else:
                matches.append(False)
                reasons.append(f"✗ Price: ${total_cost:.2f} for {constraints.party_size} > ${constraints.price_max}")
        
        # Availability
        if constraints.day and constraints.time:
            day_avail = self.availability.get(constraints.day, [])
            if constraints.time in day_avail:
                matches.append(True)
                reasons.append(f"✓ Available: {constraints.day} at {constraints.time}")
            else:
                matches.append(False)
                reasons.append(f"✗ Not available: {constraints.day} at {constraints.time}")
        
        # Window seating with view
        if "window" in str(constraints.special_requests).lower():
            if self.has_window_seating and self.window_view:
                matches.append(True)
                reasons.append(f"✓ Window seating: View of {', '.join(self.window_view)}")
            else:
                matches.append(False)
                reasons.append(f"✗ No window seating or view available")
        
        return all(matches), reasons


# ============================================================================
# PART 2: NLP PARSER
# ============================================================================

class NLPParser:
    """Simple rule-based NLP parser for extracting constraints"""
    
    CUISINE_KEYWORDS = ['turkish', 'italian', 'chinese', 'mexican', 'indian', 'french', 'japanese']
    LOCATION_PATTERNS = [
        r'in\s+(downtown\s+\w+(?:\s+\w+)?)',
        r'at\s+(downtown\s+\w+(?:\s+\w+)?)',
    ]
    PRICE_PATTERN = r'under\s+\$?(\d+)'
    PARTY_PATTERN = r'for\s+(\w+|\d+)\s+people?'
    DAY_PATTERN = r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)'
    TIME_PATTERN = r'at\s+(\d{1,2}:\d{2}\s*(?:am|pm)?)'
    
    def __init__(self):
        self.logger = []
    
    def parse(self, query: str) -> Constraints:
        """Parse natural language query into constraints"""
        self.logger.append(f"[NLP] Parsing query: '{query}'")
        query_lower = query.lower()
        constraints = Constraints()
        
        # Extract cuisine
        for cuisine in self.CUISINE_KEYWORDS:
            if cuisine in query_lower:
                constraints.cuisine = cuisine.capitalize()
                self.logger.append(f"[NLP] Extracted cuisine: {constraints.cuisine}")
                break
        
        # Extract location
        for pattern in self.LOCATION_PATTERNS:
            match = re.search(pattern, query_lower)
            if match:
                constraints.location = match.group(1).title()
                self.logger.append(f"[NLP] Extracted location: {constraints.location}")
                break
        
        # Extract price
        match = re.search(self.PRICE_PATTERN, query_lower)
        if match:
            constraints.price_max = float(match.group(1))
            self.logger.append(f"[NLP] Extracted price max: ${constraints.price_max}")
        
        # Extract party size
        match = re.search(self.PARTY_PATTERN, query_lower)
        if match:
            num_str = match.group(1)
            if num_str.isdigit():
                constraints.party_size = int(num_str)
            else:
                # Convert word to number
                word_to_num = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}
                constraints.party_size = word_to_num.get(num_str, 2)
            self.logger.append(f"[NLP] Extracted party size: {constraints.party_size}")
        
        # Extract day
        match = re.search(self.DAY_PATTERN, query_lower)
        if match:
            constraints.day = match.group(1).capitalize()
            self.logger.append(f"[NLP] Extracted day: {constraints.day}")
        
        # Extract time
        match = re.search(self.TIME_PATTERN, query_lower)
        if match:
            constraints.time = match.group(1)
            self.logger.append(f"[NLP] Extracted time: {constraints.time}")
        
        # Extract special requests
        if 'window' in query_lower:
            constraints.special_requests.append('window seating')
            self.logger.append(f"[NLP] Extracted special request: window seating")
        if 'garden' in query_lower or 'street' in query_lower:
            view = []
            if 'garden' in query_lower:
                view.append('garden')
            if 'street' in query_lower:
                view.append('street')
            constraints.special_requests.append(f"view: {', '.join(view)}")
            self.logger.append(f"[NLP] Extracted view preference: {', '.join(view)}")
        
        return constraints


# ============================================================================
# PART 3: MOCK RESTAURANT DATABASE
# ============================================================================

def create_mock_database() -> List[Restaurant]:
    """Create mock restaurant database (simulates Yelp API)"""
    return [
        Restaurant(
            name="Istanbul Grill",
            cuisine="Turkish",
            location="Downtown Baltimore, MD",
            price_range="$$",
            avg_price_per_person=28.0,
            rating=4.5,
            availability={
                "Thursday": ["6:00 pm", "6:30 pm", "7:00 pm", "7:30 pm", "8:00 pm"],
                "Friday": ["6:00 pm", "7:00 pm", "8:00 pm"]
            },
            has_window_seating=True,
            window_view=["street"],
            distance_from_center=0.3
        ),
        Restaurant(
            name="Anatolian Kitchen",
            cuisine="Turkish",
            location="Downtown Baltimore, MD",
            price_range="$$",
            avg_price_per_person=32.0,
            rating=4.7,
            availability={
                "Thursday": ["5:30 pm", "6:00 pm", "7:30 pm", "8:30 pm"],
                "Friday": ["6:00 pm", "7:00 pm"]
            },
            has_window_seating=True,
            window_view=["garden", "street"],
            distance_from_center=0.5
        ),
        Restaurant(
            name="Bosphorus Cafe",
            cuisine="Turkish",
            location="Downtown Baltimore, MD",
            price_range="$",
            avg_price_per_person=22.0,
            rating=4.2,
            availability={
                "Thursday": ["6:00 pm", "7:00 pm", "8:00 pm"],
                "Friday": ["6:30 pm", "7:30 pm"]
            },
            has_window_seating=False,
            window_view=[],
            distance_from_center=0.8
        ),
        Restaurant(
            name="Sultan's Table",
            cuisine="Turkish",
            location="Downtown Baltimore, MD",
            price_range="$$$",
            avg_price_per_person=45.0,
            rating=4.8,
            availability={
                "Thursday": ["6:00 pm", "6:30 pm", "7:30 pm"],
                "Friday": ["7:00 pm", "8:00 pm"]
            },
            has_window_seating=True,
            window_view=["garden"],
            distance_from_center=0.2
        ),
        Restaurant(
            name="Mediterranean Breeze",
            cuisine="Mediterranean",
            location="Downtown Baltimore, MD",
            price_range="$$",
            avg_price_per_person=30.0,
            rating=4.4,
            availability={
                "Thursday": ["7:30 pm", "8:00 pm"],
                "Friday": ["6:00 pm", "7:00 pm"]
            },
            has_window_seating=True,
            window_view=["street"],
            distance_from_center=0.4
        ),
        Restaurant(
            name="Turkish Delight",
            cuisine="Turkish",
            location="Harbor East, Baltimore, MD",
            price_range="$$",
            avg_price_per_person=26.0,
            rating=4.3,
            availability={
                "Thursday": ["7:30 pm", "8:00 pm"],
                "Friday": ["6:00 pm", "7:00 pm"]
            },
            has_window_seating=True,
            window_view=["harbor"],
            distance_from_center=1.2
        ),
    ]


# ============================================================================
# PART 4: SEARCH AND FILTERING AGENT
# ============================================================================

class RestaurantAgent:
    """Goal-based agent with utility reasoning for restaurant recommendations"""
    
    def __init__(self):
        self.state = SearchState.INITIAL
        self.parser = NLPParser()
        self.database = create_mock_database()
        self.log = []
        self.constraints = None
        self.candidates = []
        self.filtered_results = []
        self.ranked_results = []
    
    def log_event(self, message: str, level: str = "INFO"):
        """Log agent decision/event"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.log.append(log_entry)
        print(log_entry)
    
    def transition_state(self, new_state: SearchState):
        """Transition to new state with logging"""
        self.log_event(f"State transition: {self.state.value} → {new_state.value}", "STATE")
        self.state = new_state
    
    def search(self, query: str) -> List[Tuple[Restaurant, float, List[str]]]:
        """Main search pipeline"""
        self.log_event("="*80, "SYSTEM")
        self.log_event("RESTAURANT RECOMMENDATION AGENT STARTED", "SYSTEM")
        self.log_event("="*80, "SYSTEM")
        
        # Step 1: NLP Parsing
        self.transition_state(SearchState.NLP_PARSING)
        self.constraints = self.parser.parse(query)
        self.log.extend(self.parser.logger)
        
        # Step 2: Constraint extraction summary
        self.transition_state(SearchState.CONSTRAINT_EXTRACTION)
        self.log_event(f"Extracted constraints: {self.constraints}", "CONSTRAINT")
        
        # Step 3: Data retrieval
        self.transition_state(SearchState.DATA_RETRIEVAL)
        self.log_event(f"Retrieved {len(self.database)} restaurants from database", "DATA")
        self.candidates = self.database.copy()
        
        # Step 4: Filtering
        self.transition_state(SearchState.FILTERING)
        self.log_event("Starting constraint satisfaction filtering...", "FILTER")
        self.filtered_results = []
        
        for restaurant in self.candidates:
            matches, reasons = restaurant.matches_constraints(self.constraints)
            self.log_event(f"\nEvaluating: {restaurant.name}", "FILTER")
            for reason in reasons:
                self.log_event(f"  {reason}", "FILTER")
            
            if matches:
                self.filtered_results.append(restaurant)
                self.log_event(f"  ✓ PASS: All constraints satisfied", "FILTER")
            else:
                self.log_event(f"  ✗ FAIL: Some constraints not met", "FILTER")
        
        self.log_event(f"\nFiltering complete: {len(self.filtered_results)}/{len(self.candidates)} restaurants passed", "FILTER")
        
        # Step 5: Ranking with utility function
        self.transition_state(SearchState.RANKING)
        self.log_event("Applying utility-based ranking...", "RANK")
        self.ranked_results = self._rank_results()
        
        # Step 6: Complete
        self.transition_state(SearchState.COMPLETE)
        self.log_event("="*80, "SYSTEM")
        self.log_event("SEARCH COMPLETE", "SYSTEM")
        self.log_event("="*80, "SYSTEM")
        
        return self.ranked_results
    
    def _rank_results(self) -> List[Tuple[Restaurant, float, List[str]]]:
        """Rank filtered results using utility function"""
        ranked = []
        
        for restaurant in self.filtered_results:
            utility_score = self._calculate_utility(restaurant)
            explanation = self._generate_ranking_explanation(restaurant, utility_score)
            ranked.append((restaurant, utility_score, explanation))
            
            self.log_event(f"\n{restaurant.name}:", "RANK")
            self.log_event(f"  Total Utility Score: {utility_score:.2f}", "RANK")
            for exp in explanation:
                self.log_event(f"  {exp}", "RANK")
        
        # Sort by utility score (descending)
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked
    
    def _calculate_utility(self, restaurant: Restaurant) -> float:
        """Calculate utility score for ranking"""
        score = 0.0
        
        # Rating component (0-5 stars → 0-30 points)
        score += restaurant.rating * 6
        
        # Price efficiency (closer to budget max is better)
        if self.constraints.price_max and self.constraints.party_size:
            total_cost = restaurant.avg_price_per_person * self.constraints.party_size
            price_efficiency = (self.constraints.price_max - total_cost) / self.constraints.price_max
            score += price_efficiency * 20
        
        # Distance (closer to downtown center is better)
        distance_score = max(0, 20 - restaurant.distance_from_center * 10)
        score += distance_score
        
        # Window view bonus
        if restaurant.has_window_seating:
            score += 15
            # Extra bonus for preferred views
            if 'garden' in restaurant.window_view:
                score += 10
            if 'street' in restaurant.window_view:
                score += 5
        
        return round(score, 2)
    
    def _generate_ranking_explanation(self, restaurant: Restaurant, utility: float) -> List[str]:
        """Generate human-readable ranking explanation"""
        explanations = []
        explanations.append(f"Rating: {restaurant.rating}⭐ (contributes {restaurant.rating * 6:.1f} points)")
        
        if self.constraints.price_max and self.constraints.party_size:
            total_cost = restaurant.avg_price_per_person * self.constraints.party_size
            savings = self.constraints.price_max - total_cost
            explanations.append(f"Price: ${total_cost:.2f} for {self.constraints.party_size} (${savings:.2f} under budget)")
        
        explanations.append(f"Distance: {restaurant.distance_from_center} miles from downtown center")
        
        if restaurant.has_window_seating:
            explanations.append(f"Window view: {', '.join(restaurant.window_view)}")
        
        return explanations
    
    def display_results(self):
        """Display final ranked results"""
        print("\n" + "="*80)
        print("FINAL RANKED RECOMMENDATIONS")
        print("="*80)
        
        if not self.ranked_results:
            print("\n No restaurants found matching all criteria.")
            return
        
        for idx, (restaurant, utility, explanations) in enumerate(self.ranked_results, 1):
            print(f"\n{'='*80}")
            print(f"RANK #{idx} - {restaurant.name} (Utility Score: {utility:.2f})")
            print(f"{'='*80}")
            
            # Match summary
            print("\n📋 CONSTRAINT MATCH SUMMARY:")
            _, reasons = restaurant.matches_constraints(self.constraints)
            for reason in reasons:
                print(f"  {reason}")
            
            # Additional details
            print(f"\n Location: {restaurant.location}")
            print(f" Cuisine: {restaurant.cuisine}")
            print(f" Rating: {restaurant.rating}/5.0")
            total_cost = restaurant.avg_price_per_person * self.constraints.party_size
            print(f" Price: ${restaurant.avg_price_per_person}/person (${total_cost:.2f} for {self.constraints.party_size})")
            print(f" Window Seating: {'Yes' if restaurant.has_window_seating else 'No'}")
            if restaurant.window_view:
                print(f" View: {', '.join(restaurant.window_view).title()}")
            print(f" Available: {self.constraints.day} at {self.constraints.time}")
            
            print(f"\n💡 RANKING EXPLANATION:")
            for exp in explanations:
                print(f"  • {exp}")
    
    def save_logs(self, filename: str = "agent_log.txt"):
        """Save logs to file"""
        with open(filename, 'w') as f:
            f.write('\n'.join(self.log))
        print(f"\n Detailed logs saved to '{filename}'")


# ============================================================================
# PART 5: MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    # The user query
    query = """Find a Turkish restaurant in Downtown Baltimore, MD for two people 
    to have dinner under $65 on Thursday night at 7:30 pm with a table for two 
    near a window with a view of the garden or the street."""
    
    print("\n" + "="*80)
    print("QUERY:")
    print("="*80)
    print(query)
    print()
    
    # Create and run agent
    agent = RestaurantAgent()
    results = agent.search(query)
    
    # Display results
    agent.display_results()
    
    # Save logs to file
    agent.save_logs()


if __name__ == "__main__":
    main()