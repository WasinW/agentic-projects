"""Register the default (mock) adapters into the seam registry on import."""
from app.core.adapters import register
from app.adapters.mock_source import MockSource
from app.adapters.mock_generator import get_generator
from app.adapters.mock_publisher import MockPublisher
from app.production.runner import RecipeGenerator
from app.services.scorer import ComboScorer

# ── register defaults. Adding a real impl later = one more register() call. ──
register("source", "mock", MockSource())

# generator seam: the default `mock` is now the multi-step Content Production
# pipeline (07 §2.5) via RecipeGenerator — it BEcomes the registered generator and
# runs the per-media recipe with MOCK sub-adapters ($0, no keys). The legacy
# single-step generator stays available under "single" for comparison/fallback.
register("generator", "mock", RecipeGenerator())
register("generator", "single", get_generator())   # legacy 1-step (respects GENERATOR env)
register("generator", "real", get_generator())      # real stub path (needs keys)

register("publisher", "mock", MockPublisher())
register("scorer", "zscore", ComboScorer())
