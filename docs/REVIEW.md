# Assessment and engineering review

## Corrected during development

- The first Microsoft.Data.Sqlite version brought a transitive high-severity advisory. Restore failed with NU1903. Updated to 10.0.12; final restore/build succeeded without disabling vulnerability auditing.
- Desktop compile failed on obsolete TextBox.Watermark with warnings treated as errors. Preserved the failing build log; changed it to PlaceholderText and rebuilt successfully.
- Prepared and assigned the container data directory to the non-root runtime user; the initial Dockerfile did not do this.
- Added bounded login rate limiting to the portal.
- Introduced a separate public-contract library so the desktop client does not reference database code.
- Added isolated data/port settings for reproducible verification and kept test output separate from claims about production readiness.

## Evidence and limitations

Read evidence/unit-results.txt, integration-results.json, browser-results.json and desktop-results.txt. Unit checks use an executable assertion harness. Integration checks send real HTTP requests and exercise durable SQLite transactions. Browser checks use Chromium at desktop, tablet and mobile widths. Desktop evidence concerns the actual HTTP client flow; native mouse/keyboard and Windows-specific UI behaviour are not established by those smoke checks. Test counts describe assertions, not a code-coverage percentage.

The written task's four question numbers are retained in the report. The rubric's manufacturer/supplier wording does not replace the NWSDB case. REST/JSON satisfies the stated .NET API condition; WCF/SOAP is not silently assumed compulsory. No ICBT lecture material is cited as external research.

## Remaining production work

Identity federation, customer provisioning, real bank settlement/reconciliation, official tariff integration, email receipts, metering-system integration, production observability, secret rotation and server-database migration are outside the implemented prototype. The report must not claim those exist. A 100% grade cannot be promised; the rubric evaluation remains the lecturer's decision.
