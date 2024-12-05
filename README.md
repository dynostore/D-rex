# Reproducibility repository of the paper "D-Rex: Adaptive Erasure Coding for Efficient Data Storage on Wide-Area Heterogeneous Storage Systems"

All the information are in this depot:

```bash
~$ git clone https://github.com/dynostore/D-rex.git
```

You will find in this repository our schedulers, the state-of-the art algorithms, the simulator of data replications and the informations of the input data nodes used.
You can re-create the figure and result in the tables of the paper using our simulation.

## Simulation

In order to produce figures 5, 7, 8 and 9 one can run:

```bash
~/D-rex$ bash test/all_drex_only.sh
```

Then
```bash
~/D-rex$
```

The results are then in the folder D-rex/plot/combined
