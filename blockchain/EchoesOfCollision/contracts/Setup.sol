// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {EchoesOfCollision} from "./EchoesOfCollision.sol";

contract Setup {
    EchoesOfCollision public immutable TARGET;
    address public immutable PLAYER;

    constructor(address playerAddress) payable {
        require(
            msg.value >= 10 ether,
            "Setup needs at least 10 ether to fund the vault"
        );
        // Player starts with 1 ether in balance
        PLAYER = playerAddress;
        TARGET = new EchoesOfCollision{value: 10 ether}(uint256(block.timestamp));
        TARGET.sealVault();
    }

    function isSolved() public view returns (bool) {
        return address(TARGET).balance == 0;
    }
}
