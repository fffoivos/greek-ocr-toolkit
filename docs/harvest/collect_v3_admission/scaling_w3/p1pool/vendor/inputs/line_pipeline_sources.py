"""Lossless metadata adapters for the existing collection-v2 and W1/W2 formats."""
from pathlib import Path
from .line_pipeline import canonical


def map_path(value, parent):
    if value is None:return None
    path=str(value)
    for old,new in parent.get("path_map",{}).items():
        if path==old or path.startswith(old.rstrip("/")+"/"):
            return str(Path(new)/Path(path).relative_to(old))
    return str(Path(parent.get("path_root","."))/path) if not Path(path).is_absolute() else path


def canonicalize(record, parent, metadata):
    if parent.get("format","canonical") == "canonical":
        return dict(record,parent_id=parent["id"])
    if parent["format"] not in {"collection-v2","collect-v3-features"}:
        raise ValueError("unknown input adapter")
    row=dict(record,parent_id=parent["id"])
    row["id"]=record["id"]
    if parent["format"]=="collect-v3-features":
        page=record["page_id"];book=page.rsplit("--s",1)[0]
    else:
        book=record["doc"];page=record["id"].rsplit("-l",1)[0]
    row["book_id"]=book;row["page_id"]=page
    declared=metadata.get("books",{}).get(book,{})
    split=metadata.get("row_splits",{}).get(canonical([parent["id"],row["id"]]),declared.get("split",record.get("split",parent.get('split','unassigned'))))
    if parent["format"]=="collection-v2" and parent.get("split") in {"train","dev","test"}:
        aliases={"val":"dev","reserved":"test"}
        # A frozen parent defines its cohort. No raw/book/row override may
        # silently move observations between training and evaluation.
        values=[record.get("split"),declared.get("split"),
                metadata.get("row_splits",{}).get(canonical([parent["id"],row["id"]]))]
        if any(value is not None and aliases.get(value,value)!=parent["split"] for value in values):
            raise ValueError("collection-v2 split conflicts with frozen parent")
    # Frozen collection-v2 evaluation manifests use legacy cohort spellings.
    # Require the explicit parent cohort and reject metadata that would move
    # these observations into training; retain the literal source spelling.
    if parent["format"]=="collection-v2" and split in {"val","reserved"}:
        cohort={"val":"dev","reserved":"test"}[split]
        if parent.get("split")!=cohort:
            raise ValueError("collection-v2 legacy evaluation split conflicts with parent/metadata")
        split=cohort
    if parent["format"]=="collection-v2" and record.get("split") in {"val","reserved"}:
        original=record["split"]
        if parent.get("split")!={"val":"dev","reserved":"test"}[original]:
            raise ValueError("collection-v2 legacy evaluation split conflicts with parent/metadata")
        row["source_split"]=original
    row["split"]=split
    row["edition_id"]=declared.get("edition_id",record.get("edition_id","unresolved:"+book))
    row["edition_identity_status"]="bound" if declared.get("edition_id") or record.get("edition_id") else "unresolved"
    fields=parent.get("raw_text_fields",["old_label","text","label"] if parent["format"]=="collect-v3-features" else ["label"])
    field=next((k for k in fields if isinstance(record.get(k),str)),None)
    if field is None:raise ValueError("no literal/raw parent text field")
    row["raw_text"]=record[field];row["raw_text_field"]=field
    crop=metadata.get("crops",{}).get(canonical([parent["id"],row["id"]]),{})
    row["crop_sha256"]=record.get("crop_sha256") or crop.get("sha256") or "0"*64
    row["crop_identity_status"]="bound" if record.get("crop_sha256") or crop.get("sha256") else "unavailable"
    row["crop_path"]=map_path(crop.get("path",record.get("crop")),parent)
    row["crop_source_image"]=map_path(record.get("crop_source_image",crop.get("source_image")),parent)
    row["crop_source_sha256"]=record.get("crop_source_sha256",crop.get("source_sha256"))
    row["crop_bbox"]=record.get("crop_bbox",crop.get("bbox"))
    row["content_role"]=declared.get("content_role",record.get("primary_class","prose"))
    return row
