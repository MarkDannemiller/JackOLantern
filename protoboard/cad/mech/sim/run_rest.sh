#!/bin/bash
set -e
cd "$(dirname "$0")/../../.."
export OMNI_KIT_ACCEPT_EULA=YES
ISAAC=~/.local/opt/isaacsim-6.2/bin/python
~/.local/opt/jj-mech/bin/python cad/mech/sim/make_urdf.py c --payload 0.25 | tail -1
for t in a b c; do
  for s in push; do $ISAAC cad/mech/sim/run_sim.py $t $s 2>&1 | grep -E "^done|py stderr" | head -3; done
done
for s in hold wave reach estop; do
  $ISAAC cad/mech/sim/run_sim.py c $s 2>&1 | grep -E "^done|py stderr" | head -3
  $ISAAC cad/mech/sim/run_sim.py c $s --balancer 2>&1 | grep -E "^done|py stderr" | head -3
done
