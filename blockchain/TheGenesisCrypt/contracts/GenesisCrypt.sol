// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Oh, look who it is. Another "hacker"
// reading the source code because they
// can't reverse engineer, Cute.

/**
 * @author 0xkryvon (Lyes Boudjabout)
 * @title The Genesis Crypt
 * @notice A vault that should be secure... but is it?
 * @dev The key demonstrates a critical solidity 0.5.x breaking change
 */
contract GenesisCrypt {
    event Deposit(address indexed depositor, uint256 amount);
    event Withdraw(address indexed withdrawer, uint256 amount);

    struct Proposal {
        address proposer;
        uint256 timeOfSubmission;
        string content;
    }

    address private owner;
    bool private initialized;
    uint256 private numberOfProposals;

    mapping (uint256 => Proposal) public improvementProposals;

    // Every magic number is a ghost of a previous state.
    uint256 public constant MAGIC_NUMBER =
        90028716064323320151525972407266432128556371065131841289487431191071985929384;

    error WhyProposingNow(string proposal);
    
    constructor() {
        // It's empty. Are you confused? If not, you should be.
        // Keywords are just for people who can't keep their names consistent.
    }

    // You're probably going to copy-paste this into ChatGPT, right?
    // Trust me, doesn't have a clue of what's happening.
    function init(address _owner, string memory proof) external {
        require(!initialized, "Already initialized");
        // Can you find a collision in the keccak256 algorithm?
        // Even the world's most elite cryptographers wouldn't dare try to break this.
        // But you can continue staring, maybe the math will change if you blink enough.
        require(
            uint256(keccak256(bytes(proof))) == MAGIC_NUMBER,
            "Invalid proof"
        );
        owner = _owner;
        initialized = true;
    }

    // "You can always send me some ETH (real or fake)"
    function deposit() external payable {
        require(initialized, "Not initialized");
        require(msg.value > 0, "No ETH deposited");

        emit Deposit(msg.sender, msg.value);
    }

    function withdraw() external {
        // Can msg.sender be equal to zero?
        // If yes, you need to think about a way to make initialized true.
        // Therefore, don't even think about it.
        require(msg.sender == owner, "Not owner");
        require(initialized, "Not initialized");

        (bool success, ) = msg.sender.call{value: address(this).balance}("");
        require(success, "Transfer failed");

        emit Withdraw(msg.sender, address(this).balance);
    }

    // After initialization, you can send improvement proposals.
    // I'll take my time to review them, and maybe I'll implement them.
    // But for now, just send them.
    function sendImprovementProposals(string memory proposalContent) public {
        if (!initialized) {
            revert WhyProposingNow(proposalContent);
        }
        Proposal memory proposal = Proposal({
            proposer: msg.sender,
            timeOfSubmission: block.timestamp,
            content: proposalContent
        });
        improvementProposals[numberOfProposals] = proposal;
        numberOfProposals++;
    }

    // "Take a look at who's the owner (not you)"
    function getOwner() external view returns (address) {
        return owner;
    }

    // "I'm sure you're wondering if it's initialized"
    function getInitialized() external view returns (bool) {
        return initialized;
    }

    // "And how many proposals have been sent (accepted actually)"
    function getNumberOfProposals() external view returns (uint256) {
        return numberOfProposals;
    }

    // Thanks for the ETH, use a real wallet next time.
    receive() external payable {}
}
