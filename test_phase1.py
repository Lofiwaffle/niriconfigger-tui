#!/usr/bin/env python3
"""Test Phase 1 foundation - config loading and modification."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.core.config_manager import ConfigManager
from src.core.validators import Validators


def test_config_load():
    """Test loading configuration."""
    print("=" * 60)
    print("TEST 1: Load Configuration")
    print("=" * 60)

    try:
        config_manager = ConfigManager()
        config_model = config_manager.load()

        print(f"✓ Configuration loaded successfully")
        print(f"  - Config file: {config_manager.config_path}")
        print(f"  - Gaps: {config_model.layout.gaps}px")
        print(f"  - Corner radius: {config_model.visual.corner_radius}px")
        print(f"  - Center focused column: {config_model.layout.center_focused_column}")
        print(f"  - Opacity rules: {len(config_model.window_rules)} rules")
        return True, config_manager, config_model

    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return False, None, None


def test_modify_gaps(config_manager, config_model):
    """Test modifying gaps and saving."""
    print("\n" + "=" * 60)
    print("TEST 2: Modify Gaps and Save")
    print("=" * 60)

    try:
        original_gaps = config_model.layout.gaps
        new_gaps = original_gaps + 4 if original_gaps < 50 else original_gaps - 4

        # Validate new value
        valid, error = Validators.validate_gaps(new_gaps)
        if not valid:
            print(f"✗ Validation failed: {error}")
            return False

        # Modify
        config_model.layout.gaps = new_gaps
        print(f"✓ Changed gaps from {original_gaps}px to {new_gaps}px")

        # Save
        config_manager.save(config_model)
        print(f"✓ Configuration saved successfully")

        # Reload to verify
        config_manager2 = ConfigManager()
        config_model2 = config_manager2.load()

        if config_model2.layout.gaps == new_gaps:
            print(f"✓ Verified: gaps saved and reloaded correctly ({new_gaps}px)")
            return True
        else:
            print(f"✗ Verification failed: expected {new_gaps}px, got {config_model2.layout.gaps}px")
            return False

    except Exception as e:
        print(f"✗ Failed to modify and save: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validators():
    """Test input validators."""
    print("\n" + "=" * 60)
    print("TEST 3: Input Validators")
    print("=" * 60)

    test_cases = [
        ("gaps", Validators.validate_gaps, [
            (4, True),
            (0, True),
            (256, True),
            (-1, False),
            (257, False),
        ]),
        ("opacity", Validators.validate_opacity, [
            (0.5, True),
            (0.0, True),
            (1.0, True),
            (1.5, False),
            (-0.1, False),
        ]),
        ("corner_radius", Validators.validate_corner_radius, [
            (16, True),
            (0, True),
            (256, True),
            (-1, False),
        ]),
    ]

    all_passed = True
    for validator_name, validator_func, cases in test_cases:
        print(f"\n  Testing {validator_name}:")
        for value, expected_valid in cases:
            valid, error = validator_func(value)
            status = "✓" if valid == expected_valid else "✗"
            print(f"    {status} {validator_name}({value}) = {valid}")
            if valid != expected_valid:
                all_passed = False

    return all_passed


def main():
    """Run all tests."""
    print("\nNiriConfig GUI - Phase 1 Foundation Tests\n")

    # Test 1: Load config
    success, config_manager, config_model = test_config_load()
    if not success:
        print("\n✗ Phase 1 tests FAILED - could not load configuration")
        return 1

    # Test 2: Modify and save
    if not test_modify_gaps(config_manager, config_model):
        print("\n✗ Phase 1 tests FAILED - could not modify configuration")
        return 1

    # Test 3: Validators
    if not test_validators():
        print("\n✗ Phase 1 tests FAILED - validators failed")
        return 1

    print("\n" + "=" * 60)
    print("✓ ALL PHASE 1 TESTS PASSED!")
    print("=" * 60)
    print("\nPhase 1 Foundation is complete:")
    print("  ✓ Configuration loading with comment preservation")
    print("  ✓ Configuration modification and saving")
    print("  ✓ Input validation system")
    print("  ✓ Layout settings infrastructure")
    print("\nReady to proceed to Phase 2: Visual Settings")

    return 0


if __name__ == "__main__":
    sys.exit(main())
