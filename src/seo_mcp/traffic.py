"""
Check the estimated search traffic for any website. Try Ahrefs' free traffic checker.
"""

from typing import Optional, Dict, Any, Literal, List
import requests
import json


def check_traffic(token: str, domain_or_url: str, mode: Literal["subdomains", "exact"] = "subdomains", country: str = "None") -> Optional[Dict[str, Any]]:
    """
    Check the estimated search traffic for any website.
    
    Args:
        domain_or_url (str): The domain or URL to query
        token (str): Verification token
        mode (str): Query mode, default is "subdomains"
        country (str): Country, default is "None"
    
    Returns:
        Optional[Dict[str, Any]]: Dictionary containing traffic data, returns None if request fails
    """
    if not token:
        return None
    
    url = "https://ahrefs.com/v4/stGetFreeTrafficOverview"
    
    # Convert parameters to JSON string and pass as single input parameter
    params = {
        "input": json.dumps({
            "captcha": token,
            "country": country,
            "protocol": "None",
            "mode": mode,
            "url": domain_or_url
        })
    }
    
    headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "referer": f"https://ahrefs.com/traffic-checker/?input={domain_or_url}&mode={mode}"
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            return None
        
        data: Optional[List[Any]] = response.json()

        # Check response data format
        if not isinstance(data, list) or len(data) < 2 or data[0] != "Ok":
            return None
        
        # Extract valid data
        traffic_data = data[1]
        
        # Format return result
        result = {
            "traffic_history": traffic_data.get("traffic_history", []),
            "traffic": {
                "trafficMonthlyAvg": traffic_data.get("traffic", {}).get("trafficMonthlyAvg", 0),
                "costMontlyAvg": traffic_data.get("traffic", {}).get("costMontlyAvg", 0)
            },
            "top_pages": traffic_data.get("top_pages", []),
            "top_countries": traffic_data.get("top_countries", []),
            "top_keywords": traffic_data.get("top_keywords", [])
        }
        
        return result
    except Exception as e:
        return None