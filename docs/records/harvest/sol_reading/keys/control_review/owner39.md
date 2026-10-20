# owner39 controls — private lead review

Pixel review is required before readers start. Expected calls are planted checks, not new ink adjudication.

## k6b5c988347

Shown: {"A": "αυτης", "B": "ὰυτης", "C": "ᾶυτης", "D": "άυτης"}

Expected: `{"form": "αυτής", "heads": {"breathing": "none", "accent": "none", "diaeresis": "none", "subscript": "none"}, "choice": "literal"}`

## k7e52fd39d5

Shown: {"A": "που", "B": "πὸυ", "C": "πο͂υ", "D": "πόυ"}

Expected: `{"form": "που", "heads": {"breathing": "none", "accent": "none", "diaeresis": "none", "subscript": "none"}, "choice": "A"}`

## k18921690a3

Shown: {"A": "τὴ", "B": "τῆ", "C": "τή", "D": "τη"}

Expected: `{"form": "τη", "heads": {"breathing": "none", "accent": "none", "diaeresis": "none", "subscript": "none"}, "choice": "D"}`

## k773f4330d0

Shown: {"A": "στὰδιο", "B": "στᾶδιο", "C": "στάδιο", "D": "σταδιο"}

Expected: `{"form": "στάδιο", "heads": {"breathing": "none", "accent": "acute", "diaeresis": "none", "subscript": "none"}, "choice": "C"}`

