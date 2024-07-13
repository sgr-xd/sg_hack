// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DocumentVault {
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

    Record[] private records;
    Activity[] private activities;
    mapping(uint => uint) private recordIdToIndex;
    mapping(uint => uint[]) private recordIdToActivityIds;
    uint private nextRecordId = 1;

    event RecordCreated(uint id, string ipfsHash, string title, address owner);
    event RecordUpdated(uint id, string ipfsHash, string title, address owner);
    event ActivityLogged(uint recordId, string action, address user, uint timestamp);

    function createRecord(string memory ipfsHash, string memory title) public {
        uint recordId = nextRecordId;
        records.push(Record(recordId, ipfsHash, title, msg.sender));
        recordIdToIndex[recordId] = records.length - 1;
        nextRecordId++;
        
        emit RecordCreated(recordId, ipfsHash, title, msg.sender);
    }

    function updateRecord(uint recordId, string memory ipfsHash, string memory title) public {
        require(records[recordIdToIndex[recordId]].owner == msg.sender, "Only the owner can update the record");

        records[recordIdToIndex[recordId]].ipfsHash = ipfsHash;
        records[recordIdToIndex[recordId]].title = title;

        emit RecordUpdated(recordId, ipfsHash, title, msg.sender);
    }

    function logActivity(uint recordId, string memory action) public {
        require(records[recordIdToIndex[recordId]].owner == msg.sender, "Only the owner can log activity");

        activities.push(Activity(recordId, action, msg.sender, block.timestamp));
        recordIdToActivityIds[recordId].push(activities.length - 1);

        emit ActivityLogged(recordId, action, msg.sender, block.timestamp);
    }

    function getRecord(uint recordId) public view returns (uint, string memory, string memory, address) {
        Record memory record = records[recordIdToIndex[recordId]];
        return (record.id, record.ipfsHash, record.title, record.owner);
    }

    function getAllRecords() public view returns (Record[] memory) {
        return records;
    }

    function getActivities(uint recordId) public view returns (Activity[] memory) {
        uint[] memory activityIds = recordIdToActivityIds[recordId];
        Activity[] memory result = new Activity[](activityIds.length);

        for (uint i = 0; i < activityIds.length; i++) {
            result[i] = activities[activityIds[i]];
        }

        return result;
    }
}
