// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract eVault {
    struct Record {
        uint id;
        string hash;
        string title;
        address owner;
    }

    mapping(uint => Record) public records;
    uint public recordCount;

    event RecordCreated(
        uint id,
        string hash,
        string title,
        address owner
    );

    function createRecord(string memory _hash, string memory _title) public {
        recordCount++;
        records[recordCount] = Record(recordCount, _hash, _title, msg.sender);
        emit RecordCreated(recordCount, _hash, _title, msg.sender);
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
}
