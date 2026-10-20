"""One durable reservation per image, shared across tranches and restarts.

There is no automatic retry of an uncertain paid read. The transaction commits
before sending. A response saved atomically before death is sufficient to resume;
a request without a response is held for owner reconciliation indefinitely.
"""
import sqlite3,time
from pathlib import Path

class UncertainRead(RuntimeError):pass
class BudgetExceeded(RuntimeError):pass

class Ledger:
    def __init__(self,path,caps,exclusion_manifest_sha256=None):
        path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
        self.db=sqlite3.connect(path,timeout=30);self.db.row_factory=sqlite3.Row
        self.db.execute('PRAGMA journal_mode=WAL');self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('CREATE TABLE IF NOT EXISTS reads (image_hash TEXT PRIMARY KEY, page_id TEXT UNIQUE NOT NULL, tranche TEXT NOT NULL, micro_usd INTEGER NOT NULL, state TEXT NOT NULL, created REAL NOT NULL, exclusion_manifest_sha256 TEXT)')
        columns={r[1] for r in self.db.execute('PRAGMA table_info(reads)')}
        if 'exclusion_manifest_sha256' not in columns:
            self.db.close();raise ValueError('legacy ledger lacks frozen exclusion binding; preserve it for reconciliation')
        prior={r[0] for r in self.db.execute('SELECT DISTINCT exclusion_manifest_sha256 FROM reads')}
        if prior and prior!={exclusion_manifest_sha256}:
            self.db.close();raise ValueError('ledger exclusion manifest changed')
        self.exclusion_manifest_sha256=exclusion_manifest_sha256
        self.caps={k:round(v*1e6) for k,v in caps.items()}
    def get(self,image_hash):
        r=self.db.execute('SELECT * FROM reads WHERE image_hash=?',(image_hash,)).fetchone();return dict(r) if r else None
    def reserve(self,image_hash,page_id,tranche):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            prior=self.get(image_hash)
            if prior:self.db.commit();return prior,False
            cost=self.db.execute('SELECT COALESCE(SUM(micro_usd),0) FROM reads WHERE tranche=?',(tranche,)).fetchone()[0]
            if cost+1500>self.caps[tranche]:raise BudgetExceeded(tranche+' hard cap reached')
            self.db.execute('INSERT INTO reads VALUES (?,?,?,?,?,?,?)',(image_hash,page_id,tranche,1500,'reserved',time.time(),self.exclusion_manifest_sha256));self.db.commit();return self.get(image_hash),True
        except BaseException:self.db.rollback();raise
    def start(self,image_hash):
        with self.db:
            cursor=self.db.execute("UPDATE reads SET state='request_started' WHERE image_hash=? AND state='reserved'",(image_hash,))
            if cursor.rowcount!=1:raise UncertainRead('image already requested; response required for resume')
    def complete(self,image_hash):
        with self.db:self.db.execute("UPDATE reads SET state='response_saved' WHERE image_hash=?",(image_hash,))
    def rows(self):return [dict(r) for r in self.db.execute('SELECT * FROM reads ORDER BY created')]
    def close(self):self.db.close()
