from flask import Blueprint, request, jsonify
from collections import Counter
from core.db import supabase, exec_data, QUIZQN_TABLE  # ensure: QUIZQN_TABLE = "questions"

bp = Blueprint("quiz", __name__)

# ---------- helpers ----------
def truthy(v, default=False):
    if v is None:
        return default
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    return s in ("1","true","t","yes","y","on")

def to_float(v):
    if v is None: return None
    s = str(v).strip()
    if s == "": return None
    try: return float(s)
    except ValueError: return None

def to_int(v):
    f = to_float(v)
    return int(f) if f is not None else None

def norm_str(v):
    if v is None: return None
    s = str(v).strip()
    return s if s != "" else None

def normalize_row(r):
    return {
        "key": r.get("key"),
        "prompt": r.get("prompt"),
        "input_type": (r.get("input_type") or "").strip().lower(),
        "unit": norm_str(r.get("unit")),
        "min_value": to_float(r.get("min_value")),
        "max_value": to_float(r.get("max_value")),
        "step": to_float(r.get("step")),
        "scale_positive_high": truthy(r.get("scale_positive_high"), default=True),
        "required": truthy(r.get("required"), default=True),
        "section": (r.get("section") or "").strip(),
        "display_order": to_int(r.get("display_order")) or 0,
        "active": truthy(r.get("active"), default=True),
    }

# ---------- endpoint ----------
@bp.route("/quizqn", methods=["GET"])
def get_quizqn():
    """
    Get question catalog entries (CSV-backed table)
    Query:
      key: string (optional) -> single row by key
      section: string (default 'daily'; use 'all' to disable)
      include_inactive: bool (default false)
    """
    try:
        cols = ["key","prompt","input_type","unit","min_value","max_value","step",
                "scale_positive_high","required","section","display_order","active"]

        q_key = request.args.get("key", type=str)
        section = (request.args.get("section") or "daily").strip()
        include_inactive = truthy(request.args.get("include_inactive"), default=False)

        # Always fetch all once; normalize in Python (robust to CSV types)
        resp = supabase.table(QUIZQN_TABLE).select(",".join(cols)).execute()
        raw_rows = exec_data(resp) or []

        # --- DEBUG: what's actually in the table?
        sections = [str(r.get("section") or "").strip().lower() for r in raw_rows]
        actives = [str(r.get("active")).strip().lower() for r in raw_rows]
        # print(f"get_quizqn: raw_rows={len(raw_rows)} sections={Counter(sections)} active={Counter(actives)} table={QUIZQN_TABLE}")

        rows = [normalize_row(r) for r in raw_rows]

        # Single row by key (after normalization)
        if q_key:
            row = next((r for r in rows if r["key"] == q_key), None)
            if not row:
                # print(f"get_quizqn: key='{q_key}' not found")
                return jsonify({"error": "Row not found"}), 404
            if section.lower() != "all" and row["section"].strip().lower() != section.lower():
                # print(f"get_quizqn: key='{q_key}' section mismatch row='{row['section']}' want='{section}'")
                return jsonify({"error": "Row not found"}), 404
            if not include_inactive and not row["active"]:
                # print(f"get_quizqn: key='{q_key}' inactive")
                return jsonify({"error": "Row not found"}), 404
            return jsonify({"row": row}), 200

        # List: filter by section (unless 'all') and activity
        if section.lower() != "all":
            want = section.lower()
            rows = [r for r in rows if (r["section"] or "").strip().lower() == want]
        if not include_inactive:
            rows = [r for r in rows if r["active"]]

        rows.sort(key=lambda r: (r["display_order"], r["key"] or ""))

        # print(f"get_quizqn: returning {len(rows)} rows (section={section}, include_inactive={include_inactive})")
        return jsonify({"rows": rows, "count": len(rows)}), 200

    except Exception as e:
        # print("Error in get_quizqn:", e)
        return jsonify({"error": str(e)}), 500
