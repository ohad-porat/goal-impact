"""Utility module for triggering Next.js cache revalidation."""

import os

import requests

from .logger import get_logger

logger = get_logger("revalidation")


def trigger_revalidation(paths=None):
    """
    Trigger Next.js cache revalidation after scraping completes.

    Args:
        paths: Optional list of specific paths to revalidate. If None, revalidates all common paths.

    Returns:
        bool: True if revalidation was successful, False otherwise.
    """
    revalidate_url = os.getenv("REVALIDATE_URL")
    secret = os.getenv("REVALIDATE_SECRET")

    if not revalidate_url:
        logger.warning("REVALIDATE_URL not set, skipping revalidation")
        return False

    if not secret:
        logger.warning("REVALIDATE_SECRET not set, skipping revalidation")
        return False

    try:
        payload = {}
        if paths:
            payload["paths"] = paths

        response = requests.post(
            revalidate_url,
            json=payload,
            headers={"x-revalidate-secret": secret, "Content-Type": "application/json"},
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            logger.info("Successfully triggered Next.js revalidation")
            logger.info(f"Response: {result.get('message', 'OK')}")
            if result.get("timestamp"):
                logger.info(f"Revalidated at: {result['timestamp']}")
            return True
        else:
            logger.warning(f"Revalidation returned status {response.status_code}")
            logger.warning(f"Response: {response.text}")
            return False

    except requests.exceptions.Timeout:
        logger.error("Revalidation request timed out after 30 seconds")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Error triggering revalidation: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during revalidation: {e}")
        return False
