// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract eVault {
    struct Record {
        uint id;
        string ipfsHash;
        string title;
        address owner;
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

    event ActivityLogged(
        uint recordId,
        string action,
        address user,
        uint timestamp
    );

    function createRecord(string memory _ipfsHash, string memory _title) public {
        recordCount++;
        records[recordCount] = Record(recordCount, _ipfsHash, _title, msg.sender);
        activities[recordCount].push(Activity(recordCount, "Created", msg.sender, block.timestamp));
        emit RecordCreated(recordCount, _ipfsHash, _title, msg.sender);
    }

    function updateRecord(uint _id, string memory _ipfsHash, string memory _title) public {
        require(_id <= recordCount, "Record does not exist.");
        Record storage record = records[_id];
        record.ipfsHash = _ipfsHash;
        record.title = _title;
        activities[_id].push(Activity(_id, "Updated", msg.sender, block.timestamp));
        emit RecordUpdated(_id, _ipfsHash, _title, msg.sender);
    }

    function logActivity(uint _recordId, string memory _action) public {
        require(_recordId <= recordCount, "Record does not exist.");
        activities[_recordId].push(Activity(_recordId, _action, msg.sender, block.timestamp));
        emit ActivityLogged(_recordId, _action, msg.sender, block.timestamp);
    }

    function getRecord(uint _id) public view returns (Record memory) {
        return records[_id];
    }

    function getAllRecords() public view returns (Record[] memory) {
        Record[] memory allRecords = new Record[](recordCount);
        for (uint i = 1; i <= recordCount; i++) {
            allRecords[i - 1] = records[i];
        }
        return allRecords;
    }

    function getActivities(uint _recordId) public view returns (Activity[] memory) {
        return activities[_recordId];
    }
}