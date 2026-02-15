// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// I don't think you need to read this (trust me)

import {ReentrancyGuard} from "./ReentrancyGuard.sol";

/**
 * @title OracleParadox
 * @author 0xkryvon (Lyes Boudjabout)
 * @notice An oracle is a bridge between the blockchain and the real world.
 *         But what happens when the bridge is a trap?
 */
contract OracleParadox is ReentrancyGuard {
    // The vault's funds
    uint256 public totalVaultBalance;

    // I won't let you play around the contract for a long time.
    // Choose your transactions wisely.
    uint256 public nonce;

    // Mapping to store user data.
    // If you can't read bitwise operations, might as well stop here.
    mapping(address => uint256) private packedUserData;
    mapping(address => bool) private isMaintainer;

    uint256 public constant MIN_HOLD_BLOCKS = 10;
    uint256 public constant MIN_BLOCKS_THRESHOLD = 2;
    uint256 public constant BONUS_RATE = 100;

    event Deposit(address indexed user, uint256 amount, uint256 blockNumber);
    event Withdrawal(address indexed user, uint256 principal, uint256 bonus);
    event RealityAltered(address indexed user, uint256 times);

    modifier onlyMaintainer() {
        require(isMaintainer[msg.sender], "Not a maintainer");
        _;
    }

    constructor() payable {
        totalVaultBalance = msg.value;
    }

    // ChatGPT will maybe tell you where the problem is.
    // But it won't tell you how to solve it.
    function deposit() external payable nonReentrant {
        // We only accept real value here. Keep your dust.
        require(msg.value > 0, "Cannot deposit 0");
        require(
            msg.value < type(uint128).max,
            "Deposit too large for packed storage"
        );

        require(
            packedUserData[msg.sender] == 0,
            "Existing deposit found. Withdraw first."
        );

        packedUserData[msg.sender] = _pack(block.number, msg.value);
        totalVaultBalance += msg.value;
        nonce++;

        emit Deposit(msg.sender, msg.value, block.number);
    }

    function withdraw(uint256 puzzle) external nonReentrant {
        // ReentrancyGuard is on. Go find a different vulnerability.
        uint256 packedData = packedUserData[msg.sender];
        require(packedData > 0, "No liquidity provided");

        (uint256 depositBlock, uint256 originalAmount) = _unpack(packedData);

        uint256 bonus = 0;
        uint256 blocksHeld = block.number - depositBlock;

        // If you want the bonus, you need to solve the puzzle
        // I ain't giving away free money here
        if ((puzzle >> 32) == 0xdeadbeef && blocksHeld > 0) {
            bonus = (originalAmount * MIN_BLOCKS_THRESHOLD * BONUS_RATE) / 10000;
        }

        // Standard solvency check.
        // We use safe math implicitly (Solidity 0.8+)
        // So don't even try overflow bugs.
        uint256 totalPayout = originalAmount + bonus;

        require(
            address(this).balance >= totalPayout,
            "Vault insolvent currently"
        );

        (bool success, ) = payable(msg.sender).call{value: totalPayout}("");
        require(success, "Withdrawal failed");

        delete packedUserData[msg.sender];
        totalVaultBalance -= originalAmount;
        nonce++;

        emit Withdrawal(msg.sender, originalAmount, bonus);
    }

    // "Maintainers are payed as much as they want, whenever they want. No questions asked."
    function emergencyWithdraw() external onlyMaintainer nonReentrant {
        (bool success, ) = msg.sender.call{value: address(this).balance}("");
        require(success, "Transfer failed");
    }

    /**
     * @notice A failsafe mechanism.
     * Use this if you think the contract state is corrupted.
     * (Spoiler: It's not, you just don't understand the logic).
     */
    function restoreTimeline(address _space, bytes calldata _darkMatter) external {
        nonce++;
        require(_space != address(0), "The space has a non-zero address");
        require(_darkMatter.length == 0xD5, "Dimension mismatch");
        require(_observeTimeline() > 1200 * 10 ** 15, "Timeline is stable");

        bytes20 observer;
        assembly {
            observer := calldataload(add(_darkMatter.offset, 0x44))
        }
        
        require(observer == bytes20(msg.sender), "Observer not entangled");

        (bool collapsed, bytes memory singularity) = _space.staticcall(_darkMatter);

        require(collapsed, "Universe rejected the simulation");
        require(singularity[0] == 0x00, "High entropy detected");

        // "As a reward, you are now a maintainer of the Oracle Paradox."
        isMaintainer[msg.sender] = true;
    }

    function getMyStake()
        external
        returns (uint256 depositBlock, uint256 amount)
    {
        nonce++;
        return _unpack(packedUserData[msg.sender]);
    }

    /**
     * @notice Checks the vault's health ratio.
     * @dev If this returns anything other than 1e18, you broke physics or math.
     *      Probably math.
     */
    function _observeTimeline() private returns (uint256) {
        nonce++;
        if (address(this).balance == 0) return 0;
        return (totalVaultBalance * 1e18) / address(this).balance;
    }

    // DANGER ZONE: Bitwise surgery (Have you ever seen a surgery with no mistakes?).
    // If you don't know what endianness EVM uses, turn back now.
    // These operations are totally safe and can't lead to undefined behavior... or can they ?
    function _pack(
        uint256 _block,
        uint256 _amount
    ) internal pure returns (uint256) {
        return (uint256(uint128(_block)) << 128) | uint256(uint128(_amount));
    }

    // If you use some kind of static analysis tool, it will really help you.
    // The compiler itself is considered a static analysis tool!
    function _unpack(
        uint256 _packed
    ) internal pure returns (uint256 _block, uint256 _amount) {
        _block = uint256(uint128(_packed >> 128));
        _amount = uint256(uint128(_packed));
    }

    receive() external payable {
        totalVaultBalance += msg.value;
    }
}
