import json
import os
import re
import stat
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(os.environ.get("MEDIA_ROOT", "/srv/media")).resolve(strict=True)
VIDEO_EXTENSIONS = {".mkv", ".mp4", ".avi", ".m4v", ".mov", ".webm", ".mpg", ".mpeg"}
INVALID_COMPONENT = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
STABILITY_SECONDS = max(0, int(os.environ.get("MEDIA_STABILITY_SECONDS", "600")))
_observed_files = {}
_observed_files_lock = threading.Lock()


def reply(handler, status, body):
    data = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(data)


def split_relative(value):
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise ValueError("invalid_path")
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError("invalid_path")
    if any(INVALID_COMPONENT.search(part) for part in parts):
        raise ValueError("invalid_path")
    return parts


def no_symlink_path(parts, allow_missing=False):
    current = ROOT
    for index, part in enumerate(parts):
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError:
            if allow_missing:
                continue
            raise
        if stat.S_ISLNK(info.st_mode):
            raise ValueError("symlink_not_allowed")
    return current


def valid_source(parts):
    if len(parts) != 2 or parts[0] != "Inbox":
        raise ValueError("source_must_be_direct_child_of_inbox")
    if Path(parts[1]).suffix.lower() not in VIDEO_EXTENSIONS:
        raise ValueError("unsupported_video_extension")
    path = no_symlink_path(parts)
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode):
        raise ValueError("source_must_be_regular_file")
    return path


def valid_destination(parts, source_ext):
    if parts[0] == "Review":
        if len(parts) != 2:
            raise ValueError("invalid_review_destination")
    elif parts[0] == "Movies":
        if len(parts) != 3 or not re.search(r" \((?:19|20)\d{2}\)$", parts[1]):
            raise ValueError("invalid_movie_destination")
    elif parts[0] == "Shows":
        if len(parts) != 4 or not re.fullmatch(r"Season \d{2,3}", parts[2]):
            raise ValueError("invalid_show_destination")
    else:
            raise ValueError("destination_must_be_review_movies_or_shows")
    if Path(parts[-1]).suffix.lower() != source_ext:
        raise ValueError("extension_mismatch")
    if any(part.startswith(".") or part.endswith((".", " ")) for part in parts):
        raise ValueError("invalid_path_component")
    return no_symlink_path(parts, allow_missing=True)


class Handler(BaseHTTPRequestHandler):
    server_version = "MediaOrganizer/1.0"
    sys_version = ""

    def log_message(self, fmt, *args):
        # Avoid writing file names or request data to container logs.
        return

    def do_GET(self):
        route = urlsplit(self.path).path
        if route == "/health":
            return reply(self, 200, {"ok": True})
        if route != "/inbox":
            return reply(self, 404, {"error": "not_found"})
        inbox = ROOT / "Inbox"
        try:
            files = []
            now = time.monotonic()
            seen = set()
            with os.scandir(inbox) as entries:
                for entry in entries:
                    if entry.name.startswith(".") or Path(entry.name).suffix.lower() not in VIDEO_EXTENSIONS:
                        continue
                    info = entry.stat(follow_symlinks=False)
                    if not stat.S_ISREG(info.st_mode):
                        continue
                    seen.add(entry.name)
                    signature = (info.st_size, info.st_mtime_ns)
                    with _observed_files_lock:
                        previous = _observed_files.get(entry.name)
                        if previous is None or previous[0] != signature:
                            _observed_files[entry.name] = (signature, now)
                            continue
                        stable_since = previous[1]
                    if now - stable_since < STABILITY_SECONDS:
                        continue
                    files.append({"name": entry.name, "size": info.st_size, "mtime": int(info.st_mtime)})
            with _observed_files_lock:
                for name in set(_observed_files) - seen:
                    _observed_files.pop(name, None)
            files.sort(key=lambda item: item["name"].casefold())
            return reply(self, 200, {"files": files})
        except OSError:
            return reply(self, 500, {"error": "inbox_unavailable"})

    def do_POST(self):
        if urlsplit(self.path).path != "/move":
            return reply(self, 404, {"error": "not_found"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 4096:
                return reply(self, 400, {"error": "invalid_request_size"})
            request = json.loads(self.rfile.read(length))
            source_parts = split_relative(request.get("source"))
            target_parts = split_relative(request.get("destination"))
            source = valid_source(source_parts)
            destination = valid_destination(target_parts, source.suffix.lower())
            destination.parent.mkdir(mode=0o2775, parents=True, exist_ok=True)
            # Re-check every component after mkdir so a symlink cannot redirect the move.
            destination = no_symlink_path(target_parts, allow_missing=True)
            if destination.exists() or destination.is_symlink():
                return reply(self, 200, {"moved": False, "reason": "destination_exists"})
            try:
                # Hard-link then unlink is same-filesystem and will never overwrite a target.
                os.link(source, destination, follow_symlinks=False)
            except FileExistsError:
                return reply(self, 200, {"moved": False, "reason": "destination_exists"})
            try:
                os.unlink(source)
            except OSError:
                try:
                    os.unlink(destination)
                except OSError:
                    pass
                raise
            return reply(self, 200, {"moved": True, "destination": "/".join(target_parts)})
        except (ValueError, json.JSONDecodeError, TypeError):
            return reply(self, 400, {"error": "invalid_request"})
        except FileNotFoundError:
            return reply(self, 200, {"moved": False, "reason": "source_missing"})
        except OSError:
            return reply(self, 500, {"error": "move_failed"})


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
