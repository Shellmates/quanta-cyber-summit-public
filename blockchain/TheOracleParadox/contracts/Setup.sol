// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {OracleParadox} from "./OracleParadox.sol";

contract Setup {
    OracleParadox public immutable TARGET;
    address public immutable PLAYER;

    constructor(address playerAddress) payable {
        // The player starts with 23 ETH in balance
        PLAYER = playerAddress;
        // Deploy the vault with 100 ETH to make it spicy
        require(msg.value >= 100 ether, "Setup needs at least 100 ether");
        TARGET = new OracleParadox{value: 100 ether}();
    }

    /**
     * @notice Check if the challenge is solved
     * @return true if the vault has been drained
     */
    function isSolved() public view returns (bool) {
        return address(TARGET).balance == 0 && TARGET.nonce() <= 4;
    }
}
