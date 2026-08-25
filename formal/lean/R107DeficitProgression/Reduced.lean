import R107DeficitProgression.Definitions

namespace R107DeficitProgression

set_option maxRecDepth 100000

/-- The reduced support has 43 of the 53 quotient coordinates. -/
theorem reducedSupport_card : reducedSupport.card = 43 := by
  decide

/-- Its ten-point complement is exactly `23+42j`, `0 ≤ j ≤ 9`. -/
theorem deficit_eq_progression : deficit = deficitProgression := by
  decide

theorem deficit_card : deficit.card = 10 := by
  decide

end R107DeficitProgression
