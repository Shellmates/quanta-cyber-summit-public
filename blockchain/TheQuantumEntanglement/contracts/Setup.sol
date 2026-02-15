// SPDX-License-Identifier: MIT
pragma solidity ^0.8.29;

import {QuantumVault} from "./QuantumVault.sol";
import {EntanglementFactory} from "./EntanglementFactory.sol";
import {StateOracle} from "./StateOracle.sol";
import {ProxyDelegate} from "./ProxyDelegate.sol";

contract Setup {
    QuantumVault public immutable TARGET;
    EntanglementFactory public immutable FACTORY;
    StateOracle public immutable ORACLE;
    ProxyDelegate public immutable DELEGATE;
    address public immutable PLAYER;

    constructor(address playerAddress) payable {
        PLAYER = playerAddress;

        FACTORY = new EntanglementFactory();
        ORACLE = new StateOracle();

        // Why doing all of this?
        // Ask your AI, maybe he got some answers for you.
        // Or maybe he's just as confused as you are.
        address predictedVaultAddress = address(
            uint160(
                uint256(
                    keccak256(
                        abi.encodePacked(
                            bytes1(0xd6),
                            bytes1(0x94),
                            address(this),
                            uint8(4)
                        )
                    )
                )
            )
        );

        DELEGATE = new ProxyDelegate(predictedVaultAddress);
        TARGET = new QuantumVault{value: 20 ether}(
            address(FACTORY),
            address(ORACLE),
            address(DELEGATE)
        );

        require(
            address(TARGET) == predictedVaultAddress,
            "Vault address prediction failed"
        );
    }

    function isSolved() public view returns (bool) {
        return TARGET.getVaultBalance() == 0;
    }
}
