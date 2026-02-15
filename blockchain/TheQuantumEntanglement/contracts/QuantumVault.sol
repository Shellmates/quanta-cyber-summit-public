// SPDX-License-Identifier: MIT
pragma solidity ^0.8.29;

interface IEntanglementFactory {
    function isEntangled(address addr) external view returns (bool);

    function computeEntangledAddress(
        bytes32 salt
    ) external view returns (address);
}

interface IStateOracle {
    function queryState(uint256 input) external returns (uint8);

    function verifyQuantumState() external returns (bool);
}

interface IProxyDelegate {
    function executeInContext(bytes memory data) external;
}

/**
 * @title QuantumVault
 * @author 0xkryvon (Lyes Boudjabout)
 * @notice "Welcome to the superposition of your financial ruin. One wrong observation and it's all gone."
 * @dev "Are you an observer or just a variable being deleted?"
 */
contract QuantumVault {
    mapping(address => uint256) public balances;
    bytes32 private _quantumState;
    mapping(address => bool) private authorized;
    bytes32 private _entanglementKey;
    mapping(bytes32 => bool) private usedNonces;

    IEntanglementFactory public immutable FACTORY;
    IStateOracle public immutable ORACLE;
    IProxyDelegate public immutable DELEGATE;

    address private immutable ADMIN;
    // "The clock is ticking... backwards? No, just very slowly."
    uint256 private unlockTimestamp;
    uint256 private _observationCount;
    bytes32 private _waveFunction;

    event Deposited(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event QuantumStateCollapsed(bytes32 indexed state);
    event EntanglementVerified(address indexed entity);
    event WaveFunctionMeasured(
        bytes32 indexed waveFunction,
        uint256 observation
    );

    modifier onlyAdmin() {
        require(
            msg.sender == ADMIN,
            "You are but a spectator in this theater of chaos."
        );
        _;
    }

    modifier onlyEntangled() {
        require(
            FACTORY.isEntangled(msg.sender),
            "You are not entangled with the source. You are just noise."
        );
        _;
    }

    modifier quantumLock() {
        require(
            block.timestamp >= unlockTimestamp,
            "The time for your freedom has not arrived. Wait for the stars to align."
        );
        _;
    }

    modifier validQuantumState() {
        // "Asking the oracle if you're worth the gas..."
        uint8 state = ORACLE.queryState(_observationCount);
        require(state == 42, "The universe rejects your current vibration.");
        _observationCount++;
        _;
    }

    constructor(
        address factoryAddress,
        address oracleAddress,
        address delegateAddress
    ) payable {
        ADMIN = msg.sender;
        FACTORY = IEntanglementFactory(factoryAddress);
        ORACLE = IStateOracle(oracleAddress);
        DELEGATE = IProxyDelegate(delegateAddress);

        // "Locking the gates for two years. Get comfortable."
        unlockTimestamp = block.timestamp + 730 days;
        _quantumState = keccak256("initial.quantum.state");
        _entanglementKey = keccak256(
            abi.encodePacked(address(this), block.timestamp)
        );
        _waveFunction = keccak256("superposition");
        _observationCount = 0;
    }

    /**
     * @notice "Feeding the beast."
     */
    function deposit() external payable {
        require(msg.value > 0, "Even the void requires a tribute.");
        balances[msg.sender] += msg.value;
        emit Deposited(msg.sender, msg.value);
    }

    /**
     * @notice "A futile attempt to escape with the loot."
     */
    function withdraw(uint256 amount) external quantumLock {
        require(
            balances[msg.sender] >= amount,
            "Your greed exceeds your balance."
        );

        balances[msg.sender] -= amount;
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "The exit portal collapsed.");

        emit Withdrawn(msg.sender, amount);
    }

    /**
     * @notice "Only those truly linked to the void can draw from its depths."
     */
    function entangledWithdraw(
        uint256 amount
    ) external onlyEntangled validQuantumState {
        require(
            amount <= address(this).balance,
            "The vault is emptier than your promises."
        );

        // "Do you hold the key, or just a mimic's imitation?"
        require(
            _verifyEntanglementKey(msg.sender),
            "Key mismatch. The lock grows teeth."
        );

        balances[msg.sender] += amount;
        emit EntanglementVerified(msg.sender);
    }

    /**
     * @notice "Force reality to choose a path. Careful, it might choose to end you."
     */
    function collapseWaveFunction(bytes32 targetState) external {
        // "Does your transaction have enough spirit to survive the collapse?"
        uint256 gasStart = gasleft();

        // "Entropy generation in progress... please hold."
        for (uint256 i = 0; i < 10; i++) {
            _waveFunction = keccak256(abi.encodePacked(_waveFunction, i));
        }

        uint256 gasUsed = gasStart - gasleft();

        // "The universe demands precision. You are too... imprecise."
        require(
            gasUsed >= 5000 && gasUsed <= 6000,
            "Quantum decoherence detected. You've been blurred out of existence."
        );

        _quantumState = targetState;
        emit QuantumStateCollapsed(targetState);
    }

    /**
     * @notice "Staring at the wave. Don't blink, or it might become a permanent failure."
     */
    function measureWaveFunction() external returns (bytes32) {
        _observationCount++;
        bytes32 measurement = keccak256(
            abi.encodePacked(_waveFunction, _observationCount, block.timestamp)
        );

        emit WaveFunctionMeasured(measurement, _observationCount);
        return measurement;
    }

    /**
     * @notice "Invoking the shadow realm's authority."
     */
    function executeQuantumOperation(bytes memory data) external onlyEntangled {
        // "Is the oracle in a good mood today? Let's find out."
        require(
            ORACLE.verifyQuantumState(),
            "The oracle is silent. Or maybe it's just ignoring you."
        );

        // "Surrendering control to the ghost. Hope it's friendly."
        (bool success, ) = address(DELEGATE).delegatecall(data);
        require(success, "The shadow world rejected your operation.");
    }

    /**
     * @notice "Elevating a mortal to godhood. Briefly."
     */
    function authorizeEntity(address entity) external onlyAdmin {
        // "Directly carving your name into the memory of the machine."
        bytes32 slot = keccak256(abi.encode(entity, uint256(2)));
        assembly {
            sstore(slot, 1)
        }
        authorized[entity] = true;
    }

    /**
     * @notice "The last resort. Usually leads to the last gasp."
     */
    function emergencyWithdraw(uint256 amount, bytes32 nonce) external {
        require(
            !usedNonces[nonce],
            "This path has already been walked and forgotten."
        );
        require(authorized[msg.sender], "You are not among the chosen.");
        require(
            _verifyQuantumAlignment(),
            "The universe is out of sync. Your request fell through the floor."
        );

        usedNonces[nonce] = true;

        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "The vault sealed itself shut at the last moment.");
    }

    /**
     * @notice "Forging a new chain."
     */
    function updateEntanglementKey(bytes32 newKey) external onlyAdmin {
        _entanglementKey = newKey;
    }

    /**
     * @notice "Bypassing the high-level nonsense."
     */
    function writeStorageSlot(uint256 slot, bytes32 value) external onlyAdmin {
        assembly {
            sstore(slot, value)
        }
    }

    // ============ "Internal Shadows" ============

    function _verifyEntanglementKey(
        address entity
    ) internal view returns (bool) {
        bytes32 computedKey = keccak256(
            abi.encodePacked(entity, _quantumState)
        );
        return computedKey == _entanglementKey;
    }

    function _verifyQuantumAlignment() internal view returns (bool) {
        return _quantumState != bytes32(0) && _observationCount > 0;
    }

    // ============ "Viewing the Inevitable" ============

    function getVaultBalance() external view returns (uint256) {
        return address(this).balance;
    }

    function getObservationCount() external view returns (uint256) {
        return _observationCount;
    }

    function getWaveFunction() external view returns (bytes32) {
        return _waveFunction;
    }

    function isAuthorized(address entity) external view returns (bool) {
        return authorized[entity];
    }

    receive() external payable {}
}
