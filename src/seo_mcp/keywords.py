from typing import List, Optional, Any, Dict, Union

import requests


def _coerce_int(value: Any) -> int:
    """
    Coerce a value to an integer, handling various input types.

    Args:
        value: The value to convert (int, float, str, or other)

    Returns:
        Integer value, or 0 if conversion fails
    """
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        # Try to parse numeric strings
        try:
            # Handle strings like "1,000" or "1.5k"
            cleaned = value.replace(',', '').lower().strip()
            if cleaned.endswith('k'):
                return int(float(cleaned[:-1]) * 1000)
            if cleaned.endswith('m'):
                return int(float(cleaned[:-1]) * 1000000)
            return int(float(cleaned))
        except (ValueError, TypeError):
            return 0
    return 0


def _map_difficulty_label_to_int(label: Union[str, int, None]) -> int:
    """
    Map difficulty labels to integer values (0-100 scale).

    Args:
        label: Difficulty label string or numeric value

    Returns:
        Integer difficulty score (0-100)
    """
    if label is None:
        return 0
    if isinstance(label, (int, float)):
        return _coerce_int(label)

    label_lower = str(label).lower().strip()

    difficulty_map = {
        'easy': 15,
        'medium': 40,
        'hard': 70,
        'super hard': 90,
        'very hard': 85,
        'very easy': 5,
        'unknown': 0,
    }

    if label_lower in difficulty_map:
        return difficulty_map[label_lower]

    # Try to parse as numeric
    return _coerce_int(label)


def _map_volume_label_to_int(label: Union[str, int, None]) -> int:
    """
    Map volume labels to integer values.

    Args:
        label: Volume label string or numeric value

    Returns:
        Integer volume estimate
    """
    if label is None:
        return 0
    if isinstance(label, (int, float)):
        return _coerce_int(label)

    label_str = str(label).strip()

    # Handle range formats like "100-1K" or "1K-10K"
    if '-' in label_str:
        parts = label_str.split('-')
        if len(parts) == 2:
            # Use the lower bound of the range
            return _coerce_int(parts[0])

    # Handle formats like "0" or "10" or "1K" or "10K"
    return _coerce_int(label_str)


def format_keyword_ideas(keyword_data: Optional[List[Any]]) -> List[str]:
    if not keyword_data or len(keyword_data) < 2:
        return ["\n❌ No valid keyword ideas retrieved"]
    
    data = keyword_data[1]

    result = []
    
    # Process regular keyword ideas
    if "allIdeas" in data and "results" in data["allIdeas"]:
        all_ideas = data["allIdeas"]["results"]
        for idea in all_ideas:
            simplified_idea = {
                "keyword": idea.get('keyword', 'No keyword'),
                "country": idea.get('country', '-'),
                "difficulty": _map_difficulty_label_to_int(idea.get('difficultyLabel')),
                "volume": _map_volume_label_to_int(idea.get('volumeLabel')),
                "updatedAt": idea.get('updatedAt', '-')
            }
            result.append({
                "label": "keyword ideas",
                "value": simplified_idea
            })

    # Process question keyword ideas
    if "questionIdeas" in data and "results" in data["questionIdeas"]:
        question_ideas = data["questionIdeas"]["results"]
        for idea in question_ideas:
            simplified_idea = {
                "keyword": idea.get('keyword', 'No keyword'),
                "country": idea.get('country', '-'),
                "difficulty": _map_difficulty_label_to_int(idea.get('difficultyLabel')),
                "volume": _map_volume_label_to_int(idea.get('volumeLabel')),
                "updatedAt": idea.get('updatedAt', '-')
            }
            result.append({
                "label": "question ideas",
                "value": simplified_idea
            })
    
    if not result:
        return ["\n❌ No valid keyword ideas retrieved"]
    
    return result


def get_keyword_ideas(token: str, keyword: str, country: str = "us", search_engine: str = "Google") -> Optional[List[str]]:
    if not token:
        return None
    
    url = "https://ahrefs.com/v4/stGetFreeKeywordIdeas"
    payload = {
        "withQuestionIdeas": True,
        "captcha": token,
        "searchEngine": search_engine,
        "country": country,
        "keyword": ["Some", keyword]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        return None
    
    data = response.json()

    return format_keyword_ideas(data)


def get_keyword_difficulty(token: str, keyword: str, country: str = "us") -> Optional[Dict[str, Any]]:
    """
    Get keyword difficulty information
    
    Args:
        token (str): Verification token
        keyword (str): Keyword to query
        country (str): Country/region code, default is "us"
        
    Returns:
        Optional[Dict[str, Any]]: Dictionary containing keyword difficulty information, returns None if request fails
    """
    if not token:
        return None
    
    url = "https://ahrefs.com/v4/stGetFreeSerpOverviewForKeywordDifficultyChecker"
    
    payload = {
        "captcha": token,
        "country": country,
        "keyword": keyword
    }
    
    headers = {
        "accept": "*/*",
        "content-type": "application/json; charset=utf-8",
        "referer": f"https://ahrefs.com/keyword-difficulty/?country={country}&input={keyword}"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            return None
        
        data: Optional[List[Any]] = response.json()
        # Check response data format
        if not isinstance(data, list) or len(data) < 2 or data[0] != "Ok":
            return None
        
        # Extract valid data
        kd_data = data[1]
        
        # Format return result
        result = {
            "difficulty": kd_data.get("difficulty", 0),  # Keyword difficulty
            "shortage": kd_data.get("shortage", 0),      # Keyword shortage
            "lastUpdate": kd_data.get("lastUpdate", ""), # Last update time
            "serp": {
                "results": []
            }
        }
        
        # Process SERP results
        if "serp" in kd_data and "results" in kd_data["serp"]:
            serp_results = []
            for item in kd_data["serp"]["results"]:
                # Only process organic search results
                if item.get("content") and item["content"][0] == "organic":
                    organic_data = item["content"][1]
                    if "link" in organic_data and organic_data["link"][0] == "Some":
                        link_data = organic_data["link"][1]
                        result_item = {
                            "title": link_data.get("title", ""),
                            "url": link_data.get("url", [None, {}])[1].get("url", ""),
                            "position": item.get("pos", 0)
                        }
                        
                        # Add metrics data (if available)
                        if "metrics" in link_data and link_data["metrics"]:
                            metrics = link_data["metrics"]
                            result_item.update({
                                "domainRating": metrics.get("domainRating", 0),
                                "urlRating": metrics.get("urlRating", 0),
                                "traffic": metrics.get("traffic", 0),
                                "keywords": metrics.get("keywords", 0),
                                "topKeyword": metrics.get("topKeyword", ""),
                                "topVolume": metrics.get("topVolume", 0)
                            })
                        
                        serp_results.append(result_item)
            
            result["serp"]["results"] = serp_results
        
        return result
    except Exception:
        return None
