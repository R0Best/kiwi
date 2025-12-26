import llvmlite.binding as llvm
import pytest


@pytest.fixture(scope="session")
def lexer_adapter():
    """Returns the class, not instance, as per Lark requirements"""
    return


@pytest.fixture(scope="session")
def parser():
    """
    Initializes the Lark parser once for the whole test session.
    This saves ~0.5s per test.
    """
    return


@pytest.fixture
def jit_engine():
    """
    Initializes the LLVM JIT engine.
    (You would import your JIT setup function here)
    """

    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()
    return llvm
