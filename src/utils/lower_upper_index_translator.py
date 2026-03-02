SUPERSCRIPT_MAP = str.maketrans(
    "0123456789+-=()n",
    "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿ"
)

def to_superscript(text: str) -> str:
    return str(text).translate(SUPERSCRIPT_MAP)


SUBSCRIPT_MAP = str.maketrans(
    "0123456789+-=()aehijklmnoprstuvx",
    "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ"
)

def to_subscript(text: str) -> str:
    return str(text).translate(SUBSCRIPT_MAP)