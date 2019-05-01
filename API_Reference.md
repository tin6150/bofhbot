# API Reference

## `GET /status`
- Returns list of nodes and their states

## `POST /cycle`
- Payload: `[string]` of node host names
- Power cycle selected nodes (IPMI)

## `POST /resume`
- Payload: `[string]` of node host names
- Resume selected nodes (`scontrol update state=resume`)

## `POST /cycle-resume`
- Payload: `[string]` of node host names
- Power cycle selected nodes and resume if overall check is OK

/etc/pdsh