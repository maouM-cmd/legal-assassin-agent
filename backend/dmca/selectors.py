"""CSS selectors for DMCA platform forms (update when DOM changes)."""

YOUTUBE = {
    "url_input": 'input[name*="video"]',
    "description": 'textarea',
    "submit": 'button[type="submit"]',
}

TIKTOK = {
    "url_input": 'input[type="url"], input[name*="url"]',
    "description": 'textarea',
    "submit": 'button[type="submit"]',
}

TWITTER = {
    "url_input": 'input[type="url"], input[name*="url"]',
    "description": 'textarea',
    "submit": 'button[type="submit"], input[type="submit"]',
}
