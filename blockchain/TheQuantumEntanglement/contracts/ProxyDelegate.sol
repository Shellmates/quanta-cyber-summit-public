// SPDX-License-Identifier: MIT
pragma solidity ^0.8.29;

/**
 * @title ProxyDelegate
 * @author 0xkryvon (Lyes Boudjabout)
 * @notice "I am the ghost in the machine. I execute your desires, but I am not your servant."
 */
contract ProxyDelegate {
    // "The boss. Not you."
    address private immutable ADMIN;
    mapping(address => uint256) private _addressToTimestamp;
    bytes32 private _proxySecretState;
    uint256 private _executionNonce;
    bytes32 private _contextHash;
    address private immutable EXPECTED_VAULT;

    event OperationProcessed(bytes32 indexed opHash, uint256 timestamp);
    event StorageModified(uint256 indexed slot, bytes32 value);
    event ContextExecuted(address indexed caller, bytes32 contextId);

    modifier onlyAdmin() {
        require(msg.sender == ADMIN, "You are not the chosen one.");
        _;
    }

    constructor(address vaultAddress) {
        ADMIN = msg.sender;
        EXPECTED_VAULT = vaultAddress;
        _proxySecretState = keccak256(
            abi.encodePacked(msg.sender, block.timestamp)
        );
    }

    /**
     * @notice "Step into the context. Hope you don't get lost in the recursion."
     */
    function executeInContext(bytes memory data) external {
        // "Checking if you're even allowed to speak to me."
        require(_isValidContext(), "Access denied to the astral plane.");

        _executionNonce++;
        _addressToTimestamp[msg.sender] = block.timestamp;
        bytes32 contextId = keccak256(
            abi.encodePacked(msg.sender, block.timestamp, _executionNonce)
        );
        _contextHash = contextId;
        emit ContextExecuted(msg.sender, contextId);

        (bytes32 opCode, bytes memory params) = abi.decode(
            data,
            (bytes32, bytes)
        );

        // "Processing your request... or maybe I'll just delete everything. Hard to say."
        if (opCode == keccak256("STORAGE_WRITE_OP")) {
            _executeWriteStorage(params);
        } else if (opCode == keccak256("MAPPING_MODIFY_OP")) {
            _executeModifyMapping(params);
        } else if (opCode == keccak256("BATCH_STORAGE_OP")) {
            _executeBatchWrite(params);
        } else if (opCode == keccak256("AUTH_GRANT_OP")) {
            _executeAuthorize(params);
        } else if (opCode == keccak256("SLOT_MANIPULATION_OP")) {
            _executeSlotManipulation(params);
        } else {
            revert("Your dialect is unknown to me.");
        }

        emit OperationProcessed(opCode, block.timestamp);
    }

    /**
     * @notice "Writing to the fabric of reality. Don't blink."
     */
    function _executeWriteStorage(bytes memory params) internal {
        (uint256 slot, bytes32 value, bytes32 verificationHash) = abi.decode(
            params,
            (uint256, bytes32, bytes32)
        );

        // "You must prove your worth... with a hash."
        require(
            verificationHash == keccak256(abi.encodePacked(slot, value)),
            "The sacrifice was insufficient."
        );

        assembly {
            sstore(slot, value)
        }

        emit StorageModified(slot, value);
    }

    /**
     * @notice "Navigating the labyrinth of mappings."
     */
    function _executeModifyMapping(bytes memory params) internal {
        (uint256 mappingSlot, address key, uint256 value, bool directSlot) = abi
            .decode(params, (uint256, address, uint256, bool));

        bytes32 slot;

        if (directSlot) {
            slot = bytes32(mappingSlot);
        } else {
            slot = keccak256(abi.encode(key, mappingSlot));
        }

        assembly {
            sstore(slot, value)
        }

        emit StorageModified(uint256(slot), bytes32(value));
    }

    /**
     * @notice "Mass destruction in progress."
     */
    function _executeBatchWrite(bytes memory params) internal {
        (
            uint256[] memory slots,
            bytes32[] memory values,
            bytes32 batchHash
        ) = abi.decode(params, (uint256[], bytes32[], bytes32));

        require(slots.length == values.length, "The dimensions do not align.");
        require(
            slots.length > 0 && slots.length <= 10,
            "Too much power for one human."
        );

        require(
            batchHash == keccak256(abi.encode(slots, values)),
            "The batch is corrupted."
        );

        for (uint256 i = 0; i < slots.length; i++) {
            assembly {
                sstore(
                    mload(add(add(slots, 0x20), mul(i, 0x20))),
                    mload(add(add(values, 0x20), mul(i, 0x20)))
                )
            }
            emit StorageModified(slots[i], values[i]);
        }
    }

    /**
     * @notice "Granting power to the unworthy."
     */
    function _executeAuthorize(bytes memory params) internal {
        (address entity, uint256 mappingSlot, bytes32 proof) = abi.decode(
            params,
            (address, uint256, bytes32)
        );

        // "Wait, you're trying to do WHAT?"
        require(mappingSlot == 2, "You're knocking on the wrong door.");
        require(
            proof ==
                keccak256(abi.encodePacked("AUTHORIZE", entity, mappingSlot)),
            "Your credentials are as fake as your optimism."
        );

        bytes32 slot = keccak256(abi.encode(entity, mappingSlot));

        assembly {
            sstore(slot, 1)
        }

        emit StorageModified(uint256(slot), bytes32(uint256(1)));
    }

    /**
     * @notice "Sliding through the slots like a cold wind."
     */
    function _executeSlotManipulation(bytes memory params) internal {
        (
            uint256 baseSlot,
            int256 offset,
            bytes32 value,
            bytes32 operationProof
        ) = abi.decode(params, (uint256, int256, bytes32, bytes32));

        uint256 targetSlot;
        if (offset >= 0) {
            targetSlot = baseSlot + uint256(offset);
        } else {
            targetSlot = baseSlot - uint256(-offset);
        }

        require(
            operationProof ==
                keccak256(abi.encodePacked(baseSlot, offset, value)),
            "The proof of your crimes is invalid."
        );

        assembly {
            sstore(targetSlot, value)
        }

        emit StorageModified(targetSlot, value);
    }

    /**
     * @notice "Are we home? Or are we in someone else's nightmare?"
     */
    function _isValidContext() internal view returns (bool) {
        return address(this) == EXPECTED_VAULT;
    }
}
