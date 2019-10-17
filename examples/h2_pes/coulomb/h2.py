#!/usr/bin/python3

import mlqm
import psi4
import matplotlib.pyplot as plt
import numpy as np

#Return the biggest n values in a matrix.
def biggest_values(mat, n) :
    line = []
    for r in mat :
        line.extend(r)
    if len(line) < n :
        line.extend(0 for i in range(len(line) - n))
    return sorted(line, reverse = True)[:n]

pes = mlqm.PES("pes.json")
opts = {"basis": pes.basis, "scf_type": "pk", "e_convergence": 1e-8,
        "d_convergence": 1e-8}
extras = """
wfn.to_file('wfn.npy')
import numpy as np
mol = wfn.molecule()
coulomb = np.array([[(mol.fZ(i) ** 2.4 / 2 if i == j else (mol.fZ(i) * mol.fZ(j)) / np.linalg.norm([mol.fx(i) - mol.fx(j), mol.fy(i) - mol.fy(j), mol.fz(i) - mol.fz(j)])) for j in range(mol.natom())] for i in range(mol.natom())])
np.save('j.npy', coulomb)
"""

dlist = pes.generate(opts, directory = "./pes", extra = extras)

pes.save()
pes.run(progress = True)
pes.save()
results = mlqm.datahelper.grabber(dlist, varnames = ["SCF TOTAL ENERGY"],
                                  fnames = ["j.npy"])
scf_E = [E for E in list(results['SCF TOTAL ENERGY'].values())]
mats = [m for m in list(results["j.npy"].values())]
reps = [biggest_values(mat, 10) for mat in mats]

ds = mlqm.Dataset(inpf = "ml.json", reps = reps, vals = scf_E)

validators = list(reversed([i for i in range(0, ds.setup["N"], 4)]))
valid_reps = [ds.grand["representations"][val] for val in validators]
valid_vals = [ds.grand["values"][val] for val in validators]
ds.grand["representations"] = np.delete(ds.grand["representations"], validators,
                                        axis = 0)
ds.grand["values"] = np.delete(ds.grand["values"], validators, axis = 0)

ds.find_trainers("k-means")

ds, t_AVG = ds.train("KRR")
ds.save()
pred_E = mlqm.krr.predict(ds, valid_reps)
pred_E = np.add(pred_E, t_AVG)

pes_x = np.linspace(float(pes.dis[0]), float(pes.dis[1]), int(pes.pts))
v_pes = [pes_x[i] for i in validators]
noval_pes = np.delete(pes_x, validators, axis = 0)
t_pes = [noval_pes[i] for i in ds.data["trainers"]]

plt.figure(1)
plt.plot(pes_x, scf_E, 'y-o', label = "SCF PES")
plt.plot(v_pes, pred_E, 'r-^', label = "J PES")
plt.plot(t_pes, [min(min(scf_E), min(pred_E)) * 1.1 for i in range(len(t_pes))],
         "go", label = "Training Points")
plt.legend()
plt.savefig("pes.png")
plt.figure(2)
plt.plot(v_pes, np.subtract([scf_E[i] for i in validators], pred_E), "bo",
         label = "Absolute Errors")
plt.plot(pes_x, [0.002 for i in pes_x], "r-")
plt.plot(pes_x, [-0.002 for i in pes_x], "r-")
plt.legend()
plt.savefig("error.png")
plt.show()
