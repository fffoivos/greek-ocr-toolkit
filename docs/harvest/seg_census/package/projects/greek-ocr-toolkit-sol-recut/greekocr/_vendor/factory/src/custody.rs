//! Byte-level custody shared by synthetic builds and real imports.
use anyhow::Result;
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;
use std::path::Path;

pub fn hash(bytes: &[u8]) -> String {
    format!("{:x}", Sha256::digest(bytes))
}

pub fn shard_hashes(root: &Path) -> Result<BTreeMap<String, String>> {
    let mut hashes = BTreeMap::new();
    for entry in walkdir::WalkDir::new(root) {
        let entry = entry?;
        let p = entry.path();
        if p.is_file() && p.file_name().is_some_and(|n| n.to_string_lossy().starts_with("shard-"))
            && p.extension().is_some_and(|e| e == "parquet") {
            hashes.insert(p.strip_prefix(root)?.to_string_lossy().into_owned(), hash(&std::fs::read(p)?));
        }
    }
    Ok(hashes)
}
