import R107DeficitProgression.Definitions

namespace R107DeficitProgression

set_option maxRecDepth 100000

theorem factorLogarithms :
    (2 : ZMod 107) ^ 70 = 3 ∧
    (2 : ZMod 107) ^ 22 = 11 ∧
    (2 : ZMod 107) ^ 59 = 43 ∧
    (2 : ZMod 107) ^ 66 = 47 := by
  decide

theorem fullSupport_card : fullSupport.card = 96 := by
  decide

/-- The middle target `-1`, whose logarithm is 53, is represented. -/
theorem middleTarget_mem : (53 : ZMod 106) ∈ fullSupport := by
  decide

/-- The exterior target in this carrier, whose logarithm is 60, is absent. -/
theorem exteriorTarget_not_mem : (60 : ZMod 106) ∉ fullSupport := by
  decide

end R107DeficitProgression
