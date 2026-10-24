#!/bin/bash
# Every simulation run: URDFs with the 0.25 kg payload in the right hand, each scenario per tier with and without
# the shoulder balancer, and the push test again with two 25 lb sandbags on the skirt.
cd "$(dirname "$0")/../../.."
PY=~/.local/opt/jj-mech/bin/python
ISAAC=~/.local/opt/isaacsim-6.2/bin/python
export OMNI_KIT_ACCEPT_EULA=YES
run() { $ISAAC cad/mech/sim/run_sim.py "$@" 2>&1 | grep -E "^done|py stderr" | head -3; }
for t in a b c; do
  $PY cad/mech/sim/make_urdf.py $t --payload 0.25 | tail -1
  $PY cad/mech/sim/make_urdf.py $t --payload 0.25 --sandbags 2 | tail -1
  for s in hold wave reach estop; do run $t $s; run $t $s --balancer; done
  run $t push; run $t push --balancer; run "$t+sandbags2" push --balancer
done
