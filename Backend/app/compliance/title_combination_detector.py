class TitleCombinationDetector:
    def __init__(self):
        # In a real system, this would be a trie or a pre-computed token set
        # For the hackathon Lean 6, we use a simple set-based comparison
        pass

    async def check(self, title: str, existing_titles: list) -> dict:
        """
        Detects if the submitted title is a combination of two or more existing titles.
        Example: "Hindu Indian Express" where "Hindu" and "Indian Express" exist.
        Using exact substring match for higher precision.
        """
        title_lower = title.lower()
        
        found_components = []
        for existing in existing_titles:
            existing_title = existing["normalized_title"].lower()
            
            # Ensure we don't match the same title and use word boundaries
            pattern = rf"\b{re.escape(existing_title)}\b"
            if re.search(pattern, title_lower):
                found_components.append(existing_title)
                
            # Stop if we found a combination of at least 2 distinct existing titles
            if len(found_components) >= 2:
                # Double check to prevent overlapping matches (e.g. "Indian" and "Indian Express")
                # We want distinct segments of the title
                distinct_components = []
                sorted_components = sorted(found_components, key=len, reverse=True)
                
                temp_title = title_lower
                for comp in sorted_components:
                    if comp in temp_title:
                        distinct_components.append(comp)
                        temp_title = temp_title.replace(comp, " ", 1)
                
                if len(distinct_components) >= 2:
                    return {
                        "reason": f"Title appears to be a combination of existing titles: {', '.join(distinct_components)}",
                        "components": distinct_components,
                        "penalty": 1.0
                    }
        
        return None
