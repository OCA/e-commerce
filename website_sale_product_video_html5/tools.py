# Copyright 2026 Bosd
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import posixpath
from urllib.parse import urlsplit

ALLOWED_HOSTS_PARAM = "website_sale_product_video_html5.allowed_hosts"

VIDEO_MIMETYPES = {
    ".mp4": "video/mp4",
    ".m4v": "video/mp4",
    ".webm": "video/webm",
    ".ogv": "video/ogg",
    ".ogg": "video/ogg",
}

# Player options are stored in the video URL, like Odoo does for the other
# platforms. Only these exact pairs are ours: anything else in the query
# string belongs to the video host (e.g. signed URLs) and is left untouched.
OPTION_PARAMS = {
    "autoplay=1": "autoplay",
    "loop=1": "loop",
    "controls=0": "hide_controls",
}


def get_allowed_hosts(env):
    value = env["ir.config_parameter"].sudo().get_param(ALLOWED_HOSTS_PARAM) or ""
    return [
        host.strip().lower().removeprefix("www.")
        for host in value.replace("\n", ",").split(",")
        if host.strip()
    ]


def _host_matches(host, allowed_hosts):
    host = host.lower().removeprefix("www.")
    return any(
        host == allowed or host.endswith("." + allowed) for allowed in allowed_hosts
    )


def split_video_url(video_url):
    """Split a video URL into the bare URL and the player options it carries.

    :return: ``(url, options)`` where ``url`` has the option parameters removed
        and ``options`` maps option names to ``True``.
    """
    base, sep, fragment = video_url.partition("#")
    path, qsep, query = base.partition("?")
    options = {}
    kept = []
    for pair in query.split("&") if query else []:
        if pair in OPTION_PARAMS:
            options[OPTION_PARAMS[pair]] = True
        else:
            kept.append(pair)
    url = path + (f"?{'&'.join(kept)}" if kept else "") + sep + fragment
    return url, options


def get_html5_video_mimetype(video_url):
    """Return the mimetype guessed from the URL file extension, if any."""
    extension = posixpath.splitext(urlsplit(video_url).path)[1].lower()
    return VIDEO_MIMETYPES.get(extension)


def is_html5_video_url(video_url, allowed_hosts=()):
    """Tell whether the URL points to a video file a browser can play directly.

    That is the case when the URL path ends with a known video extension, or
    when its host is one of the allowed video hosts (CDNs often serve videos
    from URLs without extension).
    """
    if not video_url:
        return False
    parts = urlsplit(video_url.strip())
    if parts.scheme not in ("http", "https", "") or not parts.hostname:
        return False
    return bool(get_html5_video_mimetype(video_url)) or _host_matches(
        parts.hostname, allowed_hosts
    )
