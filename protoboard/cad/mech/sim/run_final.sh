#!/bin/bash
# The operating set as built: shoulder balancer on, servo torque limits so no belt passes its rating (--belt-limit).
# wave and reach are the show gestures; hold (arm straight out sideways, then forward) is the stress test; estop
# cuts the servos at full reach. wave without the balancer shows what the balancer buys. B wave also records video.
cd "$(dirname "$0")/../../.."
PY=~/.local/opt/jj-mech/bin/python
ISAAC=~/.local/opt/isaacsim-6.2/bin/python
export OMNI_KIT_ACCEPT_EULA=YES
run() { $ISAAC cad/mech/sim/run_sim.py "$@" 2>&1 | grep -E "^done|py stderr|Error" | head -3; }
for t in a b c; do
  $PY cad/mech/sim/make_urdf.py $t --payload 0.25 | tail -1
  for s in wave reach hold estop; do run $t $s --balancer --belt-limit; done
  run $t wave --belt-limit
done
run b wave --balancer --belt-limit --video
python3 cad/mech/sim/report.py > /dev/null
