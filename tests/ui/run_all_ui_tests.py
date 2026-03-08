#!/usr/bin/env python
"""
Run All UI Tests
Main entry point for executing the complete UI test suite
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

# Import test modules
from tests.ui.base_ui_test import TestRunner
from tests.ui.test_immeuble_crud import run_immeuble_tests
from tests.ui.test_locataire_crud import run_locataire_tests
from tests.ui.test_bureau_crud import run_bureau_tests
from tests.ui.test_contrat_crud import run_contrat_tests
from tests.ui.test_paiement_crud import run_paiement_tests
from tests.ui.test_deletion_constraints import run_deletion_constraint_tests


def run_all_ui_tests():
    """Run the complete UI test suite"""
    print("="*60)
    print("  UI INTEGRATION TEST SUITE")
    print("  Gestion Locative Pro")
    print("="*60)
    
    # Create test runner
    runner = TestRunner()
    
    try:
        # Setup
        runner.setup()
        
        # Run all entity tests
        run_immeuble_tests(runner)
        run_locataire_tests(runner)
        run_bureau_tests(runner)
        run_contrat_tests(runner)
        run_paiement_tests(runner)
        
        # Run deletion constraint tests
        run_deletion_constraint_tests(runner)
        
        # Print final report
        success = runner.print_report()
        
        if success:
            print("\n✓✓✓ ALL TESTS PASSED! ✓✓✓")
            return 0
        else:
            print("\n✗✗✗ SOME TESTS FAILED ✗✗✗")
            return 1
            
    except Exception as e:
        print(f"\n✗ Test suite error: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        # Cleanup
        runner.teardown()


if __name__ == "__main__":
    exit_code = run_all_ui_tests()
    sys.exit(exit_code)
