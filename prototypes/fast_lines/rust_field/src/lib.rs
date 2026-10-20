//! Current M15 independent correlation batch. No Python callbacks or threads.
use std::slice;

// NumPy's contiguous float64 pairwise reduction: 8 accumulators, block128.
fn sum(a: &[f64]) -> f64 {
    let n=a.len();
    if n<8 { let mut s=-0.0; for &x in a {s+=x;} return s; }
    if n<=128 {
        let mut r=[0.;8];r.copy_from_slice(&a[..8]);let mut i=8;
        while i<n-(n%8) {for j in 0..8 {r[j]+=a[i+j];} i+=8;}
        let mut s=((r[0]+r[1])+(r[2]+r[3]))+((r[4]+r[5])+(r[6]+r[7]));
        while i<n {s+=a[i];i+=1;}return s;
    }
    let mut n2=n/2;n2-=n2%8;sum(&a[..n2])+sum(&a[n2..])
}
fn interp(x:f64,xp:&[f64],fp:&[f64])->f64 {
    if x<xp[0] || x>xp[xp.len()-1] {return 0.;}
    if x==xp[xp.len()-1] {return fp[fp.len()-1];}
    let j=xp.partition_point(|v|*v<=x).saturating_sub(1);
    if x==xp[j] {return fp[j];}
    let slope=(fp[j+1]-fp[j])/(xp[j+1]-xp[j]);
    slope.mul_add(x-xp[j],fp[j])
}
/// All pointers have checked contiguous extents supplied by the sole Python wrapper.
/// Output buffers do not alias inputs. No pointer is retained after returning.
#[no_mangle]
pub unsafe extern "C" fn field_shifts(
    before:*const f64,moved:*const f64,profiles:*const f64,ys:*const f64,
    lag:*const f64,lengths:*const i64,columns:*const i64,energy:*const f64,
    c:usize,k:usize,w:usize,y:usize,x:usize,l:usize,
    delta:*mut f64,weight:*mut f64,scores:*mut f64,
) {
    let before=slice::from_raw_parts(before,c*k*w);let moved=slice::from_raw_parts(moved,c*k*w);
    let profiles=slice::from_raw_parts(profiles,x*y);let ys=slice::from_raw_parts(ys,y);
    let lag=slice::from_raw_parts(lag,l);let lengths=slice::from_raw_parts(lengths,k);
    let columns=slice::from_raw_parts(columns,c);let energy=if energy.is_null(){None}else{Some(slice::from_raw_parts(energy,c*k))};
    let delta=slice::from_raw_parts_mut(delta,c*k);let weight=slice::from_raw_parts_mut(weight,c*k);
    let scores=slice::from_raw_parts_mut(scores,c*k*l);
    let mut after=vec![0.;w];let mut temp=vec![0.;w];
    for ci in 0..c {let fp=&profiles[columns[ci] as usize*y..(columns[ci] as usize+1)*y];
        for ki in 0..k {let off=(ci*k+ki)*w;let b=&before[off..off+w];let m=&moved[off..off+w];
            let length=lengths[ki] as usize;
            let e=match energy {Some(e)=>e[ci*k+ki],None=>{for j in 0..w {temp[j]=b[j]*b[j];}sum(&temp)}};
            for li in 0..l {
                for j in 0..w {after[j]=interp(m[j]+lag[li],ys,fp);temp[j]=if j<length {after[j]}else{0.};}
                let mean=sum(&temp)/(length.max(1) as f64);
                for j in 0..w {after[j]=if j<length {after[j]-mean}else{0.};temp[j]=after[j]*after[j];}
                let ae=sum(&temp);
                for j in 0..w {temp[j]=after[j]*b[j];}
                scores[(ci*k+ki)*l+li]=sum(&temp)/((ae*e).sqrt()+1e-9);
            }
            let s=&scores[(ci*k+ki)*l..(ci*k+ki+1)*l];let mut best=0;
            for j in 1..l {if s[j]>s[best] {best=j;}}
            let mut d=lag[best];
            if best>0 && best+1<l {d+=0.5*(s[best-1]-s[best+1])/(-1e-9f64).min(s[best-1]-2.*s[best]+s[best+1])*(lag[1]-lag[0]);}
            delta[ci*k+ki]=if length<5 {0.}else{d};
            weight[ci*k+ki]=if length<5 {0.}else{0.0f64.max(s[best])};
        }
    }
}
