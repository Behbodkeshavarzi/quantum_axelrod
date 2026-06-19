import numpy as np

from qaxelrod.quantum_ipd import action_unitary, entangler, expected_payoffs, outcome_probabilities


def test_probabilities_normalize():
    units = [action_unitary("C", lift="phase"), action_unitary("D", lift="phase")]
    probs = outcome_probabilities(units, gamma=np.pi / 4)
    assert np.isclose(probs.sum(), 1.0)
    assert np.all(probs >= -1e-12)


def test_classical_lift_recovers_classical_payoffs_without_noise():
    cc = [action_unitary("C", lift="classical"), action_unitary("C", lift="classical")]
    cd = [action_unitary("C", lift="classical"), action_unitary("D", lift="classical")]
    dc = [action_unitary("D", lift="classical"), action_unitary("C", lift="classical")]
    dd = [action_unitary("D", lift="classical"), action_unitary("D", lift="classical")]
    for gamma in [0.0, np.pi / 8, np.pi / 4, np.pi / 2]:
        assert np.allclose(expected_payoffs(cc, gamma), [3.0, 3.0])
        assert np.allclose(expected_payoffs(cd, gamma), [0.0, 5.0])
        assert np.allclose(expected_payoffs(dc, gamma), [5.0, 0.0])
        assert np.allclose(expected_payoffs(dd, gamma), [1.0, 1.0])


def test_zz_on_zero_state_is_not_used_as_entangler():
    J = entangler(2, np.pi / 3)
    psi0 = np.array([1, 0, 0, 0], dtype=complex)
    out = J @ psi0
    # A proper EWL entangler creates nonzero amplitude on |11>.
    assert abs(out[3]) > 0.1
