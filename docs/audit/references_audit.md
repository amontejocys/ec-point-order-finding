# Bibliography audit: references [27], [28], [30]

Checked 2026-10-18. Numbering reconstructed from REVTeX citation order in the
Post_M1 snapshot (identical in the Pre_M1 export for positions 25-31). The
reviewed PDF may have used earlier numbering; the match between the reviewer's
objection types and the findings below supports the identification. No .tex or
.bib was edited; wording changes are the author's decision.

| Number | BibTeX key | Cited as | Finding | Status |
| --- | --- | --- | --- | --- |
| [27] | Bhatia2020, "Hybrid classical-quantum approaches in cryptography", Quantum Inf. Process. 19:195 (2020), DOI 10.1007/s11128-020-02694-6 | Introduction, hybrid protocols sentence; Discussion, "hybrid pattern of" | DOI resolves (Crossref) to Wang, Meng, Fei, Ma, "Finite-key security analysis of the 1-decoy state QKD protocol with a leaky intensity modulator", QIP 19:196 (2020). Crossref bibliographic search finds no article with the cited title and authors. | Existence not established; remove or replace with a verifiable source |
| [28] | Bittel2021, "Training variational quantum algorithms is NP-hard", Phys. Rev. Lett. 127, 120502 (2021) | Introduction, hybrid protocols sentence | Exists (Crossref confirmed). Topic is VQA trainability; it does not support a statement about hybrid classical-quantum cryptographic protocols. | Not pertinent to the sentence; remove |
| [30] | Endo2021, "Hybrid quantum-classical algorithms and quantum error mitigation", J. Phys. Soc. Jpn. 90, 032001 (2021) | Introduction, hybrid protocols sentence; Discussion, "hybrid pattern of" | Exists (Crossref confirmed). General review of hybrid algorithms and error mitigation, not cryptography. | Weak pertinence; keep only if the sentence is about hybrid algorithms in general |

Related: [29] Cerezo2021 (Nature Reviews Physics 3, 625-644) exists and is a
general VQA review; same pertinence caveat as [30]. All four are cited together
in one introduction sentence about hybrid classical-quantum protocols that
delegate only the classically dominant operations.

Method: Crossref REST API for each DOI and a bibliographic title search;
publisher pages were not reachable without a session.
