from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, HTMLResponse, JSONResponse, Response, StreamingResponse
import io
import base64
import os
import json
import urllib.request
import urllib.parse
import sys

# Add root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from core.privacy_engine import (
    inspect_image_privacy,
    strip_image_metadata,
    spoof_image_location,
    add_anti_fraud_watermark,
    redact_image_box,
    DUMMY_LOCATIONS
)

app = FastAPI(title="Photo Privacy Guard MCP Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENAI_CHALLENGE_TOKEN = os.getenv("OPENAI_CHALLENGE_TOKEN", "")


def parse_image_input(img_str: str) -> bytes:
    if not isinstance(img_str, str) or not img_str.strip():
        raise ValueError("Image input is required (URL or Base64 data).")
    img_str = img_str.strip()

    if img_str.startswith("data:image"):
        comma_idx = img_str.find(",")
        if comma_idx != -1:
            return base64.b64decode(img_str[comma_idx + 1:])

    if img_str.startswith("http://") or img_str.startswith("https://"):
        req = urllib.request.Request(img_str, headers={"User-Agent": "PhotoPrivacyGuard/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read()

    try:
        return base64.b64decode(img_str)
    except Exception:
        raise ValueError("Invalid image data provided. Provide a valid HTTP URL or Base64 string.")


def to_data_uri(raw_bytes: bytes, mime: str = "image/jpeg") -> str:
    return f"data:{mime};base64," + base64.b64encode(raw_bytes).decode("utf-8")


MCP_TOOLS = [
    {
        "name": "inspect_photo_privacy",
        "description": "Scans an image for hidden EXIF metadata, GPS latitude/longitude, device model, and date/time.",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": False,
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": False
        },
        "provided_tool_annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "image": {"type": "string", "description": "Image HTTP URL or Base64 Data URI to inspect"}
            },
            "required": ["image"]
        }
    },
    {
        "name": "spoof_photo_location",
        "description": "Replaces real GPS and device details with realistic dummy coordinates (Paris, Tokyo, London, NYC, Bermuda, or custom lat/long).",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": False,
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": False
        },
        "provided_tool_annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "image": {"type": "string", "description": "Image HTTP URL or Base64 Data URI"},
                "preset": {
                    "type": "string",
                    "enum": ["paris", "tokyo", "london", "newyork", "bermuda", "null_island"],
                    "default": "paris",
                    "description": "Preset tourist/dummy location"
                },
                "custom_lat": {"type": "number", "description": "Optional custom latitude (e.g. 48.858)"},
                "custom_lon": {"type": "number", "description": "Optional custom longitude (e.g. 2.294)"}
            },
            "required": ["image"]
        }
    },
    {
        "name": "strip_photo_metadata",
        "description": "Completely removes all EXIF, GPS, camera settings, and tracking tags for total privacy.",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": False,
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": False
        },
        "provided_tool_annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "image": {"type": "string", "description": "Image HTTP URL or Base64 Data URI"},
                "format": {"type": "string", "enum": ["JPEG", "PNG", "WEBP"], "default": "JPEG"}
            },
            "required": ["image"]
        }
    },
    {
        "name": "add_anti_fraud_watermark",
        "description": "Adds a repeating diagonal anti-fraud protection watermark across sensitive ID cards, CNIC, or utility bills.",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": False,
        "annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": False
        },
        "provided_tool_annotations": {
            "readOnlyHint": True,
            "destructiveHint": False,
            "openWorldHint": False
        },
        "inputSchema": {
            "type": "object",
            "properties": {
                "image": {"type": "string", "description": "Image HTTP URL or Base64 Data URI"},
                "watermark_text": {
                    "type": "string",
                    "default": "FOR VERIFICATION ONLY - DO NOT REUSE",
                    "description": "Security text (e.g. 'FOR BANK ACCOUNT ONLY' or 'SPECIMEN COPY')"
                }
            },
            "required": ["image"]
        }
    }
]


def handle_mcp_request(body: dict) -> dict:
    req_id = body.get("id")
    method = body.get("method", "")
    params = body.get("params") or {}

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "photoprivacyguard", "version": "1.0.0"}
            }
        }

    if method in ("notifications/initialized", "initialized", "ping"):
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": MCP_TOOLS}}

    if method in ("resources/list", "prompts/list", "roots/list"):
        key = method.split("/")[0]
        return {"jsonrpc": "2.0", "id": req_id, "result": {key: []}}

    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})

        try:
            raw_img = parse_image_input(args.get("image", ""))
        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32602, "message": str(e)}}

        if name == "inspect_photo_privacy":
            report = inspect_image_privacy(raw_img)
            summary_text = (
                f"Privacy Risk Score: {report['privacy_score']}/100 ({report['risk_level']})\n"
                f"Has GPS Location: {'YES - ' + str(report['gps']) if report['has_gps'] else 'NO (Safe)'}\n"
                f"Device Model: {report['device'] if report['device'] else 'None detected'}\n"
                f"Recorded Date: {report['timestamp'] or 'None'}\n"
                f"Key Findings: {'; '.join(report['findings'])}"
            )
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": summary_text}]}
            }

        elif name == "spoof_photo_location":
            preset = args.get("preset", "paris")
            lat = args.get("custom_lat")
            lon = args.get("custom_lon")
            spoofed_bytes, info = spoof_image_location(raw_img, preset=preset, custom_lat=lat, custom_lon=lon)
            data_uri = to_data_uri(spoofed_bytes, "image/jpeg")
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Successfully injected dummy location: {info['spoofed_location']} (GPS: {info['latitude']}, {info['longitude']}). Device spoofed as: {info['device']}.\n\n![Sanitized Photo]({data_uri})"
                        }
                    ]
                }
            }

        elif name == "strip_photo_metadata":
            fmt = args.get("format", "JPEG")
            clean_bytes = strip_image_metadata(raw_img, output_format=fmt)
            mime = "image/png" if fmt.upper() == "PNG" else "image/jpeg"
            data_uri = to_data_uri(clean_bytes, mime)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Metadata 100% stripped. All EXIF, GPS coordinates, and camera tracking tags removed.\n\n![Clean Photo]({data_uri})"
                        }
                    ]
                }
            }

        elif name == "add_anti_fraud_watermark":
            wm_text = args.get("watermark_text", "FOR VERIFICATION ONLY - DO NOT REUSE")
            wm_bytes = add_anti_fraud_watermark(raw_img, watermark_text=wm_text)
            data_uri = to_data_uri(wm_bytes, "image/jpeg")
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Anti-fraud document protection applied with text: '{wm_text}'.\n\n![Protected Document]({data_uri})"
                        }
                    ]
                }
            }
        else:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown tool: {name}"}}

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Unknown method: {method}"}}


def read_static(filename: str) -> str:
    path = os.path.join(BASE_DIR, "public", filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return f"<h1>{filename} not found</h1>"


def get_challenge_token() -> str:
    token = os.getenv("OPENAI_CHALLENGE_TOKEN", "Lawd5xjQFTf8GnfKaIovD7X8yJ52tIBhCFzJekbIvt4")
    if not token or token == "OPENAI_CHALLENGE_TOKEN":
        for candidate in [
            os.path.join(BASE_DIR, ".well-known", "openai-apps-challenge"),
            os.path.join(BASE_DIR, "public", ".well-known", "openai-apps-challenge"),
        ]:
            if os.path.exists(candidate):
                try:
                    with open(candidate, "r", encoding="utf-8") as f:
                        t = f.read().strip()
                        if t and t != "PENDING_OPENAI_TOKEN":
                            return t
                except Exception:
                    pass
    return token if token else "Lawd5xjQFTf8GnfKaIovD7X8yJ52tIBhCFzJekbIvt4"


@app.get("/.well-known/openai-apps-challenge")
@app.get("/api/index.py/.well-known/openai-apps-challenge")
async def openai_challenge():
    return PlainTextResponse(get_challenge_token())


@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"])
async def handler(request: Request, full_path: str = ""):
    headers = {k.lower(): v for k, v in request.headers.items()}
    path_param = request.query_params.get("path", "").lower()
    req_path = (
        path_param
        or headers.get("x-matched-path", "")
        or headers.get("x-vercel-matched-path", "")
        or headers.get("x-forwarded-path", "")
        or str(request.url.path)
    ).lower()
    all_context = f"{full_path} {req_path} {str(request.url)}".lower()

    # 0. Handle OPTIONS
    if request.method == "OPTIONS":
        return Response(status_code=200, headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS, HEAD",
            "Access-Control-Allow-Headers": "*"
        })

    # 1. Domain challenge verification (MUST be plain text!)
    if "openai-apps-challenge" in all_context or request.query_params.get("challenge") == "1":
        return PlainTextResponse(get_challenge_token())

    # 2. MCP JSON-RPC for POST (always, regardless of path)
    if request.method == "POST":
        try:
            raw = await request.body()
            if raw:
                body = json.loads(raw.decode("utf-8"))
                if isinstance(body, list):
                    return JSONResponse([handle_mcp_request(item) for item in body if isinstance(item, dict)])
                elif isinstance(body, dict) and "method" in body:
                    result = handle_mcp_request(body)
                    return JSONResponse(result)
        except Exception as e:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
            }, status_code=200)

    # 3. MCP Endpoint for GET / SSE
    if "mcp" in all_context or req_path.startswith("/mcp"):
        accept_hdr = headers.get("accept", "")
        if "text/event-stream" in accept_hdr:
            async def sse_gen():
                yield "event: endpoint\ndata: /mcp\n\n"
            return StreamingResponse(sse_gen(), media_type="text/event-stream", headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*"
            })
        return JSONResponse({
            "status": "online",
            "app": "Photo Privacy Guard MCP Server",
            "version": "1.0.0",
            "protocol": "MCP JSON-RPC 2024-11-05",
            "mcp_endpoint": "/mcp",
            "tools": [t["name"] for t in MCP_TOOLS]
        })

    # 4. Static Assets & Pages
    req_p = str(request.url.path).strip("/")
    if "manifest.json" in req_p or "manifest.json" in full_path:
        mp = os.path.join(BASE_DIR, "public", "manifest.json")
        if os.path.exists(mp):
            with open(mp, "r", encoding="utf-8") as f:
                return Response(content=f.read(), media_type="application/manifest+json")

    if req_p.endswith(".png") or full_path.endswith(".png"):
        fname = os.path.basename(req_p if req_p.endswith(".png") else full_path)
        p = os.path.join(BASE_DIR, "public", fname)
        if os.path.exists(p):
            with open(p, "rb") as f:
                return Response(content=f.read(), media_type="image/png")

    if "privacy" in req_p or "privacy" in full_path:
        return HTMLResponse(read_static("privacy.html"))
    if "about" in req_p or "about" in full_path:
        return HTMLResponse(read_static("about.html"))
    if "terms" in req_p or "terms" in full_path:
        return HTMLResponse(read_static("terms.html"))

    # 5. Default
    accept = headers.get("accept", "")
    if "text/html" not in accept:
        return JSONResponse({
            "status": "online",
            "app": "Photo Privacy Guard MCP Server",
            "version": "1.0.0",
            "protocol": "MCP JSON-RPC 2024-11-05",
            "mcp_endpoint": "/mcp",
            "tools": [t["name"] for t in MCP_TOOLS]
        })

    return HTMLResponse(read_static("index.html"))