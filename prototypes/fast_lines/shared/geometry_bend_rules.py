"""Verified finite rule barriers shared by bend and historical row experiments."""
import cv2
import numpy as np

def finite_rules(gray,h,witness,primitive,columns):
    """Native verification of every nominated vertical stroke, including cells.

    M13 certificates remain unchanged. Other rules constrain geometry only;
    they do not certify front ink and never create a removal exclusion.
    """
    from ..layout_barriers.fast import verify_rule
    from .geometry_feature_rules import curved_rule
    rules=[]
    for q in (columns or {}).get('rules',[]):
        if q.get('accepted') and q.get('rule'):rules.append(q['rule'])
    if witness is not None:
        _,sx,sy=primitive
        for x,y,w,z,area in witness.get('vertical_components',[]):
            if z/sy<3*h or w/sx>3*h:continue
            candidate=dict(bbox=[x/sx,y/sy,(x+w)/sx,(y+z)/sy])
            rule,_=verify_rule(gray,candidate,h)
            if rule is None:rule,_=curved_rule(gray,candidate,h)
            if rule is not None:rules.append(rule)
    # The old scout starts at12h. Native reduced opening exposes shorter table
    # dividers independently; the same full-resolution verifier decides them.
    scale=min(1.,12/h);small=cv2.resize(gray,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
    threshold=cv2.threshold(small,0,1,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]
    vertical=cv2.morphologyEx(threshold,cv2.MORPH_OPEN,np.ones((max(3,round(3*h*scale)),1),np.uint8))
    _,lab,stats,_=cv2.connectedComponentsWithStats(vertical,8)
    for x,y,w,z,area in stats[1:]:
        if w/scale>h/2:continue
        cx=(x+w/2)/scale;cy=(y+z/2)/scale
        if any(abs(np.interp(cy,np.array(r['path'])[:,1],np.array(r['path'])[:,0])-cx)<h/2 and r['y0']<=cy<=r['y1'] for r in rules):continue
        r,_=verify_rule(gray,dict(bbox=[x/scale,y/scale,(x+w)/scale,(y+z)/scale]),h)
        if r is not None:rules.append(r)
    return rules
