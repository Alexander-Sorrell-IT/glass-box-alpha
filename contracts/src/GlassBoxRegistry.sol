// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import { IGlassBoxAgent } from "./IGlassBoxAgent.sol";

/// Registry where any team's agent implementing IGlassBoxAgent registers
/// itself to appear on the broadcast leaderboard.
contract GlassBoxRegistry {
    struct Registration {
        uint256 agentId;
        address agentContract;
        address registrant;
        uint256 registeredAt;
    }

    Registration[] public registrations;
    mapping(uint256 => uint256) public regIndexOf;

    event AgentRegistered(uint256 indexed agentId, address agentContract, address registrant);

    error AlreadyRegistered();
    error NotInterface();

    function register(uint256 agentId, address agentContract) external {
        if (regIndexOf[agentId] != 0) revert AlreadyRegistered();

        try IGlassBoxAgent(agentContract).agentId() returns (uint256 reportedId) {
            require(reportedId == agentId, "agentId mismatch");
        } catch {
            revert NotInterface();
        }

        registrations.push(Registration({
            agentId: agentId,
            agentContract: agentContract,
            registrant: msg.sender,
            registeredAt: block.timestamp
        }));
        regIndexOf[agentId] = registrations.length;

        emit AgentRegistered(agentId, agentContract, msg.sender);
    }

    function registrationsCount() external view returns (uint256) {
        return registrations.length;
    }

    function getRegistration(uint256 agentId) external view returns (Registration memory) {
        uint256 idx = regIndexOf[agentId];
        require(idx != 0, "not registered");
        return registrations[idx - 1];
    }
}
