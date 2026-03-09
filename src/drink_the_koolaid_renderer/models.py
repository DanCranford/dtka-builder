from pydantic import BaseModel, Field


# ── Card models ─────────────────────────────────────────────────────────────

class Card(BaseModel):
    """A single card definition. `copies` drives how many physical prints to make."""
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    type: str = Field(min_length=1)
    # number of physical copies to print (expanded at render time)
    copies: int = Field(default=1, ge=1)

    # type-band metadata
    cost: str = ""          # e.g. "2S + 1$" — apostle / artifact / doctrine
    tag: str = ""           # e.g. "Age 1" — age cards only (shown instead of cost)

    # effect area
    effect_tag: str = ""    # e.g. "ACTIVE · Once per turn" (non-event/herald/age types)
    timing: str = ""        # event cards only: "INSTANT — your turn" / "INTERRUPT — any turn"
    effect: str = ""        # main effect body (HTML ok); not used for mission type
    condition: str = ""     # mission only — condition text (HTML ok)
    loss: str = ""          # doctrine only — loss condition body (HTML ok)
    reward: str = ""        # mission only — reward body (HTML ok)

    # flavour + art
    flavour: str = ""
    art: str = ""           # path/URL to art image, or "" for placeholder


class CardCollection(BaseModel):
    cards: list[Card] = Field(default_factory=list)


# ── Prophet / Placemat models ────────────────────────────────────────────────

class Ability(BaseModel):
    """A single ability row displayed on the prophet mat."""
    tag: str = Field(min_length=1)   # e.g. "Primary — Prophet Phase, once per turn"
    text: str = Field(min_length=1)  # may contain inline HTML (<strong> etc.)
    style: str = ""                  # "" | "penalty" | "resurrection"


class WinCondition(BaseModel):
    badge: str = Field(min_length=1)   # e.g. "Win 1"
    text: str = Field(min_length=1)    # e.g. "Loved — Seekers in pool"
    target: str = Field(min_length=1)  # e.g. "50S"
    progress: list[int] = Field(default_factory=list)  # milestone tick values


class CardSlot(BaseModel):
    num: str = Field(min_length=1)  # e.g. "D1", "A2", "R3"
    locked: bool = False


class SlotGroup(BaseModel):
    doctrine: list[CardSlot] = Field(default_factory=list)
    apostle: list[CardSlot] = Field(default_factory=list)
    artifact: list[CardSlot] = Field(default_factory=list)


class TurnPhase(BaseModel):
    name: str = Field(min_length=1)  # e.g. "Upkeep"
    note: str = ""                   # e.g. "+2S +1D<br>Draw 2"


class Prophet(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)            # e.g. "The Reverend"
    epithet: str = ""                          # quoted flavour line
    build_path: str = ""                       # e.g. "S / V Build Path"
    accent_color: str = "#c8882a"              # CSS colour for mat tint
    portrait_image: str = ""                   # path/URL to portrait, or ""
    abilities: list[Ability] = Field(default_factory=list)
    win_conditions: list[WinCondition] = Field(default_factory=list)
    slots: SlotGroup = Field(default_factory=SlotGroup)
    turn_phases: list[TurnPhase] = Field(default_factory=list)
    fallen_text: str = (
        "0S + 0D at End Phase → lose all Apostles &amp; Artifacts. "
        "Pay resurrection cost on Main Phase to return."
    )


class ProphetCollection(BaseModel):
    prophets: list[Prophet] = Field(default_factory=list)
