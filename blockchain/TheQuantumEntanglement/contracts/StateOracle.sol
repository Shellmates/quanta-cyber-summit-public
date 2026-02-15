// SPDX-License-Identifier: MIT
pragma solidity ^0.8.29;

/**
 * @title StateOracle
 * @author 0xkryvon (Lyes Boudjabout)
 * @notice "I see all, but you understand nothing. The oracle is not your friend."
 * @dev "Trying to predict the future? You can't even predict your own transaction failure."
 */
contract StateOracle {
    uint256 private _stateCounter;
    bytes32 private _oracleSecret;
    mapping(uint256 => uint8) private _stateHistory;

    event QuantumStateQueried(uint256 indexed input, uint8 state);
    event QuantumStateVerified(bool valid, uint256 gas);

    /**
     * @notice "Existence is pain, especially for a smart contract."
     */
    constructor() {
        _stateCounter = 0;
        _oracleSecret = keccak256("oracle.quantum.secret");
    }

    /**
     * @notice "Whisper your questions into the void. It might answer. Or it might just laugh."
     */
    function queryState(uint256 input) external returns (uint8 state) {
        uint256 gasRemaining = gasleft();

        // "Chaos is the only constant. Or is it?"
        if (gasRemaining > 100000) {
            state = 42;
        } else if (gasRemaining > 50000 && gasRemaining <= 100000) {
            state = 137;
        } else if (gasRemaining > 30000 && gasRemaining <= 50000) {
            state = uint8((gasRemaining % 200) + 1);
        } else {
            state = 0;
        }

        // "Injecting more entropy just to watch you suffer"
        if (input % 2 == 0) {
            state = uint8((uint256(state) + input) % 256);
        }

        _stateHistory[_stateCounter] = state;
        _stateCounter++;

        emit QuantumStateQueried(input, state);
        return state;
    }

    /**
     * @notice "Are we aligned with the cosmos? Probably not."
     */
    function verifyQuantumState() external returns (bool valid) {
        uint256 gasRemaining = gasleft();

        if (
            (gasRemaining >= 45000 && gasRemaining <= 55000) ||
            gasRemaining >= 95000
        ) {
            valid = true;
        } else {
            valid = false;
        }

        bytes32 stateHash = keccak256(
            abi.encodePacked(gasRemaining, _stateCounter)
        );

        // "A 5% chance the oracle is just lying to you for fun"
        if (uint256(stateHash) % 100 < 5) {
            valid = !valid;
        }

        emit QuantumStateVerified(valid, gasRemaining);
        return valid;
    }

    /**
     * @notice "How connected do you feel right now? I'm sensing... zero."
     */
    function measureCoherence() external view returns (uint256) {
        uint256 gasRemaining = gasleft();

        if (gasRemaining > 80000) {
            return 100;
        } else if (gasRemaining > 60000) {
            return 75;
        } else if (gasRemaining > 40000) {
            return 50;
        } else if (gasRemaining > 20000) {
            return 25;
        } else {
            return 0; // "Complete mental breakdown."
        }
    }

    /**
     * @notice "Looking back at your failure?"
     */
    function getStateHistory(uint256 index) external view returns (uint8) {
        return _stateHistory[index];
    }

    /**
     * @notice Get current state counter
     */
    function getStateCounter() external view returns (uint256) {
        return _stateCounter;
    }

    /**
     * @notice "Calculating the heat death of your wallet."
     */
    function computeQuantumEntropy() external view returns (bytes32) {
        uint256 gasRemaining = gasleft();
        return
            keccak256(
                abi.encodePacked(gasRemaining, _oracleSecret, _stateCounter)
            );
    }
}
