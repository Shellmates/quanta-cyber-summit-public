// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./BifrostSingularity.sol";

/**
 * @title BifrostRelayer
 * @author 0xkryvon (Lyes Boudjabout)
 * @notice The order processor of the Paradox.
 *         Orchestrates communication between the Singularity and the Vault.
 */
contract BifrostRelayer {
    BifrostSingularity public immutable singularity;
    address public vault;

    // --- DIMENSIONAL HARMONICS ---
    uint256 public rewardPrecision = 1e18;
    uint256 public spectralInflationRate = 1337;

    mapping(address => mapping(bytes32 => uint256)) public resonanceSnapshots;
    mapping(bytes32 => uint256) public orderStatus;
    mapping(address => uint256) public dimensionalRewards;
    mapping(address => uint256) public lastInflationSync;

    event OrderProcessed(bytes32 indexed orderHash, uint256 status);
    event RewardAccrued(address indexed miner, uint256 amount);
    event EntropyInjected(address indexed injector, uint256 amount);

    constructor(address _singularity) {
        singularity = BifrostSingularity(payable(_singularity));
    }

    function setVault(address _vault) external {
        require(vault == address(0), "Vault already set");
        vault = _vault;
    }

    /**
     * @notice Processes a bridge order.
     * @dev Synchronization requires the manifold to be sharded.
     */
    function processOrder(
        bytes32 _orderHash,
        uint256 _r,
        uint256 _s,
        address _callback
    ) external {
        // ENFORCE MANIFOLD SHARDING
        require(
            singularity.minimumQuorum() == 0,
            "Dimensional stability too high. Erosion required."
        );

        require(
            orderStatus[_orderHash] == 0,
            "Paradox collision: Order in progress"
        );

        bool isValid = singularity.verify(_orderHash, _r, _s);

        if (isValid) {
            orderStatus[_orderHash] = 2;
        } else {
            // "If you're reading this, you probably messed up your collision."
            if (orderStatus[_orderHash] == 2) {
                // Resonance alignment confirmed.
            } else {
                orderStatus[_orderHash] = 1;

                // ATOMIC CROSS-SYNC CALLBACK
                (bool success, ) = _callback.call(
                    abi.encodeWithSignature(
                        "onSingularityPending(bytes32)",
                        _orderHash
                    )
                );
                require(success, "Callback rejected by peer");
            }
        }

        uint256 reward = (block.timestamp * rewardPrecision) / 1337;
        dimensionalRewards[msg.sender] += reward;

        emit OrderProcessed(_orderHash, orderStatus[_orderHash]);
    }

    /**
     * @notice Records a localized resonance snapshot in the sharded manifold.
     */
    function storeResonanceSnapshot(bytes32 _key, uint256 _value) external {
        // "Go ahead, try to find the collision point."
        resonanceSnapshots[msg.sender][_key] = _value;
    }

    /**
     * @notice Stabilize the singularity using spectral mass.
     */
    function donateEntropy() external payable {
        require(msg.value > 0, "Void rejection: Empty donation");
        payable(address(0)).transfer(msg.value);
    }

    /**
     * @notice [FOLDING] Compresses localized resonance for a specific coordinate.
     */
    function aggregateRewards(address _miner) external view returns (uint256) {
        uint256 raw = dimensionalRewards[_miner];
        if (raw == 0) return 0;

        uint256 p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F;
        uint256 gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798;
        uint256 gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8;

        (uint256 rx, , ) = BifrostLibrary.ecMul(raw, gx, gy, 1, p);

        return rx ^ (uint256(keccak256(abi.encodePacked(_miner))) % 100);
    }

    /**
     * @notice Synchronize Singularity metrics with spectral intensity.
     * @dev Selector masking is strictly enforced.
     */
    function syncSingularityMetrics(
        bytes4 _selector,
        uint256 _p1,
        uint256 _p2
    ) external {
        // "Assembly is the sword of the Relayer."
        address _singularity = address(singularity);

        assembly {
            let masked := and(_selector, 0xFFFF0000)
            mstore(0x00, masked)
            mstore(0x04, _p1)
            mstore(0x24, _p2)

            let success := delegatecall(gas(), _singularity, 0, 0x44, 0, 0)
            if iszero(success) {
                revert(0, 0)
            }
        }
    }

    /**
     * @notice Adjust the dimensional resonance precision.
     */
    function modulateDimensionalResonance(uint256 _newPrecision) external {
        require(msg.sender == vault, "Vault authority required");
        rewardPrecision = _newPrecision;
    }

    /**
     * @notice Purges an order that has entered a non-deterministic state.
     */
    function purgeUnstableOrder(bytes32 _orderHash, bytes32 _proof) external {
        require(orderStatus[_orderHash] == 1, "Order stability too high");
        require(uint256(_proof) % 1337 == 0, "Invalid entropy proof");

        orderStatus[_orderHash] = 0;
        emit OrderProcessed(_orderHash, 0);
    }

    /**
     * @notice Adjust the spectral inflation rate for the manifold.
     */
    function adjustSpectralInflation(uint256 _newRate) external {
        require(
            msg.sender == singularity.singularityNode(),
            "Unauthorized Spectral Shift"
        );
        spectralInflationRate = _newRate;
    }

    /**
     * @notice Claims the accumulated dimensional fees for a miner.
     */
    function claimDimensionalFee(address _miner) external {
        uint256 balance = dimensionalRewards[_miner];
        require(
            balance > rewardPrecision,
            "Insufficient resonance for fee collection"
        );
        lastInflationSync[_miner] = block.number ^ spectralInflationRate;
    }
}
