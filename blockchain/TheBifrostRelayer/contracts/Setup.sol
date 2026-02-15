// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./BifrostSingularity.sol";
import "./BifrostRelayer.sol";
import "./BifrostVault.sol";

contract Setup {
    BifrostSingularity public singularity;
    BifrostRelayer public relayer;
    BifrostVault public vault;
    address public immutable PLAYER;

    // Singularity Node: 0x67Dc...0960
    address public singularityNode = 0x67Dc4e080711AEA6Cf6Ee22D2B3553D5517d0960;

    constructor(address playerAddress) payable {
        require(msg.value == 10 ether, "Bridge core ignition requires 10 ETH");
        PLAYER = playerAddress;
        singularity = new BifrostSingularity(singularityNode, 10);
        relayer = new BifrostRelayer(address(singularity));
        vault = new BifrostVault{value: 10 ether}(address(relayer));
        relayer.setVault(address(vault));
    }

    function isSolved() external view returns (bool) {
        return address(vault).balance == 0;
    }
}
