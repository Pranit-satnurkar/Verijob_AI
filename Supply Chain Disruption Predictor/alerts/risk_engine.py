
import random
from datetime import datetime
import sqlite3
import os

DB_NAME = "supply_chain.db"

class RiskEngine:
    def __init__(self):
        pass

    
    def run_analysis(self):
        """Run analysis for all materials in database"""
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        # Get materials
        cur.execute("SELECT material_id, material_name FROM materials")
        materials = cur.fetchall()
        
        locations = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai']
        
        print(f"Running risk analysis for {len(materials)} materials across {len(locations)} locations...")
        
        count = 0
        for mat in materials:
            for loc in locations:
                risk = self.calculate_material_risk(mat['material_name'], loc)
                
                # Save to DB
                try:
                    cur.execute("""
                    INSERT OR REPLACE INTO risk_scores 
                    (material_id, location, computed_at, supply_risk, demand_risk, logistics_risk, 
                     geopolitical_risk, weather_risk, price_risk, composite_risk_score, risk_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        mat['material_id'],
                        loc,
                        datetime.now().isoformat(),
                        risk['components']['supply'],
                        risk['components']['demand'],
                        risk['components']['logistics'],
                        risk['components']['geopolitical'],
                        risk['components']['weather'],
                        risk['components']['price'],
                        risk['composite_score'],
                        risk['risk_level']
                    ))
                    count += 1
                except Exception as e:
                    print(f"Error saving risk score: {e}")
        
        conn.commit()
        conn.close()
        print(f"✅ Updated {count} risk scores in database.")

    def calculate_material_risk(self, material_name, location):
        """
        Calculate the composite risk score for a material in a location.
        Returns a dictionary with component scores and total score.
        """
        
        # Mocking data retrieval (would query news_articles, material_prices tables here)
        supply_risk = self._get_supply_risk(material_name, location)
        demand_risk = self._get_demand_risk(material_name, location)
        logistics_risk = self._get_logistics_risk(material_name, location)
        weather_risk = self._get_weather_risk(location)
        price_risk = self._get_price_risk(material_name)
        geopolitical_risk = self._get_geopolitical_risk(material_name)
        
        # Weighted formula
        weights = {
            'supply': 0.25,
            'demand': 0.15,
            'logistics': 0.20,
            'geopolitical': 0.15,
            'weather': 0.10,
            'price': 0.15
        }
        
        composite_score = (
            supply_risk * weights['supply'] +
            demand_risk * weights['demand'] +
            logistics_risk * weights['logistics'] +
            geopolitical_risk * weights['geopolitical'] +
            weather_risk * weights['weather'] +
            price_risk * weights['price']
        )
        
        risk_level = self._get_risk_level(composite_score)
        
        return {
            'material': material_name,
            'location': location,
            'composite_score': round(composite_score, 1),
            'risk_level': risk_level,
            'components': {
                'supply': supply_risk,
                'demand': demand_risk,
                'logistics': logistics_risk,
                'geopolitical': geopolitical_risk,
                'weather': weather_risk,
                'price': price_risk
            }
        }


    def _get_risk_level(self, score):
        if score >= 80: return "Critical"
        if score >= 60: return "High"
        if score >= 40: return "Medium"
        return "Low"

    # --- Mock Helper Methods ---
    
    def _get_supply_risk(self, material, location):
        # Mock logic: Steel in Mumbai has high risk
        if "steel" in material.lower() and "mumbai" in location.lower():
            return 85
        return random.randint(20, 60)

    def _get_demand_risk(self, material, location):
        return random.randint(30, 70)

    def _get_logistics_risk(self, material, location):
        return random.randint(10, 50)

    def _get_weather_risk(self, location):
        # Mock: check if monsoon season (June-Sept)
        month = datetime.now().month
        if 6 <= month <= 9 and location.lower() in ['mumbai', 'kerala']:
            return 80
        return 10

    def _get_price_risk(self, material):
        return random.randint(20, 90)

    def _get_geopolitical_risk(self, material):
        if "steel" in material.lower():
            return 70 # Global trade issues
        return 20

if __name__ == "__main__":
    engine = RiskEngine()
    engine.run_analysis()
