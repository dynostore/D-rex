# D-rex

Link toward the input dataset used: https://zenodo.org/records/13919490?token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6ImY5MWU5ZjZiLTBhMTQtNDA5Ni04ZWRhLTY1Yjk1Yzg4NjkzYyIsImRhdGEiOnt9LCJyYW5kb20iOiIxOGZlMWE5Y2RhMjliZTA3ZGM1MWY2YzY4NjA4YzUzNyJ9.gKW9hZhYnvlejVprFPtucRT_TlXa4Ei_wCzxGGSM9MJcd__RyPRumpqVdWn2y6ki1wAuiDNfu3NBOIjFRQIjPQ

Dynamic replication for heterogeneous storage nodes.

Maxime GONTHIER - Dante - Haochen


First start a virtual environment.

```bash
python3 -m venv venv  
. venv/bin/activate
```

Install requirements:

```
pip install -e .
```

Execution:

```bash
python3 -m test.drex-test    
```

(sudo if not in editable repository ;))
