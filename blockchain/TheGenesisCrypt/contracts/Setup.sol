// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {GenesisCrypt} from "./GenesisCrypt.sol";

contract Setup {
    GenesisCrypt public immutable TARGET;
    address public immutable player;

    constructor(address playerAddress) payable {
        require(msg.value >= 10 ether, "Send at least 10 ETH");
        player = playerAddress;
        TARGET = new GenesisCrypt();
        (bool success, ) = address(TARGET).call{value: msg.value}("");
        require(success, "Transfer failed");
    }

    /**
     * @notice Check if the challenge is solved
     * @return true if the vault has been drained
     */
    function isSolved() public view returns (bool) {
        return address(TARGET).balance == 0 && player.balance >= 10 ether;
    }
}
