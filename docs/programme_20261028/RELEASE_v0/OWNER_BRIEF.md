# Owner brief — release of the Greek OCR models, lines and code (verbatim, 28 Oct 2026, Europe/Athens)

Collected from the owner's messages in the coordinator session, in order. Verbatim except for the
quoted file paths' line wrapping. These are the owner's rules; the plan implements them exactly.

1. "OK lets discuss about what should go into the github and HF repos and how should they be connected, after the discussion we will need to finalize a plan which you will execute"
2. "what about 4 evenly spread out hceckpoints? do we have optimizer states to go with that?"
3. "OK they will uploaded to my personal HF as public repos
   we will have one dataset for all the lines, with the metadata we have already agreed (repeat them)
   and one for the 3 models, and we will create a collection out of them.
   After all this is done we will start the following:
   test of the whole segmentation to ocr pipeline
   docling tests, integration into glossapi pipeline and so on"
4. "For test I would also like to see it run on
   '/Users/foivoskarounos-zamparloukos/Downloads/ΣΤΡΑΓΓΑΣ ΠΑΠΟΥΣ ΠΟΙΗΣΗ/20260727184649649.pdf' '/Users/foivoskarounos-zamparloukos/Downloads/ΣΤΡΑΓΓΑΣ ΠΑΠΟΥΣ ΠΟΙΗΣΗ/20260727185315673.pdf'
   and I want to see both the line detection and the output per page (or line)
   ...
   doesnt the line metadata also contain where the segment was found on teh page?"
5. "ok I want you to make sure that we drop the license it doesnt matter here, it's image lines, keep the source as a detailed way to find the exact book. and I want you to make sure the line dataset on HF is organized in main branch in the end without any other branches unless there is good reason for it. State the whole plan again"
6. On the open points:
   - synthetic lines: "yes as a seperate file though, what will be the matadata fields ehre? lets discuss this. they should show the distribution of the generator and the particular functions applied to that particular line, where it originated etc"
   - model repo name: "Greek-ocr , Greek OCR is best ... we should emphasize that it supports multiple scripts and both modern and polytonic greek"
   - is the .docx a transcription of the second PDF: "no"
7. "ok on the gaps, and this should also go into the plan as the standard method for documenting gaps like (1-2):
   we should open an issue to the code to fix for future versions; I think this should be in every prompt as well but we should be careful to not overdo it,
   eg we could document documentation gaps, and then push them as issues at the end of a checkpoint, when we have gathered them all together"
   (gaps 1–2 = synthetic per-operation parameters / per-line seeds not recorded; licence column dropped)
8. "ok also I want the ocr version to be v0.n where is the number of ocr model generation we have trained, this is how I want it to be from now on; when we get out of beta we will go to v1
   the same holds for every other code like the synth lines, the correction and filtering tools etc.
   Also I want the github readme to connect to the repos and as we introduce everything we say eg:
   this is the latest dataset of synth lines we have produced: HF file
   this is the corrected google lines: HF file
   this is how we reviewed: git code
   this is the model we have trained: ...
   etc"
9. "OK write the plan in a file, get an astra review on it once; fix whatever you think is right
   and then start implementing autonomously end to end, when x1 is ready do the same for it"

Standing rules that still apply: test sets are reporting only and never select anything; Sol writes all
code, the coordinator plans/reviews/runs remote commands; the Mac is not a processing worker;
credentials only via Keychain/env, never in files/argv/logs, never read or print the HF token on
Clariden; deletions are the owner's call; times in Europe/Athens.
