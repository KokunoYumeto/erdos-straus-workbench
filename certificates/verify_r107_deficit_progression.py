#!/usr/bin/env python3
"""Deterministic certificate for the R=107 deficit-progression observation.

The calculation is deliberately finite and self-contained.  It works in
discrete-log coordinates for the multiplicative group of F_107, with 2 as
primitive generator.  The three even logarithms are divided by 2 to obtain
coordinates in Z/53Z; the unique odd logarithm then produces two translates
of that reduced support on the odd parity sheet.

This certificate proves only the displayed R=107 support statements.  It
does not establish novelty, a general shell theorem, or the Erdos--Straus
conjecture.
"""

from __future__ import annotations

from itertools import product
from math import gcd, isqrt
from typing import Iterable, TypeVar


T = TypeVar("T")


def require(condition: bool, message: str) -> None:
    """Raise a stable error even when Python is invoked with ``-O``."""

    if not condition:
        raise RuntimeError(message)


def require_equal(actual: T, expected: T, label: str) -> None:
    if actual != expected:
        raise RuntimeError(f"{label}: expected {expected!r}, got {actual!r}")


def discrete_log_table(generator: int, prime: int) -> dict[int, int]:
    require(prime > 2, "prime must be odd")
    table: dict[int, int] = {}
    value = 1
    for exponent in range(prime - 1):
        require(value not in table, "generator cycle repeated too early")
        table[value] = exponent
        value = value * generator % prime
    require_equal(value, 1, "generator cycle endpoint")
    require_equal(len(table), prime - 1, "generator order")
    require_equal(set(table), set(range(1, prime)), "generator image")
    return table


def modular_sumset(
    coefficients: Iterable[int],
    coefficient_ranges: Iterable[Iterable[int]],
    modulus: int,
) -> set[int]:
    coeffs = tuple(coefficients)
    ranges = tuple(tuple(values) for values in coefficient_ranges)
    require_equal(len(coeffs), len(ranges), "sumset arity")
    return {
        sum(coefficient * value for coefficient, value in zip(coeffs, vector))
        % modulus
        for vector in product(*ranges)
    }


def translate(values: set[int], offset: int, modulus: int) -> set[int]:
    return {(value + offset) % modulus for value in values}


def difference_set(values: set[int], modulus: int) -> set[int]:
    return {(left - right) % modulus for left in values for right in values}


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    return all(value % divisor != 0 for divisor in range(3, isqrt(value) + 1, 2))


def main() -> None:
    prime = 107
    p_star = 8_803_369
    a_star = 2_200_869
    log_modulus = prime - 1
    quotient_modulus = log_modulus // 2
    generator = 2
    require(is_prime(prime), "107 is not prime")
    require(is_prime(p_star), "record integer p is not prime")
    require_equal((p_star + prime) // 4, a_star, "residual carrier")
    require_equal(3**2 * 11**2 * 43 * 47, a_star, "carrier factorization")
    require_equal(gcd(a_star, prime), 1, "carrier/modulus coprimality")
    logs = discrete_log_table(generator, prime)

    factor_logs = tuple(logs[factor] for factor in (3, 11, 43, 47))
    require_equal(factor_logs, (70, 22, 59, 66), "factor logarithms")
    require_equal(pow(generator, 53, prime), prime - 1, "logarithm of -1")
    require_equal(logs[pow(p_star, -1, prime) * (prime - 1) % prime], 60,
                  "exterior target logarithm")

    even_ranges = (range(-2, 3), range(-2, 3), range(-1, 2))
    even_support = modular_sumset((70, 22, 66), even_ranges, log_modulus)
    require(all(value % 2 == 0 for value in even_support),
            "even-factor support left the even logarithm subgroup")

    # h : 2 Z/106 Z -> Z/53 Z, h(2x)=x.  Integer division is valid for
    # the canonical even representatives 0,2,...,104.
    reduced_support = {value // 2 for value in even_support}
    direct_reduced_support = modular_sumset((35, 11, 33), even_ranges,
                                            quotient_modulus)
    require_equal(reduced_support, direct_reduced_support,
                  "half-log quotient map")
    require_equal(len(reduced_support), 43, "reduced support cardinality")

    deficit = set(range(quotient_modulus)) - reduced_support
    progression = {(23 + 42 * index) % quotient_modulus for index in range(10)}
    require_equal(deficit, progression, "ten-point deficit progression")
    require_equal(len(deficit), 10, "deficit cardinality")

    differences = difference_set(deficit, quotient_modulus)
    expected_differences = {
        (42 * offset) % quotient_modulus for offset in range(-9, 10)
    }
    require_equal(differences, expected_differences,
                  "progression difference set")
    require_equal(len(differences), 19, "sharp difference-set cardinality")
    require_equal(pow(42, -1, quotient_modulus), 24,
                  "inverse of the progression step")
    require_equal(24 * 6 % quotient_modulus, 38,
                  "coordinate of translate gap")
    require(6 not in differences, "translate gap unexpectedly lies in D-D")

    # The unique odd factor has centered support {0,59,-59}={0,59,47}.
    # On the odd sheet psi(2x+1)=x, adding 59 and 47 induces translations
    # by 29 and 23 respectively.
    missing_after_59 = translate(deficit, 29, quotient_modulus)
    missing_after_47 = translate(deficit, 23, quotient_modulus)
    require(missing_after_59.isdisjoint(missing_after_47),
            "the two translated deficits are not disjoint")
    odd_sheet = (
        translate(reduced_support, 29, quotient_modulus)
        | translate(reduced_support, 23, quotient_modulus)
    )
    require_equal(odd_sheet, set(range(quotient_modulus)),
                  "odd-sheet saturation")

    # The corpus's Legendre-sheet coordinate sends a nonresidue u to the
    # half-log of -u.  In that coordinate the same two sheets are A+3 and
    # A-3.  This differs from the odd-exponent coordinate by a translation,
    # while preserving the decisive gap 6.
    canonical_positive_offset = logs[(-43) % prime] // 2
    canonical_negative_offset = logs[(-pow(43, -1, prime)) % prime] // 2
    require_equal(canonical_positive_offset, 3, "canonical + sheet offset")
    require_equal(canonical_negative_offset, 50, "canonical - sheet offset")
    canonical_odd_sheet = (
        translate(reduced_support, canonical_positive_offset, quotient_modulus)
        | translate(reduced_support, canonical_negative_offset, quotient_modulus)
    )
    require_equal(canonical_odd_sheet, set(range(quotient_modulus)),
                  "canonical-coordinate odd-sheet saturation")

    full_ranges = (
        range(-2, 3),
        range(-2, 3),
        range(-1, 2),
        range(-1, 2),
    )
    full_support = modular_sumset(factor_logs, full_ranges, log_modulus)
    missing_exponents = set(range(log_modulus)) - full_support
    doubled_deficit = {(2 * value) % log_modulus for value in deficit}
    require_equal(missing_exponents, doubled_deficit,
                  "full-cloud missing exponents")
    require_equal(
        missing_exponents,
        {2, 20, 24, 42, 46, 60, 64, 82, 86, 104},
        "published-corpus R=107 missing-exponent list",
    )
    require_equal(len(full_support), 96, "full support cardinality")
    residue_support = {pow(generator, exponent, prime) for exponent in full_support}
    quadratic_nonresidues = {
        value for value in range(1, prime)
        if pow(value, (prime - 1) // 2, prime) == prime - 1
    }
    represented_nonresidues = {
        value for value in residue_support
        if pow(value, (prime - 1) // 2, prime) == prime - 1
    }
    require_equal(represented_nonresidues, quadratic_nonresidues,
                  "residue-level nonresidue saturation")
    require(53 in full_support, "middle target -1 is not represented")
    require(60 not in full_support, "exterior target should be absent")

    fibers: dict[int, list[tuple[int, int, int, int]]] = {53: [], 60: []}
    for vector in product(*full_ranges):
        exponent = sum(
            coefficient * value
            for coefficient, value in zip(factor_logs, vector)
        ) % log_modulus
        if exponent in fibers:
            fibers[exponent].append(vector)
    require_equal(
        fibers[53],
        [(-2, 0, -1, -1), (2, 0, 1, 1)],
        "middle-target fibers",
    )
    require_equal(fibers[60], [], "exterior-target fibers")

    print("certificate=R107-deficit-progression")
    print("status=PASS")
    print("factor_logs=(70,22,59,66)")
    print("reduced_support_cardinality=43")
    print("deficit={23+42*j mod 53:0<=j<=9}")
    print("deficit_cardinality=10")
    print("difference_set_cardinality=19")
    print("translate_gap_6_in_D_minus_D=false")
    print("canonical_sheet_offsets=(3,-3)")
    print("odd_sheet_cardinality=53")
    print("full_support_cardinality=96")
    print("middle_target_log_53_fibers=2")
    print("exterior_target_log_60_fibers=0")
    print("scope=one exact R=107 support calculation; no novelty or global claim")


if __name__ == "__main__":
    main()
