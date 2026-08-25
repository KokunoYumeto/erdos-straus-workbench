import R107DeficitProgression.Reduced

namespace R107DeficitProgression

set_option maxRecDepth 100000

/-- The progression has the sharp difference-set size `2|D|-1=19`. -/
theorem differenceSet_card : (differenceSet deficit).card = 19 := by
  decide

/-- The gap between the two odd-sheet translations is not in `D-D`. -/
theorem six_not_mem_differenceSet : (6 : ZMod 53) ∉ differenceSet deficit := by
  decide

/-- Equivalently, the two translated deficit sets are disjoint. -/
theorem translatedDeficits_disjoint :
    Disjoint (translate deficit 29) (translate deficit 23) := by
  decide

/-- The two translates induced by the `±59` odd logarithm saturate the
entire odd-sheet coordinate copy of `Z/53Z`. -/
theorem oddSheet_saturated :
    translate reducedSupport 29 ∪ translate reducedSupport 23 = Finset.univ := by
  decide

end R107DeficitProgression
