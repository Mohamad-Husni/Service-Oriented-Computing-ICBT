# Assignment guide

## Case and deliverables

NWSDB needs shared payment and recorded-usage services that its website and third-party applications can consume. WaterLink implements two .NET APIs, an ASP.NET Core web portal, and a .NET/Avalonia partner client. It is an academic prototype with fictional accounts and no bank transfers.

| Question | Marks | Repository evidence |
| --- | --- | --- |
| 1 Architecture comparison | 20 | Report section 1 |
| 2 SOC design and implementation | 60 | Report section 2; src; API guide; Mermaid diagrams |
| 3 Testing and debugging | 10 | Report section 3; tests; evidence; review notes |
| 4 Deployment | 10 | Report section 4; Dockerfile; compose.yaml; deployment guide |

## Navigation

- [GitHub report](REPORT.md)
- [Mermaid diagrams](DIAGRAMS.md): architecture, use cases, class structure, sequence and data model
- [API guide](API.md) and [OpenAPI definition](openapi.json)
- [Deployment guide](DEPLOYMENT.md)
- [Review and limitations](REVIEW.md)
- [Build and run instructions](../README.md)
- [Unit results](../evidence/unit-results.txt), [integration results](../evidence/integration-results.json), [browser results](../evidence/browser-results.json) and [desktop HTTP results](../evidence/desktop-results.txt)

## Verification boundary

The recorded run passed 56 checks: 16 unit, 26 HTTP integration, 10 Chromium and four desktop HTTP checks. The report table lists ten selected cases, some grouping related assertions. These results are not a coverage percentage. Native desktop interaction, Docker and Kubernetes execution are unverified.

The Word report retains its numbered figures and submission formatting. The GitHub report uses Mermaid for every diagram and exact text for code excerpts. UI figures remain real screenshots. Student identity fields remain blank. The document word-count audit excludes cover, contents, conclusion and bibliography.

Only original project material and supporting evidence are published here. Local copies of lecture material, SDKs, live databases and temporary rendering files are excluded.
