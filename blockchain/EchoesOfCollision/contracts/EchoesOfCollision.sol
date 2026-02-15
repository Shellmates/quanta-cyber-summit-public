// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @author 0xkryvon (Lyes Boudjabout)
 * @title EchoesOfCollision
 * @dev The goal is to provide inputs that produce a hash collision between the two encoding methods.
 */
contract EchoesOfCollision {
    address private immutable owner;
    // Some sort of salt, not much to say about it
    bytes32 private immutable SECRET_SALT;
    // Nice try looking here, but the answer isn't in plaintext (actually it is)
    uint256 private constant SOME_LOCK =
        92739511971229606987284970047757192857524688370469295801467043901388099627689;
    // "You can always send me some ETH (real or fake)"
    address private immutable AUTHOR_ETHEREUM_ADDRESS = 0xCD0734182F7948cC0ab7d347377fEa2492eBFE68;
    // This is the prime defining the Curve25519 field (The math that isn't mathing)
    uint256 private constant PRIME = 57896044618658097711785492504343953926634992332820282019728792003956564819949;
    bool private vaultSealed;

    mapping(address => uint256) private lastAttemptTime;
    mapping(address => uint256) private attemptCount;
    mapping(address => uint) private fundersAddressToAmount;

    event VaultSealed(uint256 treasureAmount, uint256 timestamp);
    event UnlockAttempted(
        address indexed seeker,
        uint256 attemptNumber,
        bool success
    );
    event TreasureClaimed(address indexed winner, uint256 amount);
    event VaultFunded(address indexed funder, uint256 amount);

    constructor(uint256 secretSalt) payable {
        require(msg.value > 0, "A vault needs treasure!");
        owner = msg.sender;
        SECRET_SALT = keccak256(abi.encode(secretSalt));
    }

    /**
     * @notice Seal the vault forever - even the owner loses control
     * @dev Once sealed, the vault can only be opened by solving the riddle.
     *      Good luck, you'll need it.
     */
    function sealVault() external {
        require(msg.sender == owner, "Only owner can seal");
        require(
            !vaultSealed,
            "Already sealed for eternity. What part of 'eternity' don't you understand?"
        );

        vaultSealed = true;
        emit VaultSealed(address(this).balance, block.timestamp);
    }

    /**
     * @notice Fund the vault with ETH
     * @dev The vault needs treasure!
     */
    function fundVault() external payable {
        require(msg.value >= 1 ether, "A vault needs treasure!");
        fundersAddressToAmount[msg.sender] += msg.value;
        emit VaultFunded(msg.sender, msg.value);
    }

    // I'm not a big fan of withdraw functions, but I'll add one for you
    function withdrawFundedAmount() external {
        require(vaultSealed, "Vault must be sealed first");
        require(fundersAddressToAmount[msg.sender] > 0, "You haven't funded the vault");
        uint256 amount = fundersAddressToAmount[msg.sender];
        fundersAddressToAmount[msg.sender] = 0;
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Withdrawal failed");
    }

    // But you can't withdraw if you're not the owner (try to be)
    // Or if you haven't funded the vault (being the owner doesn't mean not to fund and just withdraw)
    function withdrawAll() external {
        require(msg.sender == owner, "Only owner can withdraw");
        require(vaultSealed, "Vault must be sealed first");
        require(fundersAddressToAmount[msg.sender] > 0, "You haven't funded the vault");
        (bool success, ) = msg.sender.call{value: address(this).balance}("");
        require(success, "Withdrawal failed");
    }

    /**
     * @notice Attempt to unlock the vault with three key fragments
     * @dev The riddle: No need to explain, the code is already doing it for you
     */
    function attemptUnlockV1(
        string memory fragment1,
        string memory fragment2,
        bytes memory fragment4,
        bytes memory fragment5
    ) external {
        require(vaultSealed, "Vault must be sealed first");
        require(
            block.timestamp > lastAttemptTime[msg.sender] + 1 minutes,
            "Wait 1 minute between attempts. Patience is a virtue you clearly lack."
        );
        require(
            attemptCount[msg.sender] <= 3,
            "Too many attempts for such an easy challenge. Are you even trying?"
        );

        lastAttemptTime[msg.sender] = block.timestamp;
        attemptCount[msg.sender]++;

        require(keccak256(bytes(fragment1)) == SECRET_SALT, "Wrong secret");
        require(fragment4.length == 13, "Fragment 4 must be 13 bytes");
        
        bytes32 encodedHash = keccak256(
            abi.encode(msg.sender, fragment1, fragment2)
        );
        bytes32 packedHash = keccak256(
            abi.encodePacked(fragment4, fragment5)
        );

        bool success = (encodedHash == packedHash);

        // So close, yet so far... or maybe just far?
        emit UnlockAttempted(msg.sender, attemptCount[msg.sender], success);

        if (success) {
            uint256 treasure = address(this).balance;
            emit TreasureClaimed(msg.sender, treasure);

            (bool sent, ) = msg.sender.call{value: treasure}("");
            require(sent, "Treasure transfer failed");
        }
    }

    /**
     * @notice Attempt to unlock the vault with one key secret
     * @dev Expert cryptographers will know what to do
     */
    function attemptUnlockV2(uint256 _secret) external {
        require(vaultSealed, "Vault must be sealed first");
        require(
            block.timestamp > lastAttemptTime[msg.sender] + 1 minutes,
            "Wait 1 minute between attempts. Patience is a virtue you clearly lack."
        );
        require(
            attemptCount[msg.sender] <= 3,
            "Too many attempts for such an easy challenge. Are you even trying?"
        );

        lastAttemptTime[msg.sender] = block.timestamp;
        attemptCount[msg.sender]++;

        // Looks like a simple proof-of-knowledge check.
        bool success = (mulmod(_secret, _secret, PRIME) == 2);
        
        emit UnlockAttempted(msg.sender, attemptCount[msg.sender], success);

        if (success) {
            uint256 treasure = address(this).balance;
            emit TreasureClaimed(msg.sender, treasure);

            (bool sent, ) = msg.sender.call{value: treasure}("");
            require(sent, "Treasure transfer failed");
        }
    }

    /**
     * @notice Attempt to unlock the vault with two key secrets (basically my public key)
     * @dev "Just prove you know the Public Key for my wallet address!"
     */
    function attemptUnlockV3(uint256 pubKeyX, uint256 pubKeyY) external {
        require(vaultSealed, "Vault must be sealed first");
        require(
            block.timestamp > lastAttemptTime[msg.sender] + 1 minutes,
            "Wait 1 minute between attempts. Patience is a virtue you clearly lack."
        );
        require(
            attemptCount[msg.sender] <= 3,
            "Too many attempts for such an easy challenge. Are you even trying?"
        );

        lastAttemptTime[msg.sender] = block.timestamp;
        attemptCount[msg.sender]++;

        bytes memory mockPublicKey = abi.encodePacked(pubKeyX, pubKeyY);
        bytes32 hash = keccak256(mockPublicKey);
        address derived = address(uint160(uint256(hash)));

        bool success = (derived == AUTHOR_ETHEREUM_ADDRESS);

        emit UnlockAttempted(msg.sender, attemptCount[msg.sender], success);

        if (success) {
            // Congrats, you can actually drain the vault
            // You can even drain mine in real life (joking you can't, you need the private key)
            uint256 treasure = address(this).balance;
            emit TreasureClaimed(msg.sender, treasure);

            (bool sent, ) = msg.sender.call{value: treasure}("");
            require(sent, "Treasure transfer failed");
        }
    }

    // Type in my username and trust me, it'll work
    function reduceAttemptsCount(string memory password) external {
        require(
            uint256(keccak256(bytes(password))) == SOME_LOCK,
            "You got this one wrong? Seriously? Try 'admin' or something cliche."
        );
        attemptCount[msg.sender] -= 1;
    }

    function getTreasure() external view returns (uint256) {
        // You can look, but you can't touch.
        return address(this).balance;
    }

    function getMyAttempts() external view returns (uint256) {
        // Keeping track of your failures anyway.
        return attemptCount[msg.sender];
    }

    function isSealed() external view returns (bool) {
        return vaultSealed;
    }
}
