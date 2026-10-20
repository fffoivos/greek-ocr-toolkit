"""All-row adapter around the frozen crop/font/word mechanisms. No sample gates.

This changes orchestration only. It retains the accepted refocus, source-context
extent, quarter-turn, font-band reconciliation and JS decision semantics.
"""
from __future__ import annotations
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import select
import signal
import time
import sys
import unicodedata as ud
import warnings
import shutil

from .line_pipeline import digest, identity

ASSETS = Path(__file__).with_name("filtering_assets")


def file_sha(path):
    with open(path, "rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def character_count(text):
    return sum(not c.isspace() and ud.category(c)[0] not in {"M", "C"} for c in ud.normalize("NFC", text))


def reconstructed_crop(page,box,mode="L"):
    """Existing collect_v3.storage.ensure_crop byte contract, without writes."""
    image=page.convert(mode).crop(box)
    buffer=io.BytesIO();image.save(buffer,format="PNG",compress_level=3)
    return image,buffer.getvalue()


def source_crop_matches(page,image,box):
    import numpy as np
    return np.array_equal(np.asarray(page.crop(box).convert(image.mode).convert("RGB")),np.asarray(image.convert("RGB")))


def empty_oblique_rule_fit(error):
    """Recognize only the witnessed no-support refit in the frozen detector.

    This is missing context evidence, not a fitted line or a repaired detector.
    The message AND actual pinned function code frame must match; unrelated
    TypeErrors and every other geometry/runtime contract error remain strict.
    """
    if type(error) is not TypeError or str(error)!='expected non-empty vector for x':return False
    from greekocr.pages.pixels import _direct_rules
    trace=error.__traceback__
    while trace is not None:
        if trace.tb_frame.f_code is _direct_rules.__code__:return True
        trace=trace.tb_next
    return False


class JsonService:
    def __init__(self, command):
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)

    def call(self, request):
        if self.process.poll() is not None:
            raise RuntimeError("native policy/prediction service exited")
        self.process.stdin.write(json.dumps(request, allow_nan=False) + "\n")
        self.process.stdin.flush()
        line = self.process.stdout.readline()
        if not line:
            raise RuntimeError("native service returned no response")
        result = json.loads(line)
        if not result.get("ok"):
            raise RuntimeError(result.get("error", "native service error"))
        return result["result"]

    def close(self):
        if self.process.poll() is None:
            self.process.stdin.close()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.terminate()
                self.process.wait(timeout=2)


class NativeSegmenter:
    def __init__(self, versions, predictor, node="node"):
        for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
            os.environ[key] = "1"
        self.versions = versions
        self.service = JsonService([node, str(ASSETS / "service.mjs")])
        self.predictor = JsonService([str(predictor), str(ASSETS / "font-models.json")])
        spec = importlib.util.spec_from_file_location("frozen_crop_tools", ASSETS / "crop-tools.py")
        self.crop_tools = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.crop_tools)
        self.policy_sha = file_sha(ASSETS / "segmentation-policy.js")

    def close(self):
        self.service.close()
        self.predictor.close()

    def __call__(self, row):
        from PIL import Image
        import numpy as np
        import cv2
        from greekocr.glyphs.components import line_glyphs
        from greekocr.glyphs.baseline import text_lines
        from greekocr.glyphs.orientation import QuarterTurn, measure_orientation
        # OpenCV GCD: setNumThreads(1) reported 10 on this Mac; zero disables it.
        cv2.setNumThreads(0)
        if cv2.getNumThreads() != 1:
            raise RuntimeError("OpenCV single-thread request not honored")
        crop_path = row.get("crop_path")
        source = row.get("crop_source_image")
        box = row.get("crop_bbox")
        if crop_path and Path(crop_path).is_file():
            raw = Path(crop_path).read_bytes()
            if digest_bytes(raw) != row["crop_sha256"]:
                raise ValueError("crop bytes differ from frozen parent")
            image = Image.open(io.BytesIO(raw)); image.load()
        elif source and box:
            if file_sha(source) != row.get("crop_source_sha256"):
                raise ValueError("source page hash mismatch")
            with Image.open(source) as page:
                if not valid_box(box, page.size):
                    raise ValueError("invalid frozen crop coordinates")
                image,encoded=reconstructed_crop(page,box,row.get("crop_color_mode","L"))
                if digest_bytes(encoded) != row["crop_sha256"]:
                    raise ValueError("reconstructed crop bytes differ from frozen crop hash")
        else:
            raise FileNotFoundError("crop and reconstructable source unavailable")
        upright, frame = self.crop_tools.orient_crop(image, row.get("primary_class"), measure_orientation, QuarterTurn)
        chars = character_count(row["raw_text"])
        with warnings.catch_warnings(record=True) as notices:
            glyphs = line_glyphs(upright); lines = text_lines(glyphs)
            complete = [l for l in lines if l.visible >= .9 and l.votes >= 6 and l.x1-l.x0 >= 3*glyphs.band.xh]
            if len(complete) == 1 and complete[0].side != "main" and lines[0].visible < .9:
                mid = float(np.median(complete[0].base[complete[0].x0:complete[0].x1+1])); xh = glyphs.band.xh
                glyphs = line_glyphs(upright, focus=(mid-.4*xh, mid+.4*xh)); lines = text_lines(glyphs)
        yy, xx = np.nonzero(glyphs.ink)
        ink_box = [int(xx.min()), int(yy.min()), int(xx.max())+1, int(yy.max())+1] if len(xx) else None
        components = [dict(index=int(c.index), bbox=[int(c.x0),int(c.y0),int(c.x1),int(c.y1)], role=c.role, area=int(c.area), touches=list(c.touches)) for c in glyphs.components]
        main = next((l for l in lines if l.side == "main"), None)
        angle_deg = 0.0
        # A mathematically flat fitted curve can carry a few ULPs of solver
        # roundoff. Keep that identity case off the floating rotation path.
        if main is not None and len(main.base) > 1 and np.ptp(main.base) > 8*np.spacing(max(1., float(np.max(np.abs(main.base))))):
            x = np.arange(len(main.base), dtype=float); x -= x.mean()
            slope = float(np.dot(x, main.base-main.base.mean()) / np.dot(x, x))
            angle_deg = float(np.degrees(np.arctan(slope)))  # clockwise in image coordinates
        inventory, main_cut = self.crop_tools.line_inventory(glyphs, lines, components, angle_deg)
        packed = []
        for l in lines:
            at = np.unique(np.r_[np.linspace(0,glyphs.width-1,min(128,glyphs.width),dtype=int), *[np.array([np.argmin(getattr(l,k)),np.argmax(getattr(l,k))]) for k in ('ascender','mean','base','descender')]])
            packed.append(dict(side=l.side, votes=l.votes, visible=l.visible,
                curves={k:[[int(x),round(float(getattr(l,k)[x]),3)] for x in at] for k in ('ascender','mean','base','descender')}))
        evidence = dict(characters=chars, orientation_resolved=frame["orientation_resolved"],
            lines=inventory, gate=dict(main_cut=main_cut), detected_rows=packed,
            box_evidence=dict(available=False, reason="skipped: gate did not pass"),
            padding_evidence=dict(available=False, reason="skipped: gate did not pass"), neighbour_evidence=None)
        gate = self.service.call(dict(operation="decide", policy_sha256=self.policy_sha,
            evidence=dict(evidence, gate_only=True)))
        evidence["gate"] = gate
        if gate["verdict"] == "PASS":
            features = self.crop_tools.features_from_observation(width=glyphs.width, height=glyphs.height, components=components,
                ink_box=ink_box, ink_pixels=int(glyphs.ink.sum()), xheight=float(glyphs.band.xh), xheight_source=glyphs.band.xh_source,
                support_count=glyphs.band.n_support, chars=chars, labels=glyphs.labels, angle_deg=angle_deg,
                base_curve=main.base if main is not None else None, base_is_straight=(glyphs.band.curve_is_straight
                    if glyphs.band.curve_is_straight is not None else glyphs.band.degree != 2))
            b = features["candidate_text_box"]
            evidence["box_evidence"] = dict(available=False)
            evidence["padding_evidence"] = dict(available=False)
            if b:
                rf = features["row_frame_text_box"]
                prediction = self.predictor.call(dict(long_side=max(rf["length"],rf["height"]), short_side=min(rf["length"],rf["height"]), script=row.get("script_class", "pooled")))
                evidence["box_evidence"] = dict(available=True, predictions=[None,None,prediction["expected"]], bbox=b["bbox"], prediction=prediction, row_frame=rf)
                h = features["segment"]["height"]
                evidence["padding_evidence"] = dict(available=True, total_padding_line_heights=(h-b["height"])/rf["height"],
                    upright_box_height=b["height"], row_frame_height=rf["height"])
        if any(l["side"] != "main" and l["votes"] > 0 for l in packed):
            try:
                context = self.context(row, image, frame, QuarterTurn)
            except (OSError, ValueError) as exc:
                # Context is optional diagnostics; a verified crop's decision
                # never depends on source-page availability or its binding.
                context = dict(status="unavailable", reason="source context unusable",
                    error=dict(type=type(exc).__name__, detail=str(exc)))
            if context.get('error'):
                evidence['context_unavailable']={k:context[k] for k in ('status','reason','error')}
            if context.get('invalid_geometry_count'):
                evidence['context_geometry']={k:context.get(k) for k in ('status','reason','invalid_geometry_count','invalid_row_ids','affected_invalid_row_ids')}
            evidence["neighbour_evidence"] = self.service.call(dict(operation="reconcile", policy_sha256=self.policy_sha, context=context, crop=dict(lines=packed)))
            reconciled = evidence["neighbour_evidence"]
            bands = [l for l in inventory if l["votes"] > 0]
            if "group_bindings" in reconciled:
                for i, band in enumerate(bands):
                    if band["side"] == "main":
                        continue
                    groups = [g for g in reconciled["group_bindings"] if g["band_index"] == i]
                    band.update(context_whole_words=sum(g["positive"] for g in groups),
                        context_cutoff_words=sum(not g["positive"] and not g["unresolved"] for g in groups),
                        context_count_resolved=reconciled["whole_word_count_resolved"])

        result = self.service.call(dict(operation="decide", policy_sha256=self.policy_sha, evidence=evidence))
        return dict(result, tool_version=self.versions["segmentation"]["version"], binding=identity(row), raw_text_sha256=digest(row["raw_text"]),
            policy_sha256=self.policy_sha, evidence=evidence, frame=frame, warnings=[str(w.message) for w in notices])

    def context(self, row, image, frame, QuarterTurn):
        import numpy as np
        from PIL import Image
        from greekocr.pages import process_page, PageOptions
        from .geometry_observations import vendor_ownership, vendor_magnitude, prepare_geometry_row
        from .row_inclusion import supported_rows
        source, box = row.get("crop_source_image"), row.get("crop_bbox")
        if not source or not box:
            return dict(status="unavailable", reason="source context unavailable")
        if file_sha(source) != row.get("crop_source_sha256"):
            raise ValueError("context page hash mismatch")
        with Image.open(source) as native:
            native.load()
            if not valid_box(box, native.size) or not source_crop_matches(native,image,box):
                raise ValueError("source/crop pixels differ")
            turn = QuarterTurn(native.width,native.height,frame["normalization_cw"])
            page = turn.image(native); corners = turn.rectangle(box,inverse=False)
            mapped = [int(v) for v in [*corners.min(0),*corners.max(0)]]; h=mapped[3]-mapped[1]
            roi=[0,max(0,mapped[1]-3*h),page.width,min(page.height,mapped[3]+3*h)]
            context=page.crop(roi); crop=[mapped[0],mapped[1]-roi[1],mapped[2],mapped[3]-roi[1]]
        collector=ASSETS/"collector"
        ownership=vendor_ownership(collector=collector)
        try:result=process_page(context,options=PageOptions(join_lines=True,granularity="rows"))
        except TypeError as exc:
            if not empty_oblique_rule_fit(exc):raise
            return dict(status='unavailable',reason='empty_oblique_rule_refit',error=dict(type=type(exc).__name__,detail=str(exc)))
        pixels=result.segmentation.pixels; metadata={r["id"]:r for r in result.rows}; rows=[];invalid_rows=[]
        for delivered in result.delivery:
            r={k:v for k,v in delivered.items() if k!="pieces"}
            r["component_ids"]=sorted({int(c) for i in metadata[r["row_id"]]["line_indices"] for c in result.segmentation.lines[i].component_ids})
            owned=pixels.components[np.isin(pixels.components[:,5],r["component_ids"])]
            if not len(owned): continue
            r["owned_box"]=[int(owned[:,0].min()),int(owned[:,1].min()),int(owned[:,2].max()),int(owned[:,3].max())]
            prepared,invalid=prepare_geometry_row(r,metadata[r['row_id']],pixels.ink,pixels.labels,ownership)
            if invalid is not None:invalid_rows.append(invalid)
            else:rows.append(prepared)
        observation=supported_rows(dict(rows=rows,invalid_rows=invalid_rows,invalid_geometry_count=len(invalid_rows),structure=metadata,ink=pixels.ink,labels=pixels.labels,ownership=ownership),crop,
            magnitude_loader=lambda:vendor_magnitude(collector=collector))
        if observation["status"]!="measured":
            return dict(status="unavailable", reason=observation.get("reason"),invalid_geometry_count=len(invalid_rows),
                invalid_row_ids=[r['row_id'] for r in invalid_rows],affected_invalid_row_ids=observation.get('invalid_row_ids',[]))
        hits=sorted([(int(ownership.box_hits(r,crop).sum()),r["row_id"]) for r in rows],reverse=True)
        hits=[hit for hit in hits if hit[0]]
        if not hits or len(hits)>1 and hits[0][0]==hits[1][0]:
            return dict(status="unavailable",reason="missing_or_ambiguous_target_row",invalid_geometry_count=len(invalid_rows),
                invalid_row_ids=[r['row_id'] for r in invalid_rows])
        target=hits[0][1]; byid={r["row_id"]:r for r in rows}; observed=[]
        for rr in observation["rows"]:
            if not rr["assigned_pixels"]:continue
            r=byid[rr["row_id"]]; groups=rr["local_groups"]; xx,yy=r["_x"],r["_y"]
            extent=[int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1] if len(xx) else None
            inside=extent and crop[0]<=extent[0] and extent[2]<=crop[2] and crop[1]<=extent[1] and extent[3]<=crop[3]
            edge=extent and ((extent[1]==0 and roi[1]>0) or (extent[3]==context.height and roi[3]<page.height))
            full=bool(inside and not edge and groups and all(g["positive"] for g in groups))
            observed.append(dict(row_id=rr["row_id"],full_line=full,groups=[dict(bbox=[g["box"][0]-crop[0],g["box"][1]-crop[1],g["box"][2]-crop[0],g["box"][3]-crop[1]],positive=bool(g["positive"]),unresolved=bool(g["unresolved"])) for g in groups]))
        return dict(id=row["id"],status="measured",target_row_id=target,rows=observed,
            invalid_geometry_count=len(invalid_rows),invalid_row_ids=[r['row_id'] for r in invalid_rows],
            qualification="Existing CP4 word-group geometric proxy; owner accepted current segmentation unchanged")


def digest_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def valid_box(box, size):
    return len(box)==4 and all(type(v) is int for v in box) and 0<=box[0]<box[2]<=size[0] and 0<=box[1]<box[3]<=size[1]


class NativeWorker:
    """One reusable native process; hard per-row timeout kills its whole group."""
    def __init__(self, versions_path, predictor, timeout=120, runtime_manifest=None):
        self.command=[sys.executable,"-m",__name__,"--worker",str(versions_path),str(predictor)]
        if runtime_manifest:self.command.extend(['--runtime-manifest',str(runtime_manifest)])
        self.timeout=timeout;self.process=None

    def __call__(self,row):
        if self.process is not None and self.process.poll() is not None:self.close()
        if self.process is None:
            env=dict(os.environ)
            for key in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
                env[key]="1"
            root=str(Path(__file__).resolve().parents[2])
            env["PYTHONPATH"]=root+os.pathsep+env.get("PYTHONPATH","")
            self.process=subprocess.Popen(self.command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,bufsize=0,start_new_session=True,env=env)
        try:
            deadline=time.monotonic()+self.timeout
            request=(json.dumps(row,allow_nan=False)+"\n").encode()
            os.set_blocking(self.process.stdin.fileno(),False)
            while request:
                remaining=deadline-time.monotonic()
                if remaining<=0 or not select.select([],[self.process.stdin],[],remaining)[1]:raise TimeoutError("native row timed out")
                try:sent=os.write(self.process.stdin.fileno(),request)
                except BlockingIOError:continue
                request=request[sent:]
            data=bytearray()
            while b"\n" not in data:
                remaining=deadline-time.monotonic()
                if remaining<=0 or not select.select([self.process.stdout],[],[],remaining)[0]:raise TimeoutError("native row timed out")
                chunk=os.read(self.process.stdout.fileno(),65536)
                if not chunk:raise RuntimeError("native row worker exited without a complete result")
                data.extend(chunk)
                if len(data)>64*1024*1024:raise ValueError("native worker response too large")
            line,extra=data.split(b"\n",1)
            if extra:raise ValueError("unsolicited native worker output")
            answer=json.loads(line)
            if not answer.get("ok"):
                if answer.get("error_type")=="FileNotFoundError":raise FileNotFoundError(answer["error"])
                raise RuntimeError(answer["error"])
            return answer["result"]
        except BaseException:
            self.close();raise

    def close(self):
        if self.process is not None:
            try:
                os.killpg(self.process.pid,signal.SIGKILL)
            except ProcessLookupError:
                pass
            process=self.process;self.process=None
            try:process.wait(timeout=5)
            finally:
                for stream in (process.stdin,process.stdout):
                    if stream:stream.close()


def main():
    import argparse
    import contextlib
    p=argparse.ArgumentParser();p.add_argument("--worker",action="store_true");p.add_argument("versions");p.add_argument("predictor")
    p.add_argument('--runtime-manifest')
    args=p.parse_args()
    if not args.runtime_manifest:
        raise ValueError('native worker requires a bound runtime manifest')
    node=shutil.which('node')
    if node is None:raise FileNotFoundError('Node runtime unavailable')
    if args.runtime_manifest:
        from .line_pipeline_runtime import validate
        validate(args.runtime_manifest,dict(node=node,predictor=args.predictor))
    native=NativeSegmenter(json.loads(Path(args.versions).read_text())["tools"],str(Path(args.predictor).resolve()),node=str(Path(node).resolve()))
    try:
        for line in sys.stdin:
            try:
                with contextlib.redirect_stdout(sys.stderr):
                    result=native(json.loads(line))
                answer=dict(ok=True,result=result)
            except Exception as exc:answer=dict(ok=False,error_type=type(exc).__name__,error=str(exc))
            print(json.dumps(answer,allow_nan=False),flush=True)
    finally:native.close()


if __name__=="__main__":main()
