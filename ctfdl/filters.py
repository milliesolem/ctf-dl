import logging

logger = logging.getLogger("ctfdl.filters")

def apply_filters(challenges, categories=None, min_points=None, max_points=None):
    """
    Apply filtering based on categories and points.

    Args:
        challenges (list): List of challenge objects from ctfbridge.
        categories (list): List of allowed categories (optional).
        min_points (int): Minimum points to include (optional).
        max_points (int): Maximum points to include (optional).

    Returns:
        list: Filtered list of challenges.
    """

    filtered = []

    for chal in challenges:
        if not challenge_passes_filters(chal, categories, min_points, max_points):
            continue
        filtered.append(chal)

    return filtered

def challenge_passes_filters(chal, categories, min_points, max_points):
    """
    Check if a single challenge passes all active filters.
    """

    # Category filter
    if categories:
        if not chal.category or chal.category.lower() not in [c.lower() for c in categories]:
            logger.debug("Challenge %s skipped due to category filter", chal.name)
            return False

    # Points filter
    if min_points is not None:
        if chal.value is None or chal.value < min_points:
            logger.debug("Challenge %s skipped due to min points filter", chal.name)
            return False

    if max_points is not None:
        if chal.value is None or chal.value > max_points:
            logger.debug("Challenge %s skipped due to max points filter", chal.name)
            return False

    return True
