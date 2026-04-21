import pytest
from converters import ConverterInterface
from registry.registry import ConverterRegistry


# ── Stub converters for isolated testing ─────────────────────────────

class _ImageConverter(ConverterInterface):
    supported_input_formats = {"png", "jpeg", "webp"}
    supported_output_formats = {"png", "jpeg", "webp", "gif"}
    formats_with_qualities = {"jpeg"}

    @classmethod
    def can_register(cls) -> bool:
        return True


class _AudioConverter(ConverterInterface):
    supported_input_formats = {"mp3", "wav"}
    supported_output_formats = {"mp3", "wav", "ogg"}

    @classmethod
    def can_register(cls) -> bool:
        return True


class _VideoConverter(ConverterInterface):
    supported_input_formats = {"mp4", "avi"}
    supported_output_formats = {"mp4", "avi", "mp3"}
    formats_with_qualities = {"mp4", "avi"}

    @classmethod
    def can_register(cls) -> bool:
        return True


class _UnregisterableConverter(ConverterInterface):
    supported_input_formats = {"xyz"}
    supported_output_formats = {"abc"}

    @classmethod
    def can_register(cls) -> bool:
        return False


@pytest.fixture
def empty_registry():
    """A registry with auto-discovery disabled (no real converters)."""
    reg = ConverterRegistry.__new__(ConverterRegistry)
    reg.converters = {}
    reg.input_format_map = {}
    reg.output_format_map = {}
    return reg


@pytest.fixture
def stub_registry(empty_registry):
    """A registry pre-loaded with the two stub converters."""
    empty_registry.register_converter(_ImageConverter)
    empty_registry.register_converter(_AudioConverter)
    empty_registry.register_converter(_VideoConverter)
    return empty_registry


# ── register_converter ───────────────────────────────────────────────

def test_register_converter_adds_to_converters(empty_registry):
    empty_registry.register_converter(_ImageConverter)
    assert "_ImageConverter" in empty_registry.converters


def test_register_converter_populates_input_map(empty_registry):
    empty_registry.register_converter(_ImageConverter)
    for fmt in _ImageConverter.supported_input_formats:
        assert _ImageConverter in empty_registry.input_format_map[fmt]


def test_register_converter_populates_output_map(empty_registry):
    empty_registry.register_converter(_ImageConverter)
    for fmt in _ImageConverter.supported_output_formats:
        assert _ImageConverter in empty_registry.output_format_map[fmt]


# ── get_converter ────────────────────────────────────────────────────

def test_get_converter_found(stub_registry):
    assert stub_registry.get_converter("_ImageConverter") is _ImageConverter


def test_get_converter_not_found(stub_registry):
    assert stub_registry.get_converter("NonExistent") is None


# ── get_formats ──────────────────────────────────────────────────────

def test_get_formats_returns_union(stub_registry):
    fmts = stub_registry.get_formats()
    expected = (
        _ImageConverter.supported_input_formats
        | _ImageConverter.supported_output_formats
        | _AudioConverter.supported_input_formats
        | _AudioConverter.supported_output_formats
        | _VideoConverter.supported_input_formats
        | _VideoConverter.supported_output_formats
    )
    assert fmts == expected
    assert "webvideo" not in fmts


def test_get_formats_empty(empty_registry):
    assert empty_registry.get_formats() == set()


# ── get_normalized_format ────────────────────────────────────────────

def test_normalized_format_alias(stub_registry):
    assert stub_registry.get_normalized_format("jpg") == "jpeg"
    assert stub_registry.get_normalized_format("yml") == "yaml"


def test_normalized_format_passthrough(stub_registry):
    assert stub_registry.get_normalized_format("png") == "png"


def test_normalized_format_lowercased(stub_registry):
    assert stub_registry.get_normalized_format("PNG") == "png"


# ── get_converters_for_input_format ──────────────────────────────────

def test_converters_for_input_format(stub_registry):
    result = stub_registry.get_converters_for_input_format("png")
    assert _ImageConverter in result


def test_converters_for_input_format_alias(stub_registry):
    # "jpg" should resolve to "jpeg" via alias
    result = stub_registry.get_converters_for_input_format("jpg")
    assert _ImageConverter in result


def test_converters_for_input_format_unknown(stub_registry):
    assert stub_registry.get_converters_for_input_format("xyz123") == []


def test_converters_for_webvideo_input(stub_registry):
    result = stub_registry.get_converters_for_input_format("webvideo")
    assert _VideoConverter in result


# ── get_converters_for_output_format ─────────────────────────────────

def test_converters_for_output_format(stub_registry):
    result = stub_registry.get_converters_for_output_format("ogg")
    assert _AudioConverter in result


def test_converters_for_output_format_unknown(stub_registry):
    assert stub_registry.get_converters_for_output_format("xyz123") == []


# ── get_converter_for_conversion ─────────────────────────────────────

def test_converter_for_conversion_found(stub_registry):
    conv = stub_registry.get_converter_for_conversion("png", "jpeg")
    assert conv is _ImageConverter


def test_converter_for_conversion_alias_input(stub_registry):
    conv = stub_registry.get_converter_for_conversion("jpg", "webp")
    assert conv is _ImageConverter


def test_converter_for_conversion_webvideo_input(stub_registry):
    conv = stub_registry.get_converter_for_conversion("webvideo", "mp3")
    assert conv is _VideoConverter


def test_converter_for_conversion_none(stub_registry):
    # No converter bridges image → audio
    assert stub_registry.get_converter_for_conversion("png", "mp3") is None


# ── list_converters ──────────────────────────────────────────────────

def test_list_converters(stub_registry):
    listing = stub_registry.list_converters()
    assert "_ImageConverter" in listing
    assert "_AudioConverter" in listing
    assert set(listing["_ImageConverter"]) == _ImageConverter.supported_input_formats


def test_list_converters_empty(empty_registry):
    assert empty_registry.list_converters() == {}


# ── get_compatible_formats_and_qualities ─────────────────────────────

def test_compatible_formats_and_qualities(stub_registry):
    compat = stub_registry.get_compatible_formats_and_qualities("png")
    # png input on _ImageConverter can output jpeg, webp, gif (everything except png itself)
    assert "jpeg" in compat
    assert "webp" in compat
    assert "gif" in compat
    assert "png" not in compat


def test_compatible_formats_quality_options(stub_registry):
    compat = stub_registry.get_compatible_formats_and_qualities("png")
    # jpeg is in formats_with_qualities → should have quality options
    assert len(compat["jpeg"]) > 0
    # gif is NOT in formats_with_qualities
    assert compat["gif"] == set()


def test_webvideo_compatible_formats_include_mp4(stub_registry):
    compat = stub_registry.get_compatible_formats_and_qualities("webvideo")
    assert "mp4" in compat
    assert "avi" in compat
    assert "mp3" in compat


def test_webvideo_mp4_quality_options(stub_registry):
    compat = stub_registry.get_compatible_formats_and_qualities("webvideo")
    assert len(compat["mp4"]) > 0


def test_compatible_formats_unknown_input(stub_registry):
    assert stub_registry.get_compatible_formats_and_qualities("xyz123") == {}


# ── get_format_compatibility_matrix ──────────────────────────────────

def test_format_compatibility_matrix_keys(stub_registry):
    matrix = stub_registry.get_format_compatibility_matrix()
    # Every registered format should appear as a key
    for fmt in stub_registry.get_formats():
        assert fmt in matrix


def test_format_compatibility_matrix_values(stub_registry):
    matrix = stub_registry.get_format_compatibility_matrix()
    # png can become jpeg/webp/gif
    assert "jpeg" in matrix["png"]
    assert "gif" in matrix["png"]


# ── auto-registration with skip_unregisterable ───────────────────────

def test_skip_unregisterable(monkeypatch):
    """_auto_register with skip_unregisterable=True should skip converters that return can_register()=False."""
    import inspect
    import converters as converters_mod

    # Patch inspect.getmembers to return only our stubs when called on the converters module
    original_getmembers = inspect.getmembers

    def _patched_getmembers(obj, predicate=None):
        if obj is converters_mod:
            members = [("_ImageConverter", _ImageConverter), ("_UnregisterableConverter", _UnregisterableConverter)]
            if predicate:
                return [(n, v) for n, v in members if predicate(v)]
            return members
        return original_getmembers(obj, predicate)

    monkeypatch.setattr(inspect, "getmembers", _patched_getmembers)

    reg = ConverterRegistry.__new__(ConverterRegistry)
    reg.converters = {}
    reg.input_format_map = {}
    reg.output_format_map = {}
    reg._auto_register(skip_unregisterable=True)

    assert "_ImageConverter" in reg.converters
    assert "_UnregisterableConverter" not in reg.converters


# ── singleton registry smoke test ────────────────────────────────────

def test_singleton_registry_has_converters():
    """The module-level `registry` singleton should have discovered real converters."""
    from registry import registry
    assert len(registry.converters) > 0
    assert len(registry.get_formats()) > 0
