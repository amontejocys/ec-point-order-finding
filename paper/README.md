# Manuscript synchronization

Keep the reviewed .tex/.bib snapshot in manuscript/, including required styles
and images. The current snapshot is recorded below.

Overleaf remains the editing authority until an explicit switch is agreed.
Synchronize only named exports, record the source ZIP and SHA-256, and inspect
the diff before replacing local sources. Do not edit Overleaf and local copies
independently. The baseline was ZIP (12) plus two manually corrected paragraph breaks; this was
verified against the Pre_M1 export (see below).

Figures in figures/ must identify the generating script, configuration, run,
and source commit. Do not hand-edit numerical plots.
Preserve the original structure and correct prose; blue marks real changes.

## Snapshots

### 2026-10-26, Post_P final (15:15 export): bibliography clean-up (current)

- Source: Overleaf export `Shor_s_Algorithm_Adapted_for_Determining_the_Order_of_Elliptic_Curves__1_ (6).zip` (the export was saved under that name), downloaded 2026-10-26 15:15.
- ZIP SHA-256: `901548859a987b02b58e05e9e841fa593eb2011554bb575b4e85de9223758393`.
- Changed since the 15:09 export (commit addedb6): `main.bib` only. The `Qiskit2023`
  entry lost its redundant `note = {Accessed 2024}` line; no citation is affected.
  All section files are identical to the 15:09 snapshot.
- Checks by the independent reader: keys, labels, `revision` blocks, no textcolor,
  repeated-word and spacing scan, no first-person plural.
- Files are stored byte-for-byte; compile confirmed in Overleaf by the author.

File digests:

| File | SHA-256 |
| --- | --- |
| circuit_1.png | `bab7e049982a5bb1111d2f9fe039a9a22b225953d078e7090201f9766293af3b` |
| circuit_2.png | `9cbd099eeef2009e2cec39efb6c6894e157d9ac18dddb48ac9bc3997824c3a1d` |
| classical_points.png | `1b8203677ecbf518c3f324b0d4ac981efca3342e43a44199f7e4437db7124600` |
| final_result.png | `8f9a6b496ab8afa08c13b27eb8986e19ddc47302873ee156674a69f1153ae75a` |
| main.bib | `de184702a3795f309b0c4783436fa0e488b74eca6c99b05e352c1e229e7d1c07` |
| main.tex | `351fed1fc11aa28acd4ec853cbde0f6ae77807b906f992e286c9530f24f8438d` |
| quantum_results.png | `6cd159588aede3ffadede422983e43b7dc4d19a8c786730e6b280e57b1e953f0` |
| sec/00-authors.tex | `d462fee34a0f83cadf64dc6de9febfdee9fea0e5a4bbfe599a0b289f139824f4` |
| sec/01-abstract.tex | `d0ddeb3b286a323c61a124d14df50fa1795edc8fd2bebbe79ee63278ad771424` |
| sec/02-introduction.tex | `77c063fb6938d7899d525a7a73c66887ce26caccd0d458bc475e1b56e279ed74` |
| sec/03-methods.tex | `f63032c06708b849b6e17b85f7125ec569d594fb646497ccb6b463b7bd1277bd` |
| sec/04-results_discussions.tex | `68db92d96d36c8499bed3761dc9088af39930fe0873cf05944f88cf0fe480192` |
| sec/05-acknowledgements.tex | `5d8df6aa9b0d0c1510254614cefc07989d4fd620835c31f5d9c21cde09fe670c` |
| sec/06-data_availability.tex | `7e3c99208818972c56d9fee74ed5d0285699c5ac6278e2defda051380dbaf245` |
| sec/07-author_contributions.tex | `a5a79ae019aeed3e568061a925c1d3a7d02d8bff4e4186dad6f4a8b374edbf9f` |
| sec/08-appendix.tex | `fa6099e17ecd07c709723cd561c857935ec57f089acb7b460f45bb62a1041aeb` |

### 2026-10-26, Post_P final (15:09 export): motivation wording (superseded)

- Source: Overleaf export `Shor_s_Algorithm_Adapted_for_Determining_the_Order_of_Elliptic_Curves__Post_P.zip`, downloaded 2026-10-26 15:09.
- ZIP SHA-256: `cb6e627ee168bffd612c7d72edbdcd87c913cb6b90e6336dd1dd31bd100f6630`.
- Changed since the 14:12 export (commit 3e02ab1, tag stage8-text-final): `sec/04-results_discussions.tex`.
  The Discussion sentence on motivation now states that quantum order finding is studied
  as the quantum step of the signing pipeline without claiming a speedup over classical
  point-order methods; point counting is polynomial in l, order reduction given the
  factorization of the group cardinality is polynomial, and the factorization cost is
  accounted for separately in the complexity section (the term C_fact(M) there).
- Checks by the independent reader: keys, labels, `revision` blocks, no `\textcolor`,
  repeated-word and spacing scan, no first-person plural; the cross-reference to the
  separate factorization cost was verified in the text.
- Compile in Overleaf confirmed by the author; the local build fails inside the
  algorithm float as in all earlier snapshots. Files are stored byte-for-byte.

File digests:

| File | SHA-256 |
| --- | --- |
| circuit_1.png | `bab7e049982a5bb1111d2f9fe039a9a22b225953d078e7090201f9766293af3b` |
| circuit_2.png | `9cbd099eeef2009e2cec39efb6c6894e157d9ac18dddb48ac9bc3997824c3a1d` |
| classical_points.png | `1b8203677ecbf518c3f324b0d4ac981efca3342e43a44199f7e4437db7124600` |
| final_result.png | `8f9a6b496ab8afa08c13b27eb8986e19ddc47302873ee156674a69f1153ae75a` |
| main.bib | `7322ae82b3a9a633faf1e1584776b945cfe91b67ae95617c88cf924a950caf49` |
| main.tex | `351fed1fc11aa28acd4ec853cbde0f6ae77807b906f992e286c9530f24f8438d` |
| quantum_results.png | `6cd159588aede3ffadede422983e43b7dc4d19a8c786730e6b280e57b1e953f0` |
| sec/00-authors.tex | `d462fee34a0f83cadf64dc6de9febfdee9fea0e5a4bbfe599a0b289f139824f4` |
| sec/01-abstract.tex | `d0ddeb3b286a323c61a124d14df50fa1795edc8fd2bebbe79ee63278ad771424` |
| sec/02-introduction.tex | `77c063fb6938d7899d525a7a73c66887ce26caccd0d458bc475e1b56e279ed74` |
| sec/03-methods.tex | `f63032c06708b849b6e17b85f7125ec569d594fb646497ccb6b463b7bd1277bd` |
| sec/04-results_discussions.tex | `68db92d96d36c8499bed3761dc9088af39930fe0873cf05944f88cf0fe480192` |
| sec/05-acknowledgements.tex | `5d8df6aa9b0d0c1510254614cefc07989d4fd620835c31f5d9c21cde09fe670c` |
| sec/06-data_availability.tex | `7e3c99208818972c56d9fee74ed5d0285699c5ac6278e2defda051380dbaf245` |
| sec/07-author_contributions.tex | `a5a79ae019aeed3e568061a925c1d3a7d02d8bff4e4186dad6f4a8b374edbf9f` |
| sec/08-appendix.tex | `fa6099e17ecd07c709723cd561c857935ec57f089acb7b460f45bb62a1041aeb` |

### 2026-10-26, Post_P final (14:12 export): stage-8 corrections (superseded)

- Source: Overleaf export `Shor_s_Algorithm_Adapted_for_Determining_the_Order_of_Elliptic_Curves__Post_P.zip`, downloaded 2026-10-26 14:12.
- ZIP SHA-256: `581e6c9d4feecf1dc8e64495c8f7830aa648775e67b0c476ca2a43fefb87aa1f`.
- Previous record: the Post_P snapshot of 13:44 (below, superseded). Files changed since
  then: `sec/04-results_discussions.tex`, `sec/08-appendix.tex`.
- Changes: one sentence in the Discussion stating that quantum order finding is studied
  as the quantum step of the signing pipeline and not as a faster route to the point
  order (point counting plus classical order reduction is already polynomial in l,
  Schoof citation); the theorem label `thm:speedup` renamed `thm:resource_bound` in
  all six places (one label, five references).
- Checks by the independent reader: every cited key exists and every entry is cited;
  no reference without label; `revision` blocks balanced, not nested; no `\textcolor`;
  repeated-word and spacing scan clean; no first-person plural.
- Local MiKTeX build fails inside `\end{algorithm}` as in earlier snapshots
  (REVTeX 4.2 / algorithm float interaction); Overleaf is the compile authority and
  the author confirms the clean compile there.
- Files are stored byte-for-byte (`.gitattributes -text`). `sec/00-authors.tex`
  contains author names; review before any double-blind submission.

File digests:

| File | SHA-256 |
| --- | --- |
| circuit_1.png | `bab7e049982a5bb1111d2f9fe039a9a22b225953d078e7090201f9766293af3b` |
| circuit_2.png | `9cbd099eeef2009e2cec39efb6c6894e157d9ac18dddb48ac9bc3997824c3a1d` |
| classical_points.png | `1b8203677ecbf518c3f324b0d4ac981efca3342e43a44199f7e4437db7124600` |
| final_result.png | `8f9a6b496ab8afa08c13b27eb8986e19ddc47302873ee156674a69f1153ae75a` |
| main.bib | `7322ae82b3a9a633faf1e1584776b945cfe91b67ae95617c88cf924a950caf49` |
| main.tex | `351fed1fc11aa28acd4ec853cbde0f6ae77807b906f992e286c9530f24f8438d` |
| quantum_results.png | `6cd159588aede3ffadede422983e43b7dc4d19a8c786730e6b280e57b1e953f0` |
| sec/00-authors.tex | `d462fee34a0f83cadf64dc6de9febfdee9fea0e5a4bbfe599a0b289f139824f4` |
| sec/01-abstract.tex | `d0ddeb3b286a323c61a124d14df50fa1795edc8fd2bebbe79ee63278ad771424` |
| sec/02-introduction.tex | `77c063fb6938d7899d525a7a73c66887ce26caccd0d458bc475e1b56e279ed74` |
| sec/03-methods.tex | `f63032c06708b849b6e17b85f7125ec569d594fb646497ccb6b463b7bd1277bd` |
| sec/04-results_discussions.tex | `c31074d8a1b34dc65477cdc90aec24db842fb73af91a91eab840731c2167656d` |
| sec/05-acknowledgements.tex | `5d8df6aa9b0d0c1510254614cefc07989d4fd620835c31f5d9c21cde09fe670c` |
| sec/06-data_availability.tex | `7e3c99208818972c56d9fee74ed5d0285699c5ac6278e2defda051380dbaf245` |
| sec/07-author_contributions.tex | `a5a79ae019aeed3e568061a925c1d3a7d02d8bff4e4186dad6f4a8b374edbf9f` |
| sec/08-appendix.tex | `fa6099e17ecd07c709723cd561c857935ec57f089acb7b460f45bb62a1041aeb` |

### 2026-10-26, Post_P: stage-7 integration of the F evidence (superseded by the final export above)

- Source: Overleaf export `Shor_s_Algorithm_Adapted_for_Determining_the_Order_of_Elliptic_Curves__Post_P.zip`, downloaded 2026-10-26 13:44.
- ZIP SHA-256: `e412ec03934b6fc69d2fa40c0465ba0a1919fafe15b180fe78a8875a77a89d28`.
- Previous snapshot: Post_M1 (below). Files changed: `main.bib`, `sec/01-abstract.tex`, `sec/02-introduction.tex`, `sec/03-methods.tex`, `sec/04-results_discussions.tex`, `sec/06-data_availability.tex`, `sec/08-appendix.tex`.
  Unchanged: `main.tex`, `sec/00-authors.tex`, `sec/05-acknowledgements.tex`,
  `sec/07-author_contributions.tex` and the five images.
- Content: bibliography keys `Ekera2022OrderFinding` and `Papa2025Validation` added,
  `Bhatia2020` and `Bittel2021` removed together with four uncited entries;
  appendix derivation of the finite recovery law and of the explicit baseline rule;
  results block on the finite reliability evaluation (no figure); positioning,
  limitations, abstract, contribution and data-availability updates; typographical
  corrections. All content under `revision`, no `\textcolor`; the algorithm is blue
  through `\color{blue}`. No first-person plural.
- Checks by the independent reader: every cited key exists in main.bib and every
  entry is cited; every reference has a label; `revision` blocks balanced, not nested
  or crossed; repeated-word and spacing scan clean; quoted numbers match results/m2-f/
  and results/m2-f-p4/; the 443 rule follows from the appendix bound chain.
- Local MiKTeX build fails as in earlier snapshots inside `\end{algorithm}`
  (REVTeX 4.2 / algorithm float interaction); Overleaf is the compile authority and
  the author confirms the clean compile there.
- Files are stored byte-for-byte (`.gitattributes -text`). `sec/00-authors.tex`
  contains author names; review before any double-blind submission.

File digests:

| File | SHA-256 |
| --- | --- |
| circuit_1.png | `bab7e049982a5bb1111d2f9fe039a9a22b225953d078e7090201f9766293af3b` |
| circuit_2.png | `9cbd099eeef2009e2cec39efb6c6894e157d9ac18dddb48ac9bc3997824c3a1d` |
| classical_points.png | `1b8203677ecbf518c3f324b0d4ac981efca3342e43a44199f7e4437db7124600` |
| final_result.png | `8f9a6b496ab8afa08c13b27eb8986e19ddc47302873ee156674a69f1153ae75a` |
| main.bib | `7322ae82b3a9a633faf1e1584776b945cfe91b67ae95617c88cf924a950caf49` |
| main.tex | `351fed1fc11aa28acd4ec853cbde0f6ae77807b906f992e286c9530f24f8438d` |
| quantum_results.png | `6cd159588aede3ffadede422983e43b7dc4d19a8c786730e6b280e57b1e953f0` |
| sec/00-authors.tex | `d462fee34a0f83cadf64dc6de9febfdee9fea0e5a4bbfe599a0b289f139824f4` |
| sec/01-abstract.tex | `d0ddeb3b286a323c61a124d14df50fa1795edc8fd2bebbe79ee63278ad771424` |
| sec/02-introduction.tex | `77c063fb6938d7899d525a7a73c66887ce26caccd0d458bc475e1b56e279ed74` |
| sec/03-methods.tex | `f63032c06708b849b6e17b85f7125ec569d594fb646497ccb6b463b7bd1277bd` |
| sec/04-results_discussions.tex | `58ebf4db47ad4e99148647e11f0de88a0e6d42b01e4f9741e1dbda9bb1298c71` |
| sec/05-acknowledgements.tex | `5d8df6aa9b0d0c1510254614cefc07989d4fd620835c31f5d9c21cde09fe670c` |
| sec/06-data_availability.tex | `7e3c99208818972c56d9fee74ed5d0285699c5ac6278e2defda051380dbaf245` |
| sec/07-author_contributions.tex | `a5a79ae019aeed3e568061a925c1d3a7d02d8bff4e4186dad6f4a8b374edbf9f` |
| sec/08-appendix.tex | `4ecb6a981b2ed0226bb7b9e63928d1c3700e09341b2a256ab4c7ff2ee6d51eab` |

### 2026-10-18, M1 integration (superseded by Post_P)

- Source: Overleaf export `Shor_s_Algorithm_Adapted_for_Determining_the_Order_of_Elliptic_Curves__Post_M1.zip`, downloaded 2026-10-18 17:04.
- ZIP SHA-256: `982b0f591ec339f23b3c9d50b9300f8d18cd3b5e65c8a509323978f49efb0953`.
- Baseline check: ZIP (12) (SHA-256 prefix `d5f4dfd8f35a3eb5`, downloaded 2026-10-16 23:49;
  the file is no longer in Downloads) differs from the Pre_M1 export
  (`74e3d9b6523a7211...`) only by two removed `\\` paragraph breaks (methods, results),
  confirming the agreed baseline.
- Changes Pre_M1 -> Post_M1 are confined to `sec/04-results_discussions.tex`,
  `sec/08-appendix.tex` and `main.bib` (new key `Menezes1996HAC`). Abstract,
  introduction, methods and conclusions are unchanged.
- Checks: every cited key exists in main.bib; `revision` blocks balanced in every
  file; macros `\ord`, `\operatorname{ord}`, `\mathcal{O}` available; technical
  statements match the code (64 Miller--Rabin rounds, bases in {2,...,r-2},
  2^-128 fixed-composite bound, exact small-prime acceptance of r=5).
- Files are stored byte-for-byte (CRLF as exported, `.gitattributes -text`).
- Local MiKTeX build of both Pre_M1 and Post_M1 fails identically inside
  `\end{algorithm}` (REVTeX 4.2 / algorithm float interaction); Overleaf is the
  compile authority; the author confirms the clean compile there.
- The snapshot includes `sec/00-authors.tex` with author names: review before any
  double-blind submission.

File digests:

| File | SHA-256 |
| --- | --- |
| circuit_1.png | `bab7e049982a5bb1111d2f9fe039a9a22b225953d078e7090201f9766293af3b` |
| circuit_2.png | `9cbd099eeef2009e2cec39efb6c6894e157d9ac18dddb48ac9bc3997824c3a1d` |
| classical_points.png | `1b8203677ecbf518c3f324b0d4ac981efca3342e43a44199f7e4437db7124600` |
| final_result.png | `8f9a6b496ab8afa08c13b27eb8986e19ddc47302873ee156674a69f1153ae75a` |
| main.bib | `d9879ac7781d006ac534f5c69358218c303e30a389234899df2cf632a3367489` |
| main.tex | `351fed1fc11aa28acd4ec853cbde0f6ae77807b906f992e286c9530f24f8438d` |
| quantum_results.png | `6cd159588aede3ffadede422983e43b7dc4d19a8c786730e6b280e57b1e953f0` |
| sec/00-authors.tex | `d462fee34a0f83cadf64dc6de9febfdee9fea0e5a4bbfe599a0b289f139824f4` |
| sec/01-abstract.tex | `6dccca641d8c8687d695aafd201d450f48641bd18dbd259ed31e9234971a85c4` |
| sec/02-introduction.tex | `79eb125088f2e5766771d643abcf6678cfae9c3ccf2415a0f0acd2b51edf992a` |
| sec/03-methods.tex | `e7953d03c0d1387a3139221fad86442567f3687af27ca2ebcebca31fa5a8c603` |
| sec/04-results_discussions.tex | `f0d30b5fd166bf069de0c02b29679d95b81e9b45be7010225fd67580593a2311` |
| sec/05-acknowledgements.tex | `5d8df6aa9b0d0c1510254614cefc07989d4fd620835c31f5d9c21cde09fe670c` |
| sec/06-data_availability.tex | `45db06c89c867c8d9ce68ca967f88b9eddb330140222b2914b3a77dd109cd69e` |
| sec/07-author_contributions.tex | `a5a79ae019aeed3e568061a925c1d3a7d02d8bff4e4186dad6f4a8b374edbf9f` |
| sec/08-appendix.tex | `117127a4224b9fb8d0264aded6685404a76e4888e41e04a5e6ba131ebb1fe528` |
