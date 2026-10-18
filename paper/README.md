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

### 2026-10-18, M1 integration (current)

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
