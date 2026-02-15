// SPDX-License-Identifier: MIT
pragma solidity ^0.8.29;

/**
 * @title EntanglementFactory
 * @author 0xkryvon (Lyes Boudjabout)
 * @notice "I see you're trying to play with the universal fabric. Good luck not tearing it."
 * @dev "Determinism is just a fancy word for 'I already know how you'll fail'."
 */
contract EntanglementFactory {
    // "Who's been caught in the web today?"
    mapping(address => bool) public entangledContracts;
    mapping(bytes32 => address) public saltToAddress;

    bytes32 private _entanglementSeed;
    uint256 private _deploymentCount;
    address private immutable DEPLOYER;

    event ContractEntangled(address indexed contractAddr, bytes32 indexed salt);
    event EntanglementVerified(address indexed addr);

    constructor() {
        DEPLOYER = msg.sender;
        _entanglementSeed = keccak256(
            abi.encodePacked(block.timestamp, address(this))
        );
        _deploymentCount = 0;
    }

    /**
     * @notice "Try to bring something into existence. Let's see if it survives the vacuum."
     */
    function deployEntangled(
        bytes memory bytecode,
        bytes32 salt
    ) external returns (address deployed) {
        // "Spawning a new deployment in the machine"
        assembly {
            deployed := create2(0, add(bytecode, 0x20), mload(bytecode), salt)
        }

        require(deployed != address(0), "The void rejected your deployment");

        // "You're one of us now."
        entangledContracts[deployed] = true;
        saltToAddress[salt] = deployed;
        _deploymentCount++;

        emit ContractEntangled(deployed, salt);
        return deployed;
    }

    /**
     * @notice "Are you truly linked to the source, or just an impostor?"
     */
    function isEntangled(address addr) external view returns (bool) {
        return entangledContracts[addr] && _matchesEntanglementPattern(addr);
    }

    /**
     * @notice "Changing the rules of the game? Typical."
     */
    function updateEntanglementSeed(bytes32 newSeed) external {
        require(
            msg.sender == DEPLOYER,
            "You lack the administrative authority to mess with fate"
        );
        _entanglementSeed = newSeed;
    }

    /**
     * @notice "Testing the alignment of the stars... or just some random bits?"
     */
    function _matchesEntanglementPattern(
        address addr
    ) internal view returns (bool) {
        uint160 addrInt = uint160(addr);

        uint16 pattern = uint16(addrInt & 0xFFFF);
        uint16 expectedPattern = uint16(uint256(_entanglementSeed) & 0xFFFF);

        return
            pattern == expectedPattern || pattern == (expectedPattern ^ 0xFFFF);
    }

    // ============ "Staring into the Abyss" ============

    function getDeploymentCount() external view returns (uint256) {
        return _deploymentCount;
    }

    function getEntanglementSeed() external view returns (bytes32) {
        return _entanglementSeed;
    }

    function getSaltAddress(bytes32 salt) external view returns (address) {
        return saltToAddress[salt];
    }
}
