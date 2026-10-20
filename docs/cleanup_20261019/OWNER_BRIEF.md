# Owner brief — repo clean-up and organisation (19 Oct 2026, verbatim)

OK I think the current version of the segment filter is good enough I dont want to look at it any more.

Plan and execute a clean up, and organization of the repo, I want:

(1) clear distinction of the following aspects of the repo:

(A) development of OCR, and our Segmenter: (i) the slow one (ii) the next gen (iii) the one built on top of small detector
(B) creation of training data for OCR:
(a) running google OCR on pages
(b) tools built on top of (A)'s segmenter and so on (the ones we are working on now) for correcting and filtering these
(c) the exact pipeline this process takes, which should organize the whole work of (B)
(d) the revision pipeline for (B.b) including the artifacts and how we publish for human review

I want you to create comprehensive documentation for these, an AGENTS md that explains our process (as described above) and a README. And generally removing what is not required.
Your process hsould involve either doing this in a new branch, or whatever other method allows easy comparison for an xhigh astra reviewer at the end given my brief.
