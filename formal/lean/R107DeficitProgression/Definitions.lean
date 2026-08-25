import Mathlib

/-! Shared finite-set definitions for the mod-107 deficit certificate. -/

namespace R107DeficitProgression

def centeredFive53 : List (ZMod 53) := [51, 52, 0, 1, 2]
def centeredThree53 : List (ZMod 53) := [52, 0, 1]

/-- The support of the three even factor logarithms after applying
`h(2x)=x` from the even subgroup of `Z/106Z` to `Z/53Z`. -/
def reducedSupport : Finset (ZMod 53) :=
  (centeredFive53.flatMap fun a =>
    centeredFive53.flatMap fun b =>
      centeredThree53.map fun c => 35 * a + 11 * b + 33 * c).toFinset

/-- The complement of the reduced even-factor support. -/
def deficit : Finset (ZMod 53) := Finset.univ \ reducedSupport

/-- The ten-term arithmetic progression announced in the community lead. -/
def deficitProgression : Finset (ZMod 53) :=
  ((List.range 10).map fun j => 23 + 42 * (j : ZMod 53)).toFinset

def differenceSet (A : Finset (ZMod 53)) : Finset (ZMod 53) :=
  A.biUnion fun x => A.image fun y => x - y

def translate (A : Finset (ZMod 53)) (t : ZMod 53) : Finset (ZMod 53) :=
  A.image fun x => x + t

def centeredFive106 : List (ZMod 106) := [104, 105, 0, 1, 2]
def centeredThree106 : List (ZMod 106) := [105, 0, 1]

/-- The complete centered exponent support for logs `(70,22,59,66)`. -/
def fullSupport : Finset (ZMod 106) :=
  (centeredFive106.flatMap fun a =>
    centeredFive106.flatMap fun b =>
      centeredThree106.flatMap fun c =>
        centeredThree106.map fun d => 70 * a + 22 * b + 59 * c + 66 * d).toFinset

end R107DeficitProgression
