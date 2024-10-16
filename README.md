# Reproducibility repository of the paper "D-Rex: Dynamic Data Replication for Heterogeneous Storage Nodes"

All the information are in this depot:

```bash
~$ git clone https://github.com/dynostore/D-rex.git
```

You will find in this repository our schedulers, the state-of-the art algorithms replicated, the simulator of data replications and the informations ofthe input data nodes used.
You can re-create the figure and result in the tables of the paper using our simulation.

## Simulaiton

```bash
~/D-rex$ bash test/reproducibility.sh
```

The results are then in the folder D-rex/plot/combined and D-rex/plot/drex_only
