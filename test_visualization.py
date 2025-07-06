#!/usr/bin/env python3
"""
Script test untuk visualisasi jaringan
"""

import sys
import os
import json

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.network_analysis_service import NetworkAnalysisService
from services.twitter_service import TwitterService

def test_network_visualization():
    """Test visualisasi jaringan dengan data dummy"""
    
    print("🔄 Testing Network Visualization...")
    
    # Initialize services
    twitter_service = TwitterService(use_real_api=False)
    network_service = NetworkAnalysisService()
    
    # Get dummy network data
    dummy_tweet_id = "123456789"
    network_data = twitter_service.get_tweet_network_data(dummy_tweet_id)
    
    print(f"📊 Network data generated:")
    print(f"  - Nodes: {len(network_data.get('nodes', []))}")
    print(f"  - Edges: {len(network_data.get('edges', []))}")
    print(f"  - Total interactions: {network_data.get('total_interactions', 0)}")
    
    # Analyze network
    analysis_result = network_service.analyze_network(network_data)
    
    print(f"🔍 Network analysis completed:")
    print(f"  - Network metrics: {analysis_result.get('network_metrics', {})}")
    print(f"  - Influential nodes: {len(analysis_result.get('influential_nodes', []))}")
    print(f"  - Communities: {len(analysis_result.get('communities', {}).get('communities', []))}")
    
    # Create visualizations
    print("🎨 Creating visualizations...")
    
    # Create network visualization
    try:
        viz_path = network_service.create_network_visualization()
        print(f"✅ Network visualization created: {viz_path}")
        
        if os.path.exists(viz_path):
            print(f"✅ Visualization file exists: {os.path.getsize(viz_path)} bytes")
        else:
            print(f"❌ Visualization file not found!")
            
    except Exception as e:
        print(f"❌ Error creating network visualization: {e}")
    
    # Create influence chart
    try:
        influential_nodes = analysis_result.get('influential_nodes', [])
        if influential_nodes:
            chart_path = network_service.create_influence_chart(influential_nodes)
            print(f"✅ Influence chart created: {chart_path}")
            
            if os.path.exists(chart_path):
                print(f"✅ Chart file exists: {os.path.getsize(chart_path)} bytes")
            else:
                print(f"❌ Chart file not found!")
        else:
            print("⚠️  No influential nodes found for chart")
            
    except Exception as e:
        print(f"❌ Error creating influence chart: {e}")
    
    print("\n🎉 Test completed!")
    print("\n📋 Next steps:")
    print("1. Run: python run.py --mode web")
    print("2. Open: http://localhost:8000")
    print("3. Analyze any Twitter URL")
    print("4. Check network visualization in results")

def test_dummy_data():
    """Test data dummy Twitter"""
    
    print("\n🔄 Testing Dummy Data...")
    
    twitter_service = TwitterService(use_real_api=False)
    
    # Test different URLs
    test_urls = [
        "https://twitter.com/user/status/123456",
        "https://twitter.com/hoax/status/789012", 
        "https://x.com/test/status/345678"
    ]
    
    for url in test_urls:
        print(f"\n📋 Testing URL: {url}")
        try:
            tweet_data = twitter_service.get_tweet_data(url)
            print(f"  ✅ Tweet: {tweet_data['text'][:50]}...")
            print(f"  ✅ User: @{tweet_data['user']['username']}")
            print(f"  ✅ Category: {tweet_data.get('category', 'unknown')}")
            print(f"  ✅ Controversial: {tweet_data.get('is_controversial', False)}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Twitter Hoax Detector - Visualization Test")
    print("=" * 50)
    
    # Create directories if not exist
    os.makedirs("visualizations", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    # Test dummy data
    test_dummy_data()
    
    # Test network visualization
    test_network_visualization() 