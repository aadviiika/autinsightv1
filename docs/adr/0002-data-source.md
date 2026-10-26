# ADR 0002: UCI primary and Indian S2 secondary datasets

- Status: Accepted
- Context: The project specifies UCI children data and investigation of Indian INDT-ASD data.
- Decision: Use the CC BY 4.0 UCI 419 source as the primary application dataset. Also acquire the public CC BY 4.0 S2 deidentified workbook linked to the 2019 PLOS AIIMS modified INDT-ASD validation study through Figshare. Keep the 2019 workbook distinct from the 2024 paper's named AMI database unless equivalence can be established.
- Consequences: The datasets have different questionnaires, labels, and cohorts and are evaluated separately. Raw human data stays git-ignored and is not copied into documentation.
