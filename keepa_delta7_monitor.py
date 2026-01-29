#!/usr/bin/env python3
"""
Keepa Delta 7 Monitoring Script for B07WDRQ4J7 (Air Wick Candles)
Addresses the Keepa delta 7 warnings we identified in our analysis
"""

import json
import time
import requests
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class KeepaMonitor:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://api.keepa.com"
        self.asin = "B07WDRQ4J7"
        self.product_name = "Air Wick Reed Diffuser Mulled Wine"

    def get_product_data(self, asin):
        """Fetch current Keepa data for ASIN"""
        if not self.api_key:
            logger.warning("No Keepa API key provided - using demo data")
            return self._get_demo_data()

        try:
            url = f"{self.base_url}/product"
            params = {
                "key": self.api_key,
                "domain": 1,  # US
                "asin": asin,
                "stats": 7,  # 7 days of stats
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Keepa data: {e}")
            return None

    def _get_demo_data(self):
        """Demo data based on our analysis findings"""
        return {
            "asin": self.asin,
            "title": self.product_name,
            "current_price": 46.00,
            "avg_price_7d": 44.50,
            "avg_price_30d": 42.30,
            "price_history": [
                {"date": "2026-01-10", "price": 42.00},
                {"date": "2026-01-11", "price": 43.50},
                {"date": "2026-01-12", "price": 44.00},
                {"date": "2026-01-13", "price": 45.00},
                {"date": "2026-01-14", "price": 46.00},
                {"date": "2026-01-15", "price": 46.00},
                {"date": "2026-01-16", "price": 46.00},
            ],
            "delta_7": 3.8,  # 7-day price change percentage
            "delta_30": 8.9,  # 30-day price change percentage
            "volatility": "medium",
            "trend": "increasing",
        }

    def analyze_delta_7_warning(self, data):
        """Analyze the delta 7 warning we identified"""
        if not data:
            return {"status": "error", "message": "No data available"}

        current_price = data.get("current_price", 0)
        avg_7d = data.get("avg_price_7d", current_price)
        delta_7 = data.get("delta_7", 0)

        analysis = {
            "asin": self.asin,
            "product": self.product_name,
            "current_price": current_price,
            "avg_7d_price": avg_7d,
            "delta_7_percentage": delta_7,
            "status": "normal",
            "recommendations": [],
        }

        # Delta 7 Warning Criteria (from our analysis)
        if delta_7 > 5.0:
            analysis["status"] = "warning"
            analysis["recommendations"].append("Price volatility detected - monitor closely")
            analysis["recommendations"].append("Consider adjusting selling price to maintain ROI")

        elif delta_7 < -3.0:
            analysis["status"] = "opportunity"
            analysis["recommendations"].append("Price dropping - potential buying opportunity")
            analysis["recommendations"].append("Monitor for further decreases before purchasing")

        else:
            analysis["recommendations"].append("Price stable - maintain current strategy")

        # ROI Impact Analysis
        supplier_price = 13.43  # From our analysis
        current_roi = ((current_price - supplier_price) / supplier_price) * 100

        analysis["roi_at_current_price"] = round(current_roi, 1)
        analysis["roi_impact"] = self._calculate_roi_impact(delta_7, current_price, supplier_price)

        return analysis

    def _calculate_roi_impact(self, delta_7, current_price, supplier_price):
        """Calculate how delta 7 affects our ROI"""
        price_change = current_price * (delta_7 / 100)
        new_price = current_price + price_change
        new_roi = ((new_price - supplier_price) / supplier_price) * 100

        return {
            "current_roi": round(((current_price - supplier_price) / supplier_price) * 100, 1),
            "projected_roi": round(new_roi, 1),
            "roi_change": round(
                new_roi - ((current_price - supplier_price) / supplier_price) * 100, 1
            ),
        }

    def generate_monitoring_report(self):
        """Generate comprehensive monitoring report"""
        logger.info(f"Monitoring Keepa data for {self.asin}")

        data = self.get_product_data(self.asin)
        analysis = self.analyze_delta_7_warning(data)

        report = {
            "timestamp": datetime.now().isoformat(),
            "asin": self.asin,
            "product": self.product_name,
            "analysis": analysis,
            "next_check": (datetime.now() + timedelta(hours=24)).isoformat(),
        }

        # Save report
        self._save_report(report)

        return report

    def _save_report(self, report):
        """Save monitoring report to file"""
        filename = f"keepa_monitor_{self.asin}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(filename, "w") as f:
                json.dump(report, f, indent=2)
            logger.info(f"Report saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")


def main():
    """Main monitoring function"""
    monitor = KeepaMonitor(api_key=None)  # Set your Keepa API key here

    logger.info("=== Keepa Delta 7 Monitoring for B07WDRQ4J7 ===")

    report = monitor.generate_monitoring_report()

    # Print summary
    print(f"\n🕯️  Product: {report['product']}")
    print(f"📊 ASIN: {report['asin']}")
    print(f"⏰ Timestamp: {report['timestamp']}")
    print(f"🚨 Status: {report['analysis']['status'].upper()}")

    if report["analysis"]["status"] == "warning":
        print(f"⚠️  Delta 7: {report['analysis']['delta_7_percentage']}%")
        print(f"💰 Current ROI: {report['analysis']['roi_at_current_price']}%")
        print("\n📋 Recommendations:")
        for rec in report["analysis"]["recommendations"]:
            print(f"  • {rec}")

    elif report["analysis"]["status"] == "opportunity":
        print(f"🎯 Delta 7: {report['analysis']['delta_7_percentage']}%")
        print(f"💰 Projected ROI: {report['analysis']['roi_impact']['projected_roi']}%")
        print("\n📋 Recommendations:")
        for rec in report["analysis"]["recommendations"]:
            print(f"  • {rec}")

    else:
        print(f"✅ Delta 7: {report['analysis']['delta_7_percentage']}%")
        print(f"💰 ROI: {report['analysis']['roi_at_current_price']}%")
        print("\n📋 Recommendations:")
        for rec in report["analysis"]["recommendations"]:
            print(f"  • {rec}")

    print(f"\n🔍 Next check: {report['next_check']}")


if __name__ == "__main__":
    main()
