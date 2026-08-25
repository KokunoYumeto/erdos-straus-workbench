import R107DeficitProgression.Difference
import R107DeficitProgression.FullSupport

/-!
# The mod-107 deficit progression

This root module assembles kernel-reduced finite certificates for the
support-level observation prompted by the public community lead from
`u/CommonCareful3149`.  The companion TeX note supplies the explicit
coordinate maps and the Python certificate independently replays the same
finite sets.  No priority or global Erdős--Straus claim is made here.

The larger decision proofs are separated into modules to keep peak replay
memory bounded.  They use ordinary `decide` with an explicit recursion bound,
not `native_decide`.
-/

namespace R107DeficitProgression

#print axioms reducedSupport_card
#print axioms deficit_eq_progression
#print axioms deficit_card
#print axioms differenceSet_card
#print axioms six_not_mem_differenceSet
#print axioms translatedDeficits_disjoint
#print axioms oddSheet_saturated
#print axioms factorLogarithms
#print axioms fullSupport_card
#print axioms middleTarget_mem
#print axioms exteriorTarget_not_mem

end R107DeficitProgression
