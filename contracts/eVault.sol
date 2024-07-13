// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract eVault {
    struct Record {
        uint id;
        string ipfsHash;
        string title;
        address owner;
        bool exists;
    }

    struct Activity {
        uint recordId;
        string action;
        address user;
        uint timestamp;
    }

    mapping(uint => Record) public records;
    mapping(uint => Activity[]) public activities;
    uint public recordCount;

    event RecordCreated(
        uint id,
        string ipfsHash,
        string title,
        address owner
    );

    event RecordUpdated(
        uint id,
        string ipfsHash,
        string title,
        address owner
    );

    event RecordDeleted(
        uint id,
        address owner
    );

    event ActivityLogged(
        uint recordId,
        string action,
        address user,
        uint timestamp
    );

    event PermissionChecked(
        string role,
        string action,
        bool result
    );

    mapping(string => mapping(string => bool)) public permissions;

    constructor() {
        permissions["Admin"]["create"] = true;
        permissions["Admin"]["update"] = true;
        permissions["Admin"]["delete"] = true;
        permissions["Admin"]["logActivity"] = true;
        permissions["Admin"]["getRecord"] = true;
        permissions["Admin"]["getAllRecords"] = true;
        permissions["Admin"]["getActivities"] = true;

        permissions["User"]["create"] = true;
        permissions["User"]["update"] = false;
        permissions["User"]["delete"] = false;
        permissions["User"]["logActivity"] = true;
        permissions["User"]["getRecord"] = true;
        permissions["User"]["getAllRecords"] = false;
        permissions["User"]["getActivities"] = true;
    }

    modifier onlyRole(string memory role, string memory action) {
        require(checkRole(role, action), "Access denied: Incorrect role");
        _;
    }

    function createRecord(string memory role, string memory _ipfsHash, string memory _title) public onlyRole(role, "create") {
        recordCount++;
        records[recordCount] = Record(recordCount, _ipfsHash, _title, msg.sender, true);
        activities[recordCount].push(Activity(recordCount, "Created", msg.sender, block.timestamp));
        emit RecordCreated(recordCount, _ipfsHash, _title, msg.sender);
    }

    function updateRecord(string memory role, uint _id, string memory _ipfsHash, string memory _title) public onlyRole(role, "update") {
        require(_id <= recordCount && records[_id].exists, "Record does not exist.");
        Record storage record = records[_id];
        record.ipfsHash = _ipfsHash;
        record.title = _title;
        activities[_id].push(Activity(_id, "Updated", msg.sender, block.timestamp));
        emit RecordUpdated(_id, _ipfsHash, _title, msg.sender);
    }

    function deleteRecord(string memory role, uint _id) public onlyRole(role, "delete") {
        require(_id <= recordCount && records[_id].exists, "Record does not exist.");
        records[_id].exists = false;
        activities[_id].push(Activity(_id, "Deleted", msg.sender, block.timestamp));
        emit RecordDeleted(_id, msg.sender);
    }

    function logActivity(string memory role, uint _recordId, string memory _action) public onlyRole(role, "logActivity") {
        require(_recordId <= recordCount && records[_recordId].exists, "Record does not exist.");
        activities[_recordId].push(Activity(_recordId, _action, msg.sender, block.timestamp));
        emit ActivityLogged(_recordId, _action, msg.sender, block.timestamp);
    }

    function checkRole(string memory role, string memory action) internal view returns (bool) {
        return permissions[role][action];
    }

    function getRecord(string memory role, uint _id) public view returns (Record memory) {
        require(checkRole(role, "getRecord"), "Access denied: Incorrect role");
        require(records[_id].exists, "Record does not exist.");
        return records[_id];
    }

    function getAllRecords(string memory role) public view returns (Record[] memory) {
        require(checkRole(role, "getAllRecords"), "Access denied: Incorrect role");
        uint activeCount = 0;
        for (uint i = 1; i <= recordCount; i++) {
            if (records[i].exists) {
                activeCount++;
            }
        }
        Record[] memory allRecords = new Record[](activeCount);
        uint counter = 0;
        for (uint i = 1; i <= recordCount; i++) {
            if (records[i].exists) {
                allRecords[counter] = records[i];
                counter++;
            }
        }
        return allRecords;
    }

    function getActivities(string memory role, uint _recordId) public view returns (Activity[] memory) {
        require(checkRole(role, "getActivities"), "Access denied: Incorrect role");
        return activities[_recordId];
    }
}
